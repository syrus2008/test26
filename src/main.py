import pygame
import sys
import random
import time
from missions import Mission, MissionType, Faction
from mission_manager import MissionManager
from gameplay import JeuMission
from save_manager import SaveManager
from shop import Shop
from desktop import Desktop
from logger import setup_logger
from constants import GameState, TICK_RATE
from paths import ASSETS_DIR, SAVES_DIR
from exceptions import GameError
from messages import SystemeMessage

# Initialisation
pygame.init()
pygame.mixer.init()

# Configuration
LARGEUR = 1024
HAUTEUR = 768
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("CyberHack 2084")

# Couleurs
VERT_TERMINAL = (0, 255, 0)
VERT_FONCE = (0, 180, 0)
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)

# Polices
police_titre = pygame.font.Font(None, 72)
police_menu = pygame.font.Font(None, 36)
police_ascii = pygame.font.Font(None, 24)

# Initialiser le logger
logger = setup_logger()

class EffetGlitch:
    def __init__(self):
        self.derniere_mise_a_jour = time.time()
        self.lignes_glitch = []
        self.delai = 0.1
    
    def update(self):
        if time.time() - self.derniere_mise_a_jour > self.delai:
            self.lignes_glitch = [
                (random.randint(0, LARGEUR), random.randint(0, HAUTEUR), 
                 random.randint(50, 150)) for _ in range(5)
            ]
            self.derniere_mise_a_jour = time.time()
    
    def dessiner(self, surface):
        for x, y, longueur in self.lignes_glitch:
            pygame.draw.line(surface, VERT_TERMINAL, (x, y), (x + longueur, y), 1)

class MenuPrincipal:
    def __init__(self):
        self.base_options = [
            "INFILTRER LE SYSTÈME",
            "MISSIONS DISPONIBLES",
            "PROTOCOLES",
            "MAGASIN",
            "DÉCONNEXION"
        ]
        self.game_state = GameState.MENU
        self.missions_disponibles = []  # Initialisation par défaut
        self.logger = setup_logger()  # Initialiser le logger
        
        try:
            self.selection = 0
            self.effet_glitch = EffetGlitch()
            self.ascii_art = [
                "  ▄████▄▓██   ██▓ ▄▄▄▄   ▓█████  ██▀███   ██░ ██  ▄▄▄       ▄████▄   ██ ▄█▀",
                " ▒██▀ ▀█ ▒██  ██▒▓█████▄ ▓█   ▀ ▓██ ▒ ██▒▓██░ ██▒▒████▄    ▒██▀ ▀█   ██▄█▒ ",
                " ▒▓█    ▄ ▒██ ██░▒██▒ ▄██▒███   ▓██ ░▄█ ▒▒██▀▀██░▒██  ▀█▄  ▒▓█    ▄ ▓███▄░ ",
                " ▒▓▓▄ ▄██▒░ ▐██▓░▒██░█▀  ▒▓█  ▄ ▒██▀▀█▄  ░▓█ ░██ ░██▄▄▄▄██ ▒▓▓▄ ▄██▒▓██ █▄ ",
                " ▒ ▓███▀ ░░ ██▒▓░░▓█  ▀█▓░▒████▒░██▓ ▒██▒░▓█▒░██▓ ▓█   ▓██▒▒ ▓███▀ ░▒██▒ █▄",
                " ░ ░▒ ▒  ░ ██▒▒▒ ░▒▓███▀▒░░ ▒░ ░░ ▒▓ ░▒▓░ ▒ ░░▒░▒ ▒▒   ▓▒█░░ ░▒ ▒  ░▒ ▒▒ ▓▒"
            ]
            self.save_manager = SaveManager()
            self.systeme_message = SystemeMessage()
            self.gestionnaire_missions = MissionManager(self.save_manager)
            self.shop = Shop(self.save_manager)
            player_data_loaded = self.save_manager.load_player_data()
            
            if player_data_loaded:  # Si des données ont été chargées
                # Convertir la faction de string en enum de manière sécurisée
                faction_str = self.save_manager.player_data["faction"]
                try:
                    if isinstance(faction_str, str):
                        self.faction_actuelle = Faction(faction_str)
                    else:
                        self.faction_actuelle = faction_str
                except ValueError:
                    self.logger.error(f"Faction invalide: {faction_str}")
                    self.faction_actuelle = None
                self.niveau_joueur = self.save_manager.player_data["level"]
                self.missions_completees = self.save_manager.player_data["completed_missions"]
                self.ecran_actuel = "menu"
                self.missions_disponibles = self.gestionnaire_missions.obtenir_missions_disponibles(
                    self.faction_actuelle, 
                    self.niveau_joueur
                )
                self.player_data = self.save_manager.player_data
            else:
                self.ecran_actuel = "factions"
                self.niveau_joueur = 1
                self.missions_completees = []
                self.faction_actuelle = None
                self.player_data = {
                    "faction": None,
                    "level": 1,
                    "credits": 1000,
                    "completed_missions": [],
                    "tools": [],
                    "hardware": {
                        "cpu": {"level": 1, "bonus": 0.1},
                        "ram": {"level": 1, "bonus": 0.1},
                        "network": {"level": 1, "bonus": 0.1},
                        "cooling": {"level": 1, "bonus": 0.1}
                    },
                    "stats": {
                        "missions_completed": 0,
                        "total_earnings": 0,
                        "successful_hacks": 0,
                        "stealth_missions": 0,
                        "data_stolen_value": 0,
                        "largest_botnet": 0,
                        "total_ransom": 0
                    }
                }
                self.missions_disponibles = []
            self.factions = [
                (Faction.SPECTRES, "Les Spectres", "Hacktivistes luttant pour la vérité"),
                (Faction.FORGEURS, "Les Forgeurs", "Élite des pirates informatiques"),
                (Faction.VEILLEURS, "Les Veilleurs", "Gardiens de l'ordre numérique")
            ]
            self.jeu_mission = None
            self.shop_category = 0  # 0 pour hardware, 1 pour tools
            self.shop_selection = 0
            self.shop_message = None
            self.shop_message_timer = 0
            self.desktop = None  # Pour stocker l'instance du bureau
        except GameError as e:
            logger.error(f"Erreur d'initialisation: {e}")
            sys.exit(1)

    def get_options(self):
        # Si aucune faction n'est sélectionnée, ajouter l'option
        if not self.faction_actuelle:
            return ["CHOISIR UNE FACTION"] + self.base_options
        return self.base_options

    def afficher(self, surface):
        if self.ecran_actuel == "gameplay" and self.jeu_mission:
            self.jeu_mission.afficher()
        else:
            if self.ecran_actuel == "menu":
                self.afficher_menu_principal(surface)
            elif self.ecran_actuel == "factions":
                self.afficher_selection_faction(surface)
            elif self.ecran_actuel == "missions":
                self.afficher_missions(surface)
            elif self.ecran_actuel == "protocoles":
                self.afficher_protocoles(surface)
            elif self.ecran_actuel == "magasin":
                self.afficher_magasin(surface)

    def afficher_menu_principal(self, surface):
        surface.fill(NOIR)
        
        # ASCII Art
        y_offset = 50
        for ligne in self.ascii_art:
            texte = police_ascii.render(ligne, True, VERT_FONCE)
            rect = texte.get_rect(center=(LARGEUR//2, y_offset))
            surface.blit(texte, rect)
            y_offset += 20
        
        # Options du menu
        options = self.get_options()
        for i, option in enumerate(options):
            couleur = VERT_TERMINAL if i == self.selection else BLANC
            texte = police_menu.render(f"[{option}]", True, couleur)
            rect = texte.get_rect(center=(LARGEUR//2, HAUTEUR//2 + i * 50))
            surface.blit(texte, rect)
        
        # Effet de glitch et statut
        self.effet_glitch.update()
        self.effet_glitch.dessiner(surface)
        texte_status = police_ascii.render("STATUT: CONNEXION SÉCURISÉE", True, VERT_TERMINAL)
        surface.blit(texte_status, (20, HAUTEUR - 30))

        # Afficher le niveau et la faction si disponibles
        if self.faction_actuelle:
            info_texte = f"NIVEAU: {self.niveau_joueur} | FACTION: {self.faction_actuelle.value}"
            texte = police_ascii.render(info_texte, True, VERT_TERMINAL)
            surface.blit(texte, (20, 20))

    def afficher_selection_faction(self, surface):
        surface.fill(NOIR)
        
        # Titre
        titre = police_titre.render("SÉLECTION DE FACTION", True, VERT_TERMINAL)
        surface.blit(titre, (LARGEUR//2 - titre.get_width()//2, 50))
        
        # Description du choix
        desc = police_ascii.render("Choisissez votre faction avec précaution, ce choix est définitif", 
                                 True, VERT_FONCE)
        surface.blit(desc, (LARGEUR//2 - desc.get_width()//2, 100))
        
        # Afficher les factions
        y = 150
        for i, (faction, nom, description) in enumerate(self.factions):
            # Nom de la faction
            couleur = VERT_TERMINAL if i == self.selection else BLANC
            texte = police_menu.render(f">> {nom}", True, couleur)
            surface.blit(texte, (50, y))
            
            # Description
            desc = police_ascii.render(description, True, VERT_FONCE)
            surface.blit(desc, (70, y + 30))
            
            y += 100
        
        # Instructions
        instructions = police_ascii.render("ENTRÉE pour sélectionner - ÉCHAP pour retourner", True, VERT_FONCE)
        surface.blit(instructions, (20, HAUTEUR - 30))

    def afficher_missions(self, surface):
        surface.fill(NOIR)
        
        # Titre
        titre = police_titre.render("MISSIONS DISPONIBLES", True, VERT_TERMINAL)
        surface.blit(titre, (LARGEUR//2 - titre.get_width()//2, 50))
        
        if not self.missions_disponibles:
            texte = police_menu.render("Aucune mission disponible", True, VERT_TERMINAL)
            surface.blit(texte, (LARGEUR//2 - texte.get_width()//2, HAUTEUR//2))
            return
        
        # Afficher les missions
        y = 150
        for i, mission in enumerate(self.missions_disponibles):
            # Titre de la mission
            couleur = VERT_TERMINAL if i == self.selection else BLANC
            texte = police_menu.render(f"{mission.titre}", True, couleur)
            surface.blit(texte, (50, y))
            
            # Description
            desc = police_ascii.render(mission.description, True, VERT_FONCE)
            surface.blit(desc, (70, y + 30))
            
            # Difficulté
            diff = police_ascii.render(
                f"Difficulté: {'█' * mission.difficulte}{'░' * (5-mission.difficulte)}",
                True, VERT_TERMINAL
            )
            surface.blit(diff, (70, y + 50))
            
            y += 100

    def afficher_protocoles(self, surface):
        surface.fill(NOIR)
        
        # Titre
        titre = police_titre.render("PROTOCOLES", True, VERT_TERMINAL)
        surface.blit(titre, (LARGEUR//2 - titre.get_width()//2, 50))
        
        # Liste des protocoles
        protocoles = [
            ("SCAN", "Scanner les réseaux et systèmes"),
            ("BREACH", "Techniques d'intrusion avancées"),
            ("GHOST", "Protocoles de furtivité"),
            ("CIPHER", "Cryptographie et décryptage"),
            ("CLEAN", "Effacement des traces")
        ]
        
        y = 150
        for i, (nom, description) in enumerate(protocoles):
            # Nom du protocole
            couleur = VERT_TERMINAL if i == self.selection else BLANC
            texte = police_menu.render(f">> {nom}", True, couleur)
            surface.blit(texte, (50, y))
            
            # Description
            desc = police_ascii.render(description, True, VERT_FONCE)
            surface.blit(desc, (70, y + 30))
            
            y += 80
        
        # Instructions
        instructions = police_ascii.render("ÉCHAP pour retourner", True, VERT_FONCE)
        surface.blit(instructions, (20, HAUTEUR - 30))

    def afficher_magasin(self, surface):
        surface.fill(NOIR)
        
        # Titre et crédits
        titre = police_titre.render("MAGASIN", True, VERT_TERMINAL)
        surface.blit(titre, (LARGEUR//2 - titre.get_width()//2, 50))
        
        credits = police_menu.render(f"Crédits: {self.player_data['credits']}¢", True, VERT_TERMINAL)
        surface.blit(credits, (LARGEUR - 200, 20))
        
        # Message d'achat
        if self.shop_message and time.time() - self.shop_message_timer < 2:
            msg = police_menu.render(self.shop_message, True, VERT_TERMINAL)
            surface.blit(msg, (LARGEUR//2 - msg.get_width()//2, HAUTEUR - 50))
        
        # Catégories
        categories = ["HARDWARE", "TOOLS"]
        for i, cat in enumerate(categories):
            couleur = VERT_TERMINAL if i == self.shop_category else BLANC
            texte = police_menu.render(cat, True, couleur)
            surface.blit(texte, (50 + i * 200, 100))
        
        # Liste des items
        y = 150
        if self.shop_category == 0:  # Hardware
            available = self.shop.get_available_hardware(self.niveau_joueur)
            for i, (type, items) in enumerate(available.items()):
                for j, item in enumerate(items):
                    index = sum(len(items) for items in list(available.items())[:i]) + j
                    couleur = VERT_TERMINAL if index == self.shop_selection else BLANC
                    texte = police_menu.render(f"{item.name} - {item.price}¢", True, couleur)
                    surface.blit(texte, (50, y))
                    desc = police_ascii.render(f"{item.description} | Bonus: {list(item.bonus.values())[0]}", True, VERT_FONCE)
                    surface.blit(desc, (70, y + 20))
                    y += 60
        else:  # Tools
            available = self.shop.get_available_tools(self.niveau_joueur)
            for i, tool in enumerate(available):
                couleur = VERT_TERMINAL if i == self.shop_selection else BLANC
                texte = police_menu.render(f"{tool.name} - {tool.price}¢", True, couleur)
                surface.blit(texte, (50, y))
                desc = police_ascii.render(f"{tool.description} | Effet: {list(tool.effect.values())[0]}", True, VERT_FONCE)
                surface.blit(desc, (70, y + 20))
                y += 60

        # Instructions
        instructions = police_ascii.render("ENTRÉE pour acheter - TAB pour changer de catégorie - ÉCHAP pour retourner", True, VERT_FONCE)
        surface.blit(instructions, (20, HAUTEUR - 30))

    def start_desktop(self):
        """Démarre l'interface du bureau"""
        try:
            self.desktop = Desktop(LARGEUR, HAUTEUR, self.save_manager)
            # Préparer les données du marché
            market_data = []
            # Ajouter les outils disponibles
            for tool_id, tool in self.shop.get_available_tools().items():
                market_data.append((tool["name"], tool["price"]))
            # Ajouter le hardware disponible
            for hw_type in self.shop.hardware.keys():
                hw_info = self.shop.get_hardware_info(hw_type)
                if hw_info["upgrade_cost"] is not None:
                    market_data.append((hw_info["name"], hw_info["upgrade_cost"]))
            
            self.desktop.market_data = market_data
            self.desktop.available_missions = self.missions_disponibles
            return self.desktop.run()
        except Exception as e:
            self.logger.error(f"Erreur initialisation bureau: {e}")
            return False
    
    def gerer_evenements(self):
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                
                if event.type == pygame.KEYDOWN:
                    if self.ecran_actuel == "menu":
                        if event.key == pygame.K_RETURN:
                            option = self.get_options()[self.selection]
                            if option == "INFILTRER LE SYSTÈME":
                                return self.start_desktop()
                            elif option == "MISSIONS DISPONIBLES":
                                self.ecran_actuel = "missions"
                            elif option == "PROTOCOLES":
                                self.ecran_actuel = "protocoles"
                            elif option == "MAGASIN":
                                self.ecran_actuel = "magasin"
                            elif option == "DÉCONNEXION":
                                return False
                        elif event.key == pygame.K_UP:
                            self.selection = (self.selection - 1) % len(self.get_options())
                        elif event.key == pygame.K_DOWN:
                            self.selection = (self.selection + 1) % len(self.get_options())

                    elif self.ecran_actuel == "factions":
                        if event.key == pygame.K_RETURN:
                            self.faction_actuelle = self.factions[self.selection][0]
                            # Créer et sauvegarder les données initiales du joueur
                            self.player_data = {
                                "faction": self.faction_actuelle.value,
                                "level": 1,
                                "completed_missions": [],
                                "stats": {"successful_hacks": 0, "failed_attempts": 0},
                                "hardware": {},
                                "tools": [],
                                "credits": 1000
                            }
                            self.save_manager.save_player_data(
                                self.faction_actuelle,
                                1,  # niveau initial
                                [],  # pas de missions complétées
                                self.player_data["stats"],
                                self.player_data["hardware"],
                                self.player_data["tools"]
                            )
                            # Initialiser les missions disponibles
                            self.missions_disponibles = self.gestionnaire_missions.obtenir_missions_disponibles(
                                self.faction_actuelle,
                                1
                            )
                            self.ecran_actuel = "menu"
                        elif event.key == pygame.K_UP:
                            self.selection = (self.selection - 1) % len(self.factions)
                        elif event.key == pygame.K_DOWN:
                            self.selection = (self.selection + 1) % len(self.factions)

                    elif self.ecran_actuel == "missions":
                        if event.key == pygame.K_RETURN and self.missions_disponibles:
                            mission = self.missions_disponibles[self.selection]
                            self.jeu_mission = JeuMission(mission, self.ecran, self.save_manager)
                            self.ecran_actuel = "gameplay"
                        elif event.key == pygame.K_UP:
                            self.selection = (self.selection - 1) % len(self.missions_disponibles)
                        elif event.key == pygame.K_DOWN:
                            self.selection = (self.selection + 1) % len(self.missions_disponibles)

                    elif self.ecran_actuel == "magasin":
                        if event.key == pygame.K_TAB:
                            self.shop_category = (self.shop_category + 1) % 2
                            self.shop_selection = 0
                        elif event.key == pygame.K_RETURN:
                            self.handle_shop_purchase()
                        elif event.key == pygame.K_UP:
                            if self.shop_category == 0:
                                max_items = sum(len(items) for items in self.shop.get_available_hardware(self.niveau_joueur).values())
                                self.shop_selection = (self.shop_selection - 1) % max_items
                            else:
                                max_items = len(self.shop.get_available_tools(self.niveau_joueur))
                                self.shop_selection = (self.shop_selection - 1) % max_items
                        elif event.key == pygame.K_DOWN:
                            if self.shop_category == 0:
                                max_items = sum(len(items) for items in self.shop.get_available_hardware(self.niveau_joueur).values())
                                self.shop_selection = (self.shop_selection + 1) % max_items
                            else:
                                max_items = len(self.shop.get_available_tools(self.niveau_joueur))
                                self.shop_selection = (self.shop_selection + 1) % max_items

                    elif self.ecran_actuel == "protocoles":
                        if event.key == pygame.K_UP:
                            self.selection = (self.selection - 1) % 5  # 5 protocoles
                        elif event.key == pygame.K_DOWN:
                            self.selection = (self.selection + 1) % 5
                        elif event.key == pygame.K_RETURN:
                            # Implémenter l'action du protocole sélectionné
                            protocole = ["SCAN", "BREACH", "GHOST", "CIPHER", "CLEAN"][self.selection]
                            self.logger.info(f"Protocole sélectionné: {protocole}")
                            # Pour l'instant, retourner au menu
                            self.ecran_actuel = "menu"
                            self.selection = 0

                    if event.key == pygame.K_ESCAPE:
                        if self.ecran_actuel != "menu":
                            self.ecran_actuel = "menu"
                            self.selection = 0

            return True
        except Exception as e:
            self.logger.error(f"Erreur inattendue: {e}")
            return True

    def handle_shop_purchase(self):
        """Gère l'achat d'items dans le magasin"""
        try:
            if self.shop_category == 0:  # Hardware
                available = self.shop.get_available_hardware(self.niveau_joueur)
                items = []
                for type_items in available.values():
                    items.extend(type_items)
                if self.shop_selection < len(items):
                    item = items[self.shop_selection]
                    if self.player_data["credits"] >= item.price:
                        self.player_data["credits"] -= item.price
                        self.player_data["hardware"][item.type.name] = item.name
                        self.shop_message = f"Achat réussi: {item.name}"
                    else:
                        self.shop_message = "Crédits insuffisants"
            else:  # Tools
                available = self.shop.get_available_tools(self.niveau_joueur)
                if self.shop_selection < len(available):
                    tool = available[self.shop_selection]
                    if self.player_data["credits"] >= tool.price:
                        self.player_data["credits"] -= tool.price
                        self.player_data["tools"].append(tool.name)
                        self.shop_message = f"Achat réussi: {tool.name}"
                    else:
                        self.shop_message = "Crédits insuffisants"
            
            self.shop_message_timer = time.time()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'achat: {e}")
            self.shop_message = "Erreur lors de l'achat"

    def mission_completed(self, mission_id):
        self.missions_completees.append(mission_id)
        self.niveau_joueur += 1
        self.save_manager.save_player_data(
            self.faction_actuelle,
            self.niveau_joueur,
            self.missions_completees,
            self.player_data["stats"],
            self.player_data["hardware"],
            self.player_data["tools"]
        )
        self.missions_disponibles = self.gestionnaire_missions.obtenir_missions_disponibles(
            self.faction_actuelle, 
            self.niveau_joueur
        )

def main():
    logger = setup_logger()
    try:
        clock = pygame.time.Clock()
        menu = MenuPrincipal()
        
        en_cours = True
        while en_cours:
            try:
                en_cours = menu.gerer_evenements()
                menu.afficher(ecran)
                pygame.display.flip()
                clock.tick(60)
            except Exception as e:
                logger.error(f"Erreur dans la boucle principale: {e}")
                en_cours = False
                
    except Exception as e:
        logger.critical(f"Erreur fatale: {e}")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main() 