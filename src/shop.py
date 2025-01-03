from enum import Enum

class HardwareType(Enum):
    CPU = "cpu"
    RAM = "ram"
    NETWORK = "network"
    COOLING = "cooling"

class Shop:
    def __init__(self, save_manager):
        self.save_manager = save_manager
        self.tools = {
            "vpn": {
                "name": "VPN",
                "price": 1500,
                "description": "Réduit la détection de 30%",
                "level_required": 1
            },
            "decryptor": {
                "name": "Décrypteur",
                "price": 2000,
                "description": "Permet de décrypter les fichiers chiffrés",
                "level_required": 2
            },
            "rootkit": {
                "name": "Rootkit",
                "price": 3000,
                "description": "Augmente les chances de hack de 40%",
                "level_required": 3
            },
            "cleaner": {
                "name": "Nettoyeur",
                "price": 1000,
                "description": "Réduit la détection de 20% supplémentaire",
                "level_required": 2
            }
        }
        
        self.hardware = {
            HardwareType.CPU: {
                "name": "Processeur",
                "base_price": 5000,
                "description": "Améliore les performances générales",
                "level_multiplier": 1.5
            },
            HardwareType.RAM: {
                "name": "Mémoire",
                "base_price": 4000,
                "description": "Augmente la capacité de traitement",
                "level_multiplier": 1.4
            },
            HardwareType.NETWORK: {
                "name": "Carte Réseau",
                "base_price": 3500,
                "description": "Améliore les connexions",
                "level_multiplier": 1.3
            },
            HardwareType.COOLING: {
                "name": "Refroidissement",
                "base_price": 2500,
                "description": "Réduit l'usure des outils",
                "level_multiplier": 1.2
            }
        }

    def get_available_tools(self):
        """Retourne les outils disponibles à l'achat"""
        player_level = self.save_manager.player_data["level"]
        player_tools = self.save_manager.player_data.get("tools", [])
        
        available = {}
        for tool_id, tool in self.tools.items():
            if (tool_id not in player_tools and 
                tool["level_required"] <= player_level):
                available[tool_id] = tool
                
        return available

    def get_hardware_upgrade_cost(self, hardware_type):
        """Calcule le coût d'amélioration d'un composant"""
        if hardware_type not in self.hardware:
            raise ValueError("Type de hardware invalide")
            
        hardware = self.hardware[hardware_type]
        current_level = self.save_manager.player_data["hardware"][hardware_type.value]["level"]
        
        if current_level >= 5:  # Niveau maximum
            return None
            
        return int(hardware["base_price"] * (hardware["level_multiplier"] ** current_level))

    def buy_tool(self, tool_id):
        """Achète un outil"""
        if tool_id not in self.tools:
            raise ValueError("Outil invalide")
            
        tool = self.tools[tool_id]
        player_data = self.save_manager.player_data
        
        # Vérifier le niveau requis
        if player_data["level"] < tool["level_required"]:
            raise ValueError(f"Niveau {tool['level_required']} requis")
            
        # Vérifier si l'outil est déjà possédé
        if tool_id in player_data.get("tools", []):
            raise ValueError("Outil déjà possédé")
            
        # Vérifier les crédits
        if player_data["credits"] < tool["price"]:
            raise ValueError("Crédits insuffisants")
            
        # Effectuer l'achat
        player_data["credits"] -= tool["price"]
        self.save_manager.add_tool(tool_id)
        
        return {
            "success": True,
            "message": f"{tool['name']} acheté avec succès",
            "remaining_credits": player_data["credits"]
        }

    def upgrade_hardware(self, hardware_type):
        """Améliore un composant hardware"""
        if not isinstance(hardware_type, HardwareType):
            raise ValueError("Type de hardware invalide")
            
        cost = self.get_hardware_upgrade_cost(hardware_type)
        if cost is None:
            raise ValueError("Niveau maximum atteint")
            
        player_data = self.save_manager.player_data
        if player_data["credits"] < cost:
            raise ValueError("Crédits insuffisants")
            
        # Effectuer l'amélioration
        player_data["credits"] -= cost
        success = self.save_manager.upgrade_hardware(hardware_type.value)
        
        if success:
            new_level = player_data["hardware"][hardware_type.value]["level"]
            return {
                "success": True,
                "message": f"{self.hardware[hardware_type]['name']} amélioré au niveau {new_level}",
                "remaining_credits": player_data["credits"]
            }
        else:
            raise ValueError("Erreur lors de l'amélioration")

    def get_tool_info(self, tool_id):
        """Retourne les informations détaillées d'un outil"""
        if tool_id not in self.tools:
            raise ValueError("Outil invalide")
            
        tool = self.tools[tool_id]
        player_data = self.save_manager.player_data
        
        return {
            "name": tool["name"],
            "price": tool["price"],
            "description": tool["description"],
            "level_required": tool["level_required"],
            "owned": tool_id in player_data.get("tools", []),
            "can_afford": player_data["credits"] >= tool["price"],
            "level_ok": player_data["level"] >= tool["level_required"]
        }

    def get_hardware_info(self, hardware_type):
        """Retourne les informations détaillées d'un composant hardware"""
        if not isinstance(hardware_type, HardwareType):
            raise ValueError("Type de hardware invalide")
            
        hardware = self.hardware[hardware_type]
        current_level = self.save_manager.player_data["hardware"][hardware_type.value]["level"]
        upgrade_cost = self.get_hardware_upgrade_cost(hardware_type)
        
        return {
            "name": hardware["name"],
            "description": hardware["description"],
            "current_level": current_level,
            "max_level": current_level >= 5,
            "upgrade_cost": upgrade_cost,
            "can_afford": upgrade_cost is not None and 
                         self.save_manager.player_data["credits"] >= upgrade_cost
        } 