import pygame
from config import COLORS

def create_terminal_icon():
    surface = pygame.Surface((64, 64))
    surface.fill(COLORS["BLACK"])
    pygame.draw.rect(surface, COLORS["GREEN"], (10, 10, 44, 44), 2)
    return surface

def create_message_icon():
    surface = pygame.Surface((64, 64))
    surface.fill(COLORS["BLACK"])
    pygame.draw.polygon(surface, COLORS["GREEN"], 
                       [(10, 10), (54, 10), (32, 44)])
    return surface

def create_missions_icon():
    surface = pygame.Surface((64, 64))
    surface.fill(COLORS["BLACK"])
    pygame.draw.rect(surface, COLORS["GREEN"], (10, 5, 44, 54), 2)
    for y in range(20, 50, 10):
        pygame.draw.line(surface, COLORS["GREEN"], (15, y), (49, y), 2)
    return surface

def create_market_icon():
    surface = pygame.Surface((64, 64))
    surface.fill(COLORS["BLACK"])
    pygame.draw.circle(surface, COLORS["GREEN"], (32, 32), 25, 2)
    pygame.draw.line(surface, COLORS["GREEN"], (32, 15), (32, 49), 2)
    pygame.draw.line(surface, COLORS["GREEN"], (15, 32), (49, 32), 2)
    return surface

def create_hardware_icon():
    surface = pygame.Surface((64, 64))
    surface.fill(COLORS["BLACK"])
    pygame.draw.rect(surface, COLORS["GREEN"], (10, 20, 44, 34), 2)
    pygame.draw.circle(surface, COLORS["GREEN"], (20, 37), 5, 2)
    pygame.draw.circle(surface, COLORS["GREEN"], (35, 37), 5, 2)
    return surface

def create_stats_icon():
    surface = pygame.Surface((64, 64))
    surface.fill(COLORS["BLACK"])
    points = [(10, 50), (25, 20), (40, 35), (55, 15)]
    pygame.draw.lines(surface, COLORS["GREEN"], False, points, 2)
    for x, y in points:
        pygame.draw.circle(surface, COLORS["GREEN"], (x, y), 3)
    return surface

ICON_CREATORS = {
    "terminal": create_terminal_icon,
    "messages": create_message_icon,
    "missions": create_missions_icon,
    "market": create_market_icon,
    "hardware": create_hardware_icon,
    "stats": create_stats_icon
} 