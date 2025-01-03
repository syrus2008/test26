import json
import os
from dataclasses import asdict, dataclass

@dataclass
class GameSettings:
    FULLSCREEN: bool = False
    SOUND_ENABLED: bool = True
    MUSIC_ENABLED: bool = True
    SOUND_VOLUME: float = 0.7
    MUSIC_VOLUME: float = 0.5
    SHOW_FPS: bool = False
    VSYNC: bool = True
    WINDOW_SIZE: tuple = (1024, 768)
    
    def save(self):
        """Sauvegarde les paramètres dans un fichier JSON"""
        settings_path = os.path.join(os.path.dirname(__file__), "data", "settings.json")
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        
        try:
            settings_dict = asdict(self)
            settings_dict["WINDOW_SIZE"] = list(settings_dict["WINDOW_SIZE"])
            
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings_dict, f, indent=4)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des paramètres : {e}")
            return False
    
    @classmethod
    def load(cls):
        """Charge les paramètres depuis un fichier JSON"""
        settings_path = os.path.join(os.path.dirname(__file__), "data", "settings.json")
        
        try:
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings_dict = json.load(f)
                    settings_dict["WINDOW_SIZE"] = tuple(settings_dict["WINDOW_SIZE"])
                    return cls(**settings_dict)
            return cls()  # Retourne les paramètres par défaut si le fichier n'existe pas
        except Exception as e:
            print(f"Erreur lors du chargement des paramètres : {e}")
            return cls()  # Retourne les paramètres par défaut en cas d'erreur 