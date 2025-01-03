import pygame
from dataclasses import dataclass
from config import COLORS
from icons import ICON_CREATORS
from sound_manager import SoundManager
from notification import Notification
from gameplay import Terminal
from missions import Mission, MissionType, Faction
from logger import setup_logger

@dataclass
class Icon:
    x: int
    y: int
    width: int = 64
    height: int = 64
    name: str = ""
    image: pygame.Surface = None
    active: bool = True

class Desktop:
    def __init__(self, screen_width, screen_height, save_manager):
        self.width = screen_width
        self.height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.logger = setup_logger()
        
        # Initialisation des attributs de base
        self.windows = []
        self.active_window = None
        self.taskbar = []
        self.notifications = []
        self.messages = []
        self.available_missions = []
        self.market_data = []  # Sera initialisé plus tard par MenuPrincipal
        self.player_data = {"hardware": {}, "credits": 0}
        self.save_manager = save_manager
        
        # Charger les données du joueur
        if isinstance(save_manager.player_data, dict):
            self.player_data = save_manager.player_data
        
        # Charger les messages
        from messages import SystemeMessage
        systeme_message = SystemeMessage()
        self.messages = systeme_message.obtenir_messages("ALL")
        
        # Initialisation sécurisée
        try:
            pygame.display.set_caption("CyberHack OS")
            self.sound_manager = SoundManager()
            self.font = pygame.font.Font(None, 24)
            self.taskbar_height = 40
            self.taskbar_button_width = 150
            self.init_icons()
        except Exception as e:
            self.logger.error(f"Erreur initialisation bureau: {e}")
            raise

    def create_default_icon(self, name):
        """Crée une icône par défaut avec la première lettre du nom"""
        surface = pygame.Surface((64, 64))
        surface.fill(COLORS["GREEN"])
        text = self.font.render(name[:1], True, COLORS["BLACK"])
        surface.blit(text, (25, 20))
        return surface

    def draw(self):
        # Fond d'écran - effacer tout l'écran
        self.screen.fill(COLORS["BLACK"])
        
        # Dessiner les icônes
        for name, icon in self.icons.items():
            if icon.active:
                self.screen.blit(icon.image, (icon.x, icon.y))
                text = self.font.render(name, True, COLORS["GREEN"])
                self.screen.blit(text, (icon.x, icon.y + icon.height + 5))
        
        # Dessiner la barre des tâches
        pygame.draw.rect(self.screen, COLORS["DARK_GRAY"], 
                        (0, self.height - self.taskbar_height, 
                         self.width, self.taskbar_height))
        
        # Dessiner uniquement les fenêtres actives
        for window in sorted(self.windows, key=lambda w: w == self.active_window):
            if window.active and not window.minimized:  # Vérifier si la fenêtre est active et non minimisée
                window.draw(self.screen)
        
        # Dessiner les boutons de la barre des tâches pour les fenêtres actives
        x = 5
        for window in self.windows:
            if window.active:  # Afficher un bouton même si la fenêtre est minimisée
                color = COLORS["GREEN"] if window == self.active_window else COLORS["DARK_GREEN"]
                pygame.draw.rect(self.screen, color,
                               (x, self.height - self.taskbar_height + 5,
                                self.taskbar_button_width, self.taskbar_height - 10))
                text = self.font.render(window.title[:15], True, COLORS["BLACK"])
                self.screen.blit(text, (x + 5, self.height - self.taskbar_height + 10))
                x += self.taskbar_button_width + 5
        
        # Dessiner les notifications actives
        self.notifications = [notif for notif in self.notifications if notif.draw(self.screen)]
        
        pygame.display.flip()

    def handle_click(self, pos):
        x, y = pos
        
        # Vérifier les clics sur la barre des tâches
        if y > self.height - self.taskbar_height:
            button_x = 5
            for window in self.windows:
                if window.active:
                    if button_x <= x <= button_x + self.taskbar_button_width:
                        self.active_window = window
                        return True
                    button_x += self.taskbar_button_width + 5
            return False
        
        # Vérifier les clics sur les fenêtres (de la plus active à la moins active)
        for window in reversed(self.windows):
            if window.active and window.handle_click(pos):
                self.active_window = window
                # Réorganiser les fenêtres pour que la fenêtre active soit au-dessus
                self.windows.remove(window)
                self.windows.append(window)
                return True
        
        # Vérifier les clics sur les icônes
        for name, icon in self.icons.items():
            if (icon.x <= x <= icon.x + icon.width and 
                icon.y <= y <= icon.y + icon.height):
                self.open_window(name)
                return True
        
        return False

    def minimize_window(self, window):
        """Minimise une fenêtre"""
        if window:
            window.minimized = True
            if window == self.active_window:
                self.active_window = None

    def restore_window(self, window):
        """Restaure une fenêtre minimisée"""
        if window:
            window.minimized = False
            self.active_window = window

    def close_window(self, window):
        """Ferme une fenêtre"""
        window.active = False
        if window == self.active_window:
            self.active_window = next((w for w in reversed(self.windows) 
                                     if w.active), None)

    def open_window(self, window_type):
        if window_type == "terminal":
            # Créer une instance de JeuMission d'abord
            from gameplay import Terminal, JeuMission
            from missions import Mission, MissionType
            
            # Créer une mission test si nécessaire
            test_mission = Mission(
                id="TEST_001",
                titre="Mission Test",
                description="Mission de test",
                type=MissionType.INFILTRATION,
                difficulte=1,
                recompense=1000,
                faction=Faction.SPECTRES,
                objectifs=["Infiltrer le système"]
            )
            
            # Créer l'instance de JeuMission
            jeu = JeuMission(test_mission, self.screen, self.save_manager)
            
            # Le terminal est déjà créé dans JeuMission
            term = jeu.terminal
            term.active = True
            self.windows.append(term)
            self.active_window = term
        elif window_type == "messages":
            from windows import MessageWindow
            msgs = MessageWindow(200, 100, 400, 500, self.messages)
            msgs.active = True
            self.windows.append(msgs)
            self.active_window = msgs
        elif window_type == "missions":
            from windows import MissionWindow
            missions = MissionWindow(200, 100, 500, 600, self.available_missions, self)
            missions.active = True
            self.windows.append(missions)
            self.active_window = missions
        elif window_type == "market":
            from windows import MarketWindow
            market = MarketWindow(200, 100, 400, 500, self.market_data)
            market.active = True
            self.windows.append(market)
            self.active_window = market
        elif window_type == "hardware":
            from windows import HardwareWindow
            hw = HardwareWindow(200, 100, 400, 500, self.player_data["hardware"], self.player_data["credits"])
            hw.active = True
            self.windows.append(hw)
            self.active_window = hw
        elif window_type == "stats":
            from windows import StatsWindow
            stats = StatsWindow(200, 100, 400, 500, self.player_data)
            stats.active = True
            self.windows.append(stats)
            self.active_window = stats
        # ... autres types de fenêtres 

    def handle_event(self, event):
        try:
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEWHEEL:
                if self.active_window:
                    return self.active_window.handle_mousewheel(event.y)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return self.handle_click(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                # Arrêter le déplacement des fenêtres
                for window in self.windows:
                    window.dragging = False
            elif event.type == pygame.MOUSEMOTION:
                # Gérer le déplacement des fenêtres
                for window in self.windows:
                    if window.dragging:
                        x, y = event.pos
                        offset_x, offset_y = window.drag_offset
                        window.x = x - offset_x
                        window.y = y - offset_y
                        # Empêcher la fenêtre de sortir de l'écran
                        window.x = max(0, min(window.x, self.width - window.width))
                        window.y = max(0, min(window.y, self.height - window.height))
            elif event.type == pygame.KEYDOWN:
                return self.handle_keypress(event)
                
            return True
        except Exception as e:
            self.logger.error(f"Erreur événement: {e}")
            return True  # Continue l'exécution malgré l'erreur

    def show_notification(self, message, type="info"):
        self.notifications.append(Notification(message, type))
        if type == "error":
            self.sound_manager.play("error")
        elif type == "success":
            self.sound_manager.play("success") 

    def init_icons(self):
        """Initialise les icônes du bureau"""
        self.icons = {
            "terminal": Icon(50, 50, name="Terminal"),
            "messages": Icon(50, 150, name="Messages"),
            "missions": Icon(50, 250, name="Missions"),
            "market": Icon(50, 350, name="Black Market"),
            "hardware": Icon(50, 450, name="Hardware"),
            "stats": Icon(50, 550, name="Stats")
        }
        
        # Charger les images des icônes
        for name, icon in self.icons.items():
            try:
                if name in ICON_CREATORS:
                    icon.image = ICON_CREATORS[name]()
                else:
                    raise KeyError(f"Créateur d'icône non trouvé pour {name}")
            except Exception as e:
                self.logger.error(f"Erreur chargement icône {name}: {str(e)}")
                icon.image = self.create_default_icon(name) 

    def handle_keypress(self, event):
        """Gère les événements clavier"""
        if self.active_window:
            if event.key == pygame.K_ESCAPE:
                self.minimize_window(self.active_window)
            elif event.key == pygame.K_F4 and (event.mod & pygame.KMOD_ALT):
                self.close_window(self.active_window)
            else:
                return self.active_window.handle_keypress(event)
        return True 

    def start_mission(self, mission):
        """Lance une nouvelle mission"""
        from gameplay import JeuMission
        
        # Fermer toutes les fenêtres actuelles
        self.windows.clear()
        self.active_window = None
        
        # Créer et lancer la mission
        try:
            mission_game = JeuMission(mission, self.screen, self.save_manager)
            self.show_notification(f"Mission démarrée: {mission.titre}", "info")
            
            # Boucle de jeu de la mission
            running = True
            clock = pygame.time.Clock()
            
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                
                # Mettre à jour et afficher la mission
                mission_game.afficher()
                pygame.display.flip()
                clock.tick(60)
            
            # Retour au bureau après la mission
            self.show_notification("Mission terminée", "success")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du lancement de la mission: {e}")
            self.show_notification("Erreur lors du lancement de la mission", "error") 

    def run(self):
        """Lance la boucle principale du bureau"""
        running = True
        clock = pygame.time.Clock()
        
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    else:
                        running = self.handle_event(event)
                
                self.draw()
                clock.tick(60)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur dans la boucle du bureau: {e}")
            return False 

    def handle_events(self):
        """Gère les événements du bureau"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Gestion du clic sur les icônes
                for icon in self.icons:
                    if icon.active and self.is_point_in_rect(event.pos, (icon.x, icon.y, icon.width, icon.height)):
                        self.handle_icon_click(icon)
                        break
                
                # Gestion du clic sur la barre des tâches
                if event.pos[1] > self.height - self.taskbar_height:
                    self.handle_taskbar_click(event.pos)
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.active_window:
                        self.close_window(self.active_window)
                    else:
                        return False
                        
                # Autres touches spéciales
                if event.key == pygame.K_F5:
                    self.refresh_desktop()
                    
        return True

    def handle_icon_click(self, icon):
        """Gère le clic sur une icône"""
        if icon.name == "Terminal":
            self.open_terminal()
        elif icon.name == "Missions":
            self.open_missions()
        elif icon.name == "Market":
            self.open_market()
        elif icon.name == "Stats":
            self.open_stats()
        elif icon.name == "Settings":
            self.open_settings()
        
    def handle_taskbar_click(self, pos):
        """Gère le clic sur la barre des tâches"""
        x = pos[0]
        button_width = self.taskbar_button_width
        
        for i, window in enumerate(self.windows):
            if x >= i * button_width and x < (i + 1) * button_width:
                if window == self.active_window:
                    self.minimize_window(window)
                else:
                    self.activate_window(window)
                break

    def is_point_in_rect(self, point, rect):
        """Vérifie si un point est dans un rectangle"""
        x, y = point
        rx, ry, rw, rh = rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    def refresh_desktop(self):
        """Rafraîchit le bureau"""
        self.update_market_data()
        self.update_messages()
        self.update_missions()
        self.show_notification("Bureau rafraîchi", "info") 