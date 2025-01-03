import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
SAVE_DIR = DATA_DIR / "save_games"
FONTS_DIR = ASSETS_DIR / "fonts"
SOUNDS_DIR = ASSETS_DIR / "sounds"
MUSIC_DIR = ASSETS_DIR / "music"

# Créer les répertoires s'ils n'existent pas
for directory in [ASSETS_DIR, DATA_DIR, SAVE_DIR, FONTS_DIR, SOUNDS_DIR, MUSIC_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configuration générale
GAME_VERSION = "0.1.0"
DEBUG_MODE = False

# Configuration de l'affichage
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60

# Couleurs
COLORS = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GREEN": (0, 255, 0),
    "DARK_GREEN": (0, 180, 0),
    "RED": (255, 0, 0),
    "BLUE": (0, 0, 255),
    "DARK_GRAY": (50, 50, 50)
}

# Configuration du jeu
STARTING_CREDITS = 1000
MAX_ALERT_LEVEL = 100
MISSION_BASE_DURATION = 300  # en secondes

# Messages
MESSAGES = {
    "MISSION_COMPLETE": "MISSION COMPLETE",
    "MISSION_FAILED": "MISSION FAILED",
    "TIME_OUT": "TIME OUT",
    "DETECTED": "DETECTED",
    "HIDDEN": "Hidden"
}

# Configuration du bureau
DESKTOP_CONFIG = {
    "TASKBAR_HEIGHT": 40,
    "ICON_SIZE": 64,
    "ICON_SPACING": 100,
    "WINDOW_MIN_WIDTH": 200,
    "WINDOW_MIN_HEIGHT": 150,
    "ANIMATION_SPEED": 0.1
}

# Ajouter des constantes de gameplay
GAMEPLAY_CONFIG = {
    "BASE_SUCCESS_RATE": 0.7,
    "STEALTH_BONUS": 0.2,
    "DETECTION_THRESHOLD": 80,
    "ALERT_INCREASE_RATE": {
        "LOW": 5,
        "MEDIUM": 10,
        "HIGH": 20
    }
}

# Ajouter des messages d'erreur
ERROR_MESSAGES = {
    "SAVE_ERROR": "Erreur lors de la sauvegarde",
    "LOAD_ERROR": "Erreur lors du chargement",
    "INVALID_TARGET": "Cible invalide",
    "MISSION_ERROR": "Erreur de mission"
} 