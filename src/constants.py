from enum import Enum, auto

class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4

# Constantes de gameplay
MAX_LEVEL = 50
BASE_CREDITS = 1000
LEVEL_MULTIPLIER = 1.5
MAX_INVENTORY_SIZE = 20

# Constantes de temps
TICK_RATE = 60
ANIMATION_SPEED = 0.1
NOTIFICATION_DURATION = 3000 