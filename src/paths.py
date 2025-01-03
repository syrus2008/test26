from pathlib import Path

# Structure des dossiers du projet
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Sous-dossiers des assets
ICONS_DIR = ASSETS_DIR / "icons"
SOUNDS_DIR = ASSETS_DIR / "sounds"
FONTS_DIR = ASSETS_DIR / "fonts"

# Sous-dossiers des données
SAVES_DIR = DATA_DIR / "saves"
CONFIG_DIR = DATA_DIR / "config"

# Créer les dossiers s'ils n'existent pas
for directory in [ASSETS_DIR, DATA_DIR, LOGS_DIR, ICONS_DIR, SOUNDS_DIR, 
                 FONTS_DIR, SAVES_DIR, CONFIG_DIR]:
    directory.mkdir(parents=True, exist_ok=True) 