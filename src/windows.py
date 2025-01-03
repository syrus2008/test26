import pygame
from config import COLORS

class BaseWindow:
    def __init__(self, x, y, width, height, title="Window"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.active = True
        self.minimized = False
        self.dragging = False
        self.drag_offset = (0, 0)
        self.font = pygame.font.Font(None, 24)

    def draw(self, surface):
        if self.minimized:
            return
        
        # Fond de la fenêtre
        pygame.draw.rect(surface, COLORS["DARK_GRAY"], 
                        (self.x, self.y, self.width, self.height))
        
        # Barre de titre
        pygame.draw.rect(surface, COLORS["GREEN"],
                        (self.x, self.y, self.width, 30))
        
        # Titre
        title = self.font.render(self.title, True, COLORS["BLACK"])
        surface.blit(title, (self.x + 5, self.y + 5))

    def handle_click(self, pos):
        if self.minimized:
            return False
            
        x, y = pos
        if (self.x <= x <= self.x + self.width and
            self.y <= y <= self.y + self.height):
            self.active = True  # Activer la fenêtre lors du clic
            if y <= self.y + 30:  # Barre de titre
                self.dragging = True
                self.drag_offset = (x - self.x, y - self.y)
            return True
        return False

    def handle_keypress(self, event):
        return True

    def handle_mousewheel(self, y):
        """Gère le défilement de la molette"""
        return False  # Les fenêtres de base ne gèrent pas le défilement

class MessageWindow(BaseWindow):
    def __init__(self, x, y, width, height, messages):
        super().__init__(x, y, width, height, "Messages")
        self.messages = messages
        self.scroll_offset = 0

    def draw(self, surface):
        super().draw(surface)
        y = self.y + 40
        for msg in self.messages[self.scroll_offset:]:
            text = self.font.render(msg.content[0][:30], True, COLORS["GREEN"])
            if y + 20 > self.y + self.height:
                break
            surface.blit(text, (self.x + 10, y))
            y += 30

class MissionWindow(BaseWindow):
    def __init__(self, x, y, width, height, missions, desktop):
        super().__init__(x, y, width, height, "Missions")
        self.missions = missions
        self.scroll_offset = 0
        self.selected_mission = None
        self.selected_index = -1
        self.desktop = desktop  # Référence au bureau

    def draw(self, surface):
        super().draw(surface)
        y = self.y + 40
        
        # Dessiner les missions
        for i, mission in enumerate(self.missions[self.scroll_offset:]):
            # Couleur de fond pour la mission sélectionnée
            if i == self.selected_index:
                pygame.draw.rect(surface, COLORS["DARK_GREEN"], 
                               (self.x + 5, y - 2, self.width - 10, 24))
            
            # Titre de la mission
            text = self.font.render(mission.titre[:30], True, COLORS["GREEN"])
            if y + 20 > self.y + self.height:
                break
            surface.blit(text, (self.x + 10, y))
            
            # Description de la mission si sélectionnée
            if i == self.selected_index:
                desc_y = y + 30
                # Afficher les détails de la mission
                details = [
                    f"Type: {mission.type.value}",
                    f"Difficulté: {mission.difficulte}",
                    f"Récompense: {mission.recompense}¢",
                    "",
                    "Objectifs:",
                    *[f"- {obj}" for obj in mission.objectifs],
                    "",
                    "Objectifs secondaires:",
                    *[f"- {obj}" for obj in mission.objectifs_secondaires]
                ]
                
                for line in details:
                    if desc_y + 20 > self.y + self.height - 40:
                        break
                    text = self.font.render(line, True, COLORS["GREEN"])
                    surface.blit(text, (self.x + 20, desc_y))
                    desc_y += 20
            
            y += 30

    def handle_click(self, pos):
        if super().handle_click(pos):
            # Si le clic est dans la zone des missions
            x, y = pos
            if (self.x <= x <= self.x + self.width and
                self.y + 40 <= y <= self.y + self.height):
                # Calculer l'index de la mission cliquée
                clicked_index = (y - (self.y + 40)) // 30
                if 0 <= clicked_index < len(self.missions):
                    if self.selected_index == clicked_index:
                        # Double-clic : lancer la mission
                        self.launch_selected_mission()
                    else:
                        # Simple clic : sélectionner la mission
                        self.selected_index = clicked_index
                        self.selected_mission = self.missions[clicked_index]
            return True
        return False

    def handle_keypress(self, event):
        if event.key == pygame.K_UP:
            self.selected_index = max(0, self.selected_index - 1)
            if self.selected_index >= 0:
                self.selected_mission = self.missions[self.selected_index]
        elif event.key == pygame.K_DOWN:
            self.selected_index = min(len(self.missions) - 1, self.selected_index + 1)
            if self.selected_index >= 0:
                self.selected_mission = self.missions[self.selected_index]
        elif event.key == pygame.K_RETURN and self.selected_mission:
            self.launch_selected_mission()
        return True

    def launch_selected_mission(self):
        if self.selected_mission:
            self.desktop.start_mission(self.selected_mission)

class MarketWindow(BaseWindow):
    def __init__(self, x, y, width, height, items):
        super().__init__(x, y, width, height, "Black Market")
        self.items = items
        self.scroll_offset = 0

    def draw(self, surface):
        super().draw(surface)
        y = self.y + 40
        for item in self.items[self.scroll_offset:]:
            # Gérer les items qui sont des tuples (name, price)
            if isinstance(item, tuple):
                name, price = item
                text = self.font.render(f"{name} - {price}¢", True, COLORS["GREEN"])
            else:
                # Gérer les items qui sont des objets avec name et price
                text = self.font.render(f"{item.name} - {item.price}¢", True, COLORS["GREEN"])
            
            if y + 20 > self.y + self.height:
                break
            surface.blit(text, (self.x + 10, y))
            y += 30

class HardwareWindow(BaseWindow):
    def __init__(self, x, y, width, height, hardware, credits):
        super().__init__(x, y, width, height, "Hardware")
        self.hardware = hardware
        self.credits = credits

    def draw(self, surface):
        super().draw(surface)
        y = self.y + 40
        text = self.font.render(f"Credits: {self.credits}¢", True, COLORS["GREEN"])
        surface.blit(text, (self.x + 10, y))
        y += 30
        for name, item in self.hardware.items():
            text = self.font.render(f"{name}: {item}", True, COLORS["GREEN"])
            if y + 20 > self.y + self.height:
                break
            surface.blit(text, (self.x + 10, y))
            y += 30

class StatsWindow(BaseWindow):
    def __init__(self, x, y, width, height, player_data):
        super().__init__(x, y, width, height, "Stats")
        self.player_data = player_data

    def draw(self, surface):
        super().draw(surface)
        y = self.y + 40
        stats = [
            f"Niveau: {self.player_data['level']}",
            f"Faction: {self.player_data['faction']}",
            f"Missions: {len(self.player_data['completed_missions'])}",
            f"Credits: {self.player_data['credits']}¢"
        ]
        for stat in stats:
            text = self.font.render(stat, True, COLORS["GREEN"])
            surface.blit(text, (self.x + 10, y))
            y += 30 