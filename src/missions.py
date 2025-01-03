from enum import Enum

class MissionType(Enum):
    INFILTRATION = "Infiltration"
    DATA_THEFT = "Vol de données"
    RANSOMWARE = "Ransomware"
    BOTNET = "Botnet"
    SABOTAGE = "Sabotage"

class Faction(Enum):
    SPECTRES = "Spectres"
    FORGEURS = "Forgeurs"
    VEILLEURS = "Veilleurs"

class Mission:
    def __init__(self, id, titre, type, difficulte, recompense, objectifs, objectifs_secondaires=None):
        self.id = id
        self.titre = titre
        self.type = type
        self.difficulte = difficulte  # 1-5
        self.recompense = recompense
        self.objectifs = objectifs
        self.objectifs_secondaires = objectifs_secondaires or []
        self.completed = False

    @staticmethod
    def get_mission_templates():
        """Retourne les templates de missions disponibles"""
        return {
            "infiltration_1": {
                "id": "INF_001",
                "titre": "Première Infiltration",
                "type": MissionType.INFILTRATION,
                "difficulte": 1,
                "recompense": 1000,
                "objectifs": [
                    "Compromettre le système",
                    "Voler au moins un fichier",
                    "Maintenir l'alerte sous 50%"
                ],
                "objectifs_secondaires": [
                    "Rester non détecté",
                    "Terminer en moins de 10 minutes",
                    "Ne pas déclencher d'événements de sécurité"
                ]
            },
            "data_theft_1": {
                "id": "DAT_001",
                "titre": "Vol de Données Sensibles",
                "type": MissionType.DATA_THEFT,
                "difficulte": 2,
                "recompense": 2000,
                "objectifs": [
                    "Compromettre le système",
                    "Voler pour 2000¢ de données",
                    "Rester non détecté"
                ],
                "objectifs_secondaires": [
                    "Voler une base de données complète",
                    "Maintenir l'alerte sous 30%",
                    "Utiliser moins de 3 outils"
                ]
            },
            "ransomware_1": {
                "id": "RAN_001",
                "titre": "Opération Rançon",
                "type": MissionType.RANSOMWARE,
                "difficulte": 3,
                "recompense": 3000,
                "objectifs": [
                    "Recevoir un paiement de rançon",
                    "Collecter au moins 3000¢",
                    "Chiffrer au moins 2 systèmes"
                ],
                "objectifs_secondaires": [
                    "Chiffrer un système critique",
                    "Maintenir l'alerte sous 60%",
                    "Recevoir le paiement en moins de 3 minutes"
                ]
            },
            "botnet_1": {
                "id": "BOT_001",
                "titre": "Construction du Botnet",
                "type": MissionType.BOTNET,
                "difficulte": 3,
                "recompense": 2500,
                "objectifs": [
                    "Construire un botnet de 5 machines",
                    "Maintenir l'alerte sous 80%",
                    "Miner de la crypto pendant 3 cycles"
                ],
                "objectifs_secondaires": [
                    "Atteindre 8 machines",
                    "Rester non détecté pendant 5 minutes",
                    "Générer 1000¢ avec le minage"
                ]
            },
            "sabotage_1": {
                "id": "SAB_001",
                "titre": "Sabotage Industriel",
                "type": MissionType.SABOTAGE,
                "difficulte": 4,
                "recompense": 4000,
                "objectifs": [
                    "Compromettre un système critique",
                    "Maintenir l'alerte sous 70%",
                    "Modifier les systèmes de sécurité"
                ],
                "objectifs_secondaires": [
                    "Compromettre 2 systèmes critiques",
                    "Rester non détecté pendant 8 minutes",
                    "Ne pas laisser de traces"
                ]
            }
        }

    @classmethod
    def create_from_template(cls, template_name):
        """Crée une mission à partir d'un template"""
        templates = cls.get_mission_templates()
        if template_name not in templates:
            raise ValueError(f"Template de mission inconnu: {template_name}")
            
        template = templates[template_name]
        return cls(
            id=template["id"],
            titre=template["titre"],
            type=template["type"],
            difficulte=template["difficulte"],
            recompense=template["recompense"],
            objectifs=template["objectifs"],
            objectifs_secondaires=template.get("objectifs_secondaires")
        )

    def get_difficulty_description(self):
        """Retourne une description de la difficulté"""
        descriptions = {
            1: "Facile - Parfait pour débuter",
            2: "Modéré - Quelques défis",
            3: "Difficile - Expérience requise",
            4: "Très difficile - Pour experts",
            5: "Extrême - Risque maximal"
        }
        return descriptions.get(self.difficulte, "Difficulté inconnue")

    def get_mission_description(self):
        """Retourne une description détaillée de la mission"""
        description = [
            f"=== {self.titre} ===",
            f"Type: {self.type.value}",
            f"Difficulté: {self.get_difficulty_description()}",
            f"Récompense: {self.recompense}¢",
            "",
            "Objectifs principaux:",
            *[f"- {obj}" for obj in self.objectifs]
        ]
        
        if self.objectifs_secondaires:
            description.extend([
                "",
                "Objectifs secondaires:",
                *[f"- {obj}" for obj in self.objectifs_secondaires]
            ])
            
        return description

    def get_recommended_tools(self):
        """Retourne les outils recommandés pour la mission"""
        tools = {
            MissionType.INFILTRATION: ["vpn", "cleaner"],
            MissionType.DATA_THEFT: ["decryptor", "vpn"],
            MissionType.RANSOMWARE: ["rootkit", "decryptor"],
            MissionType.BOTNET: ["rootkit", "vpn"],
            MissionType.SABOTAGE: ["rootkit", "cleaner"]
        }
        return tools.get(self.type, []) 

class FactionBonus:
    """Gère les bonus spécifiques à chaque faction"""
    
    @staticmethod
    def get_mission_bonus(faction, mission_type):
        """Retourne le multiplicateur de bonus pour une faction et un type de mission"""
        bonuses = {
            Faction.SPECTRES: {
                MissionType.INFILTRATION: 1.5,  # +50% pour infiltration
                MissionType.DATA_THEFT: 1.3,    # +30% pour vol de données
                MissionType.RANSOMWARE: 1.0,
                MissionType.BOTNET: 1.0,
                MissionType.SABOTAGE: 1.2
            },
            Faction.FORGEURS: {
                MissionType.INFILTRATION: 1.0,
                MissionType.DATA_THEFT: 1.2,
                MissionType.RANSOMWARE: 1.5,    # +50% pour ransomware
                MissionType.BOTNET: 1.3,        # +30% pour botnet
                MissionType.SABOTAGE: 1.0
            },
            Faction.VEILLEURS: {
                MissionType.INFILTRATION: 1.2,
                MissionType.DATA_THEFT: 1.0,
                MissionType.RANSOMWARE: 1.0,
                MissionType.BOTNET: 1.2,
                MissionType.SABOTAGE: 1.5       # +50% pour sabotage
            }
        }
        return bonuses.get(faction, {}).get(mission_type, 1.0)
    
    @staticmethod
    def get_faction_description(faction):
        """Retourne la description et les bonus d'une faction"""
        descriptions = {
            Faction.SPECTRES: {
                "specialite": "Experts en infiltration et vol de données",
                "bonus": [
                    "+50% de récompense sur les missions d'infiltration",
                    "+30% de récompense sur les missions de vol de données",
                    "+20% de furtivité",
                    "-20% de temps de piratage"
                ]
            },
            Faction.FORGEURS: {
                "specialite": "Maîtres du ransomware et des botnets",
                "bonus": [
                    "+50% de récompense sur les missions de ransomware",
                    "+30% de récompense sur les missions de botnet",
                    "+20% d'efficacité des malwares",
                    "-20% de coût des outils"
                ]
            },
            Faction.VEILLEURS: {
                "specialite": "Spécialistes du sabotage et de la surveillance",
                "bonus": [
                    "+50% de récompense sur les missions de sabotage",
                    "+20% de récompense sur les missions d'infiltration et de botnet",
                    "+20% de résistance des outils",
                    "-20% de détection"
                ]
            }
        }
        return descriptions.get(faction, {
            "specialite": "Faction inconnue",
            "bonus": []
        }) 