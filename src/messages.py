from enum import Enum
from dataclasses import dataclass
from typing import List
from missions import Faction

class MessageType(Enum):
    MISSION = "Mission"
    SYSTEM = "System"
    WARNING = "Warning"
    ERROR = "Error"

@dataclass
class Message:
    id: str
    sender: str
    type: MessageType
    content: List[str]
    read: bool = False

class SystemeMessage:
    def __init__(self):
        self.messages = [
            Message(
                id="WELCOME",
                sender="SYSTÈME",
                type=MessageType.SYSTEM,
                content=[
                    "Bienvenue dans le réseau",
                    "Utilisez les commandes disponibles pour interagir",
                    "Tapez 'help' pour voir la liste des commandes"
                ]
            )
        ]
        self.story_messages = {
            # Introduction et Tutoriel
            "GAME_START": Message(
                id="GAME_START",
                sender="SYSTÈME",
                type=MessageType.SYSTEM,
                content=[
                    "Année 2084. Le monde est contrôlé par les mégacorporations.",
                    "En tant que hacker indépendant, vous cherchez à faire votre place",
                    "dans ce monde cyberpunk..."
                ]
            ),
            
            # Messages par Faction
            "SPECTRES_INTRO": Message(
                id="SPECTRES_INTRO",
                sender="GHOST_RUNNER",
                type=MessageType.MISSION,
                content=[
                    "Les Spectres t'observent depuis un moment.",
                    "Nous luttons pour révéler la vérité au monde.",
                    "Si tu nous rejoins, tu auras accès à des missions d'infiltration",
                    "et de vol de données sensibles."
                ]
            ),
            
            # Progression des missions Spectres
            "SPECTRES_M1": Message(
                id="SPECTRES_M1",
                sender="GHOST_RUNNER",
                type=MessageType.MISSION,
                content=[
                    "Première mission : Infiltrer MegaCorp Industries",
                    "Nous avons besoin de preuves de leur corruption.",
                    "Trouve les documents compromettants et sors sans te faire repérer."
                ]
            ),
            "SPECTRES_M1_SUCCESS": Message(
                id="SPECTRES_M1_SUCCESS",
                sender="GHOST_RUNNER",
                type=MessageType.MISSION,
                content=[
                    "Excellent travail sur MegaCorp !",
                    "Ces documents vont faire trembler leur empire.",
                    "Continue comme ça, nous avons d'autres cibles..."
                ]
            ),
            
            # Messages de progression générale
            "LEVEL_UP_5": Message(
                id="LEVEL_UP_5",
                sender="MENTOR",
                type=MessageType.SYSTEM,
                content=[
                    "Tu commences à te faire un nom dans le milieu.",
                    "De nouvelles opportunités s'ouvrent à toi.",
                    "Je t'ai débloqué l'accès à de meilleurs équipements."
                ]
            ),
            
            # Messages d'événements spéciaux
            "CORP_WAR_START": Message(
                id="CORP_WAR_START",
                sender="INFO_BROKER",
                type=MessageType.WARNING,
                content=[
                    "ALERTE : Guerre des corporations imminente !",
                    "MegaCorp et ByteCorp s'affrontent ouvertement.",
                    "C'est le moment idéal pour profiter du chaos..."
                ]
            ),
            
            # Messages de conséquences
            "HIGH_NOTORIETY": Message(
                id="HIGH_NOTORIETY",
                sender="SYSTÈME",
                type=MessageType.WARNING,
                content=[
                    "ATTENTION : Votre notoriété attire l'attention",
                    "Les corporations ont renforcé leur sécurité",
                    "Soyez plus prudent dans vos opérations"
                ]
            )
        }
        
    def ajouter_message(self, message: Message):
        self.messages.append(message)
    
    def obtenir_messages(self, filter_type="ALL"):
        if filter_type == "ALL":
            return self.messages
        return [m for m in self.messages if m.type == filter_type] 
    
    def envoyer_message_progression(self, trigger_event, player_data):
        """Envoie des messages basés sur les événements du jeu"""
        if trigger_event == "game_start":
            self.ajouter_message(self.story_messages["GAME_START"])
            
        elif trigger_event == "mission_complete":
            missions_completed = len(player_data["completed_missions"])
            faction = player_data["faction"]
            
            # Messages spécifiques aux missions des Spectres
            if faction == Faction.SPECTRES:
                if "INF_001" in player_data["completed_missions"]:
                    self.ajouter_message(self.story_messages["SPECTRES_M1_SUCCESS"])
            
            # Messages de progression générale
            if missions_completed == 5:
                self.ajouter_message(self.story_messages["LEVEL_UP_5"])
                
        elif trigger_event == "faction_choice":
            if player_data["faction"] == Faction.SPECTRES:
                self.ajouter_message(self.story_messages["SPECTRES_INTRO"])
                self.ajouter_message(self.story_messages["SPECTRES_M1"])
            
        elif trigger_event == "detection":
            self.ajouter_message(self.story_messages["DETECTION_WARNING"])
            if player_data.get("notoriety", 0) > 75:
                self.ajouter_message(self.story_messages["HIGH_NOTORIETY"])
            
        # Événements spéciaux basés sur le temps de jeu ou les actions
        elif trigger_event == "time_trigger" and player_data["play_time"] > 3600:  # 1 heure
            self.ajouter_message(self.story_messages["CORP_WAR_START"]) 