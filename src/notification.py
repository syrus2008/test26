import pygame
from config import COLORS

class Notification:
    def __init__(self, message, type="info"):
        self.message = message
        self.type = type
        self.duration = 3000  # 3 secondes
        self.start_time = pygame.time.get_ticks()
        self.font = pygame.font.Font(None, 24)
        
    def draw(self, screen):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time < self.duration:
            alpha = 255 * (1 - (current_time - self.start_time) / self.duration)
            color = COLORS["GREEN"] if self.type == "success" else COLORS["RED"]
            text = self.font.render(self.message, True, color)
            text.set_alpha(alpha)
            x = (screen.get_width() - text.get_width()) // 2
            screen.blit(text, (x, 10))
            return True
        return False 