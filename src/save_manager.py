import json
import os
from datetime import datetime
from missions import Faction

class SaveManager:
    def __init__(self, save_directory="saves"):
        self.save_directory = save_directory
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
        self.ensure_save_directory()
        self.load_player_data()

    def ensure_save_directory(self):
        """Crée le répertoire de sauvegarde s'il n'existe pas"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

    def get_save_path(self, faction_name):
        """Retourne le chemin du fichier de sauvegarde pour une faction"""
        return os.path.join(self.save_directory, f"{faction_name.lower()}_save.json")

    def save_player_data(self, faction, level, completed_missions, stats, hardware, tools):
        """Sauvegarde les données du joueur"""
        self.player_data.update({
            "faction": faction.value if faction else None,
            "level": level,
            "completed_missions": completed_missions,
            "stats": stats,
            "hardware": hardware,
            "tools": tools,
            "last_save": datetime.now().isoformat()
        })
        
        save_path = self.get_save_path(faction.value if faction else "default")
        with open(save_path, 'w') as f:
            json.dump(self.player_data, f, indent=4)

    def load_player_data(self):
        """Charge les données du joueur"""
        # Chercher une sauvegarde existante
        save_files = [f for f in os.listdir(self.save_directory) 
                     if f.endswith('_save.json')]
        
        if not save_files:
            return False
            
        # Charger la sauvegarde la plus récente
        latest_save = max(save_files, key=lambda f: os.path.getmtime(
            os.path.join(self.save_directory, f)))
        
        try:
            with open(os.path.join(self.save_directory, latest_save), 'r') as f:
                data = json.load(f)
                
            # Convertir la faction de string à enum
            if data.get("faction"):
                faction_name = data["faction"]
                if isinstance(faction_name, str):
                    try:
                        data["faction"] = Faction(faction_name)
                    except ValueError:
                        # Si la conversion échoue, mettre faction à None
                        data["faction"] = None
                
            self.player_data.update(data)
            return True
        except Exception as e:
            print(f"Erreur lors du chargement de la sauvegarde: {e}")
            return False

    def save_completed_mission(self, mission_id):
        """Sauvegarde une mission complétée"""
        if mission_id not in self.player_data["completed_missions"]:
            self.player_data["completed_missions"].append(mission_id)
            self.save_player_data(
                self.player_data["faction"],
                self.player_data["level"],
                self.player_data["completed_missions"],
                self.player_data["stats"],
                self.player_data["hardware"],
                self.player_data["tools"]
            )

    def create_new_save(self, faction):
        """Crée une nouvelle sauvegarde"""
        self.player_data["faction"] = faction
        self.player_data["level"] = 1
        self.player_data["credits"] = 1000
        self.player_data["completed_missions"] = []
        self.player_data["tools"] = ["vpn"]  # Outil de départ
        self.player_data["stats"] = {
            "missions_completed": 0,
            "total_earnings": 0,
            "successful_hacks": 0,
            "stealth_missions": 0,
            "data_stolen_value": 0,
            "largest_botnet": 0,
            "total_ransom": 0
        }
        
        # Sauvegarder
        self.save_player_data(
            faction,
            self.player_data["level"],
            self.player_data["completed_missions"],
            self.player_data["stats"],
            self.player_data["hardware"],
            self.player_data["tools"]
        )

    def backup_save(self):
        """Crée une sauvegarde de secours"""
        if not self.player_data["faction"]:
            return False
            
        backup_dir = os.path.join(self.save_directory, "backups")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(
            backup_dir, 
            f"{self.player_data['faction'].value.lower()}_{timestamp}.json"
        )
        
        with open(backup_path, 'w') as f:
            json.dump(self.player_data, f, indent=4)
        
        # Nettoyer les anciennes sauvegardes (garder les 5 plus récentes)
        backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.json')],
                        key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)))
        
        while len(backups) > 5:
            os.remove(os.path.join(backup_dir, backups.pop(0)))
            
        return True

    def update_stats(self, stat_updates):
        """Met à jour les statistiques du joueur"""
        for key, value in stat_updates.items():
            if key in self.player_data["stats"]:
                if isinstance(value, (int, float)):
                    self.player_data["stats"][key] += value
                else:
                    self.player_data["stats"][key] = value
                    
        # Sauvegarder automatiquement après la mise à jour des stats
        self.save_player_data(
            self.player_data["faction"],
            self.player_data["level"],
            self.player_data["completed_missions"],
            self.player_data["stats"],
            self.player_data["hardware"],
            self.player_data["tools"]
        )

    def add_tool(self, tool_name):
        """Ajoute un nouvel outil à l'inventaire"""
        if tool_name not in self.player_data["tools"]:
            self.player_data["tools"].append(tool_name)
            self.save_player_data(
                self.player_data["faction"],
                self.player_data["level"],
                self.player_data["completed_missions"],
                self.player_data["stats"],
                self.player_data["hardware"],
                self.player_data["tools"]
            )
            return True
        return False

    def upgrade_hardware(self, hardware_type):
        """Améliore un composant hardware"""
        if hardware_type in self.player_data["hardware"]:
            current_level = self.player_data["hardware"][hardware_type]["level"]
            if current_level < 5:  # Maximum niveau 5
                self.player_data["hardware"][hardware_type]["level"] += 1
                self.player_data["hardware"][hardware_type]["bonus"] += 0.1
                
                self.save_player_data(
                    self.player_data["faction"],
                    self.player_data["level"],
                    self.player_data["completed_missions"],
                    self.player_data["stats"],
                    self.player_data["hardware"],
                    self.player_data["tools"]
                )
                return True
        return False 