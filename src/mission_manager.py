from missions import Mission, MissionType, Faction, FactionBonus

class MissionManager:
    def __init__(self, save_manager):
        self.save_manager = save_manager
        self.available_missions = {}
        self.completed_missions = set()
        self.current_mission = None
        self.load_missions()

    def load_missions(self):
        """Charge les missions disponibles"""
        # Charger les missions complétées depuis la sauvegarde
        player_data = self.save_manager.player_data
        self.completed_missions = set(player_data.get("completed_missions", []))
        
        # Charger les templates de mission
        templates = Mission.get_mission_templates()
        
        # Filtrer les missions selon le niveau et la faction du joueur
        player_level = player_data.get("level", 1)
        player_faction = player_data.get("faction")
        
        for template_name, template in templates.items():
            # Vérifier si la mission est adaptée au niveau
            if template["difficulte"] <= player_level:
                # Créer la mission
                mission = Mission.create_from_template(template_name)
                self.available_missions[mission.id] = mission

    def get_available_missions(self):
        """Retourne les missions disponibles"""
        return [
            mission for mission in self.available_missions.values()
            if mission.id not in self.completed_missions
        ]

    def get_mission_by_id(self, mission_id):
        """Récupère une mission par son ID"""
        return self.available_missions.get(mission_id)

    def start_mission(self, mission_id):
        """Démarre une mission"""
        if mission_id not in self.available_missions:
            raise ValueError("Mission non disponible")
            
        if mission_id in self.completed_missions:
            raise ValueError("Mission déjà complétée")
            
        mission = self.available_missions[mission_id]
        self.current_mission = mission
        return mission

    def complete_mission(self, mission_id):
        """Marque une mission comme complétée"""
        if mission_id not in self.available_missions:
            raise ValueError("Mission inconnue")
            
        self.completed_missions.add(mission_id)
        self.save_manager.save_completed_mission(mission_id)
        
        # Vérifier si de nouvelles missions sont débloquées
        self.check_mission_unlocks()

    def check_mission_unlocks(self):
        """Vérifie si de nouvelles missions sont débloquées"""
        player_data = self.save_manager.player_data
        player_level = player_data.get("level", 1)
        
        # Charger les nouveaux templates disponibles
        templates = Mission.get_mission_templates()
        for template_name, template in templates.items():
            mission_id = template["id"]
            if (mission_id not in self.available_missions and 
                template["difficulte"] <= player_level):
                # Débloquer la nouvelle mission
                mission = Mission.create_from_template(template_name)
                self.available_missions[mission_id] = mission

    def get_mission_progress(self, mission_id):
        """Retourne la progression d'une mission"""
        if mission_id not in self.available_missions:
            raise ValueError("Mission inconnue")
            
        mission = self.available_missions[mission_id]
        
        if mission_id in self.completed_missions:
            return {
                "status": "completed",
                "progress": 100,
                "rewards_claimed": True
            }
            
        if mission == self.current_mission:
            # Calculer la progression
            completed_objectives = sum(1 for obj in mission.objectifs if obj)
            total_objectives = len(mission.objectifs)
            progress = (completed_objectives / total_objectives) * 100
            
            return {
                "status": "in_progress",
                "progress": progress,
                "rewards_claimed": False
            }
            
        return {
            "status": "available",
            "progress": 0,
            "rewards_claimed": False
        }

    def get_mission_rewards(self, mission_id):
        """Retourne les récompenses d'une mission"""
        if mission_id not in self.available_missions:
            raise ValueError("Mission inconnue")
            
        mission = self.available_missions[mission_id]
        
        # Récompenses de base
        rewards = {
            "credits": mission.recompense,
            "xp": mission.difficulte * 100
        }
        
        # Bonus selon le type de mission
        if mission.type == MissionType.INFILTRATION:
            rewards["tool"] = "vpn"
        elif mission.type == MissionType.DATA_THEFT:
            rewards["tool"] = "decryptor"
        elif mission.type == MissionType.RANSOMWARE:
            rewards["credits"] *= 1.5
        elif mission.type == MissionType.BOTNET:
            rewards["hardware"] = "network"
        elif mission.type == MissionType.SABOTAGE:
            rewards["hardware"] = "cpu"
            
        return rewards

    def get_recommended_missions(self):
        """Retourne les missions recommandées selon le profil du joueur"""
        player_data = self.save_manager.player_data
        player_faction = player_data.get("faction")
        player_level = player_data.get("level", 1)
        
        recommended = []
        for mission in self.get_available_missions():
            # Vérifier si la mission correspond au niveau
            if mission.difficulte <= player_level + 1:
                # Calculer un score de recommandation
                score = 0
                
                # Bonus si la mission correspond à la faction
                faction_bonus = FactionBonus.get_mission_bonus(player_faction, mission.type)
                score += (faction_bonus - 1) * 100
                
                # Bonus si le joueur a les outils recommandés
                recommended_tools = mission.get_recommended_tools()
                player_tools = player_data.get("tools", [])
                tools_owned = sum(1 for tool in recommended_tools if tool in player_tools)
                score += tools_owned * 20
                
                # Malus si la mission est trop facile
                if mission.difficulte < player_level - 1:
                    score -= 30
                
                recommended.append((mission, score))
        
        # Trier par score et retourner les missions
        recommended.sort(key=lambda x: x[1], reverse=True)
        return [mission for mission, _ in recommended[:3]] 

    def obtenir_missions_disponibles(self, faction, niveau):
        """Retourne les missions disponibles pour une faction et un niveau donnés"""
        missions_disponibles = []
        completed_missions = self.save_manager.player_data.get("completed_missions", [])
        
        # Récupérer tous les templates de missions
        templates = Mission.get_mission_templates()
        
        for template_name, template in templates.items():
            # Vérifier si la mission n'a pas déjà été complétée
            if template["id"] not in completed_missions:
                # Vérifier le niveau requis (basé sur la difficulté)
                if template["difficulte"] <= niveau:
                    # Créer la mission
                    mission = Mission.create_from_template(template_name)
                    # Appliquer les bonus de faction
                    if faction:
                        bonus = FactionBonus.get_mission_bonus(faction, mission.type)
                        mission.recompense = int(mission.recompense * bonus)
                    missions_disponibles.append(mission)
        
        return missions_disponibles 