import pygame
import random
import time
from dataclasses import dataclass
from config import COLORS
from shop import HardwareType
from missions import MissionType, Faction
from messages import SystemeMessage, MessageType
from exceptions import MissionError, SecurityError, HardwareError
from targets import TargetGenerator, Target
from logger import setup_logger
from windows import BaseWindow
from enums import SecurityLevel, TargetType
from enum import Enum

class SecurityLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    EXTREME = 4

class TargetType(Enum):
    CORPORATE = "Entreprise"
    BANK = "Banque"
    RESEARCH = "Recherche"
    INFRASTRUCTURE = "Infrastructure"
    GOVERNMENT = "Gouvernement"

class Terminal(BaseWindow):
    def __init__(self, x, y, width, height, jeu_mission=None):
        super().__init__(x, y, width, height, title="Terminal")
        print("Initialisation du Terminal...")  # Debug
        self.contenu = ""
        
        # Initialiser l'historique avec les informations de mission
        mission_info = [
            "CyberHack OS v2.84 - Terminal Ready",
            "Type 'help' for commands",
            "----------------------------------------",
            "MISSION BRIEFING:"
        ]
        
        # Ajouter les détails de la mission si disponible
        if jeu_mission and jeu_mission.mission:
            print(f"Mission trouvée: {jeu_mission.mission.titre}")  # Debug
            try:
                mission_info.extend([
                    f"Mission: {jeu_mission.mission.titre}",
                    "Objectifs:",
                    *[f"- {obj}" for obj in jeu_mission.mission.objectifs]
                ])
            except Exception as e:
                print(f"Erreur lors de l'ajout des objectifs: {e}")  # Debug
            
        mission_info.append("----------------------------------------")
        
        self.historique = mission_info
        self.prompt = "root@cyber:~$ "
        self.jeu_mission = jeu_mission
        self.scroll_offset = 0
        self.line_height = 20
        self.font = pygame.font.Font(None, 24)
        print("Terminal initialisé avec succès")  # Debug

    def handle_keypress(self, event):
        """Gère les entrées clavier"""
        if not self.active:
            return False

        if event.key == pygame.K_RETURN:
            if self.contenu:
                self.historique.append(self.prompt + self.contenu)
                if self.jeu_mission:
                    try:
                        commande = self.contenu.split()
                        if commande:
                            resultat = self.jeu_mission.execute_command(commande[0], commande[1:] if len(commande) > 1 else [])
                            if resultat:
                                self.historique.extend(resultat)
                    except Exception as e:
                        print(f"Erreur dans Terminal: {e}")
                        self.historique.append(f"Erreur: {str(e)}")
                self.contenu = ""
        elif event.key == pygame.K_BACKSPACE:
            self.contenu = self.contenu[:-1]
        else:
            if event.unicode.isprintable():
                self.contenu += event.unicode
        return True

    def handle_mousewheel(self, y):
        """Gère le défilement de la molette"""
        max_scroll = max(0, len(self.historique) * self.line_height - (self.height - 60))
        self.scroll_offset = max(0, min(max_scroll, self.scroll_offset - y * 20))
        return True

    def draw(self, surface):
        super().draw(surface)
        
        # Calculer les lignes visibles en tenant compte du défilement
        visible_lines = (self.height - 60) // self.line_height
        total_height = len(self.historique) * self.line_height
        
        # Calculer l'index de départ basé sur le défilement
        start_line = self.scroll_offset // self.line_height
        
        # Dessiner l'historique
        for i, ligne in enumerate(self.historique[start_line:start_line + visible_lines]):
            y_pos = self.y + 40 + (i * self.line_height) - (self.scroll_offset % self.line_height)
            texte = self.font.render(ligne, True, COLORS["GREEN"])
            surface.blit(texte, (self.x + 10, y_pos))
        
        # Toujours afficher la ligne de commande en bas
        ligne_commande = self.prompt + self.contenu
        if time.time() % 1 > 0.5:
            ligne_commande += "█"
        texte = self.font.render(ligne_commande, True, COLORS["GREEN"])
        surface.blit(texte, (self.x + 10, self.y + self.height - 30))

class JeuMission:
    def __init__(self, mission, ecran, save_manager):
        print("Initialisation de JeuMission...")  # Debug
        if not mission or not save_manager:
            raise ValueError("Mission et save_manager sont requis")
            
        self.logger = setup_logger()
        self.mission = mission
        print(f"Mission chargée: {mission.titre}")  # Debug
        self.ecran = ecran
        self.save_manager = save_manager
        self.systeme_compromis = False
        self.donnees_volees = []
        self.alert_level = 0
        self.detected = False
        self.is_running = True
        
        # Initialiser les cibles en fonction de la mission
        self.target_generator = TargetGenerator()
        # Charger les cibles principales
        self.primary_targets = self.target_generator.get_targets_for_mission(mission.id)
        # Charger les cibles secondaires
        self.secondary_targets = self.target_generator.get_secondary_targets_for_mission(mission.id)
        # Combiner toutes les cibles disponibles
        self.available_targets = self.primary_targets + self.secondary_targets
        
        print(f"Cibles principales: {[t.name for t in self.primary_targets]}")  # Debug
        print(f"Cibles secondaires: {[t.name for t in self.secondary_targets]}")  # Debug
        
        self.current_target = None
        self.botnet_size = 0
        self.botnet_targets = []  # Liste des machines dans le botnet
        self.encrypted_systems = {}
        self.total_ransom = 0
        
        # Initialiser les timers
        self.last_event_check = time.time()
        self.last_save_time = time.time()
        self.last_difficulty_check = time.time()
        self.last_unlock_check = time.time()
        self.last_botnet_check = time.time()  # Timer pour les revenus du botnet
        
        # Initialiser les commandes disponibles
        self.commandes_disponibles = {
            'help': self.cmd_help,
            'scan': self.cmd_scan,
            'connect': self.cmd_connect,
            'crack': self.cmd_crack,
            'inject': self.cmd_inject,
            'clear': self.cmd_clear,
            'status': self.cmd_status,
            'mission': self.cmd_mission,
            'exit': self.cmd_exit,
            'ls': self.cmd_ls,
            'tools': self.cmd_tools,
            'stats': self.cmd_stats,
            'analyze': self.cmd_analyze,
            'stealth': self.cmd_stealth,
            'ransom': self.cmd_ransom,
            'botnet': self.cmd_botnet,
            'market': self.cmd_market,
            'exfiltrate': self.cmd_exfiltrate,
            'download': self.cmd_download,
            'modify': self.cmd_modify,
            'exploit': self.cmd_exploit
        }
        
        # Créer le terminal
        self.terminal = Terminal(50, 50, 924, 668, self)
        
        # Ajouter ces attributs manquants
        self.mission_duration = 1800  # 30 minutes par défaut
        self.mission_start_time = time.time()
        self.objectifs_completes = [False] * len(mission.objectifs)
        self.hardware_bonus = {"stealth": 1.0, "exploit": 0}
        self.player_data = save_manager.player_data
        
        # Ajouter la gestion de l'état des outils
        self.tool_durability = {}
        for tool in self.player_data.get("tools", []):
            self.tool_durability[tool] = 100  # Durabilité initiale de 100%
        
        # Ajouter le suivi des payloads
        self.active_payloads = {}  # {target_id: {payload_type: timestamp}}
        self.payload_effects = {
            "keylogger": {"data_rate": 100, "detection_rate": 5},
            "backdoor": {"data_rate": 50, "detection_rate": 2},
            "miner": {"credits_rate": 200, "detection_rate": 8},
            "trojan": {"data_rate": 150, "detection_rate": 10}
        }
        self.last_payload_check = time.time()
        
        # Ajouter la gestion du hardware
        self.hardware_stats = {
            "cpu": {"level": 1, "bonus": 0.1},
            "ram": {"level": 1, "bonus": 0.1},
            "network": {"level": 1, "bonus": 0.1},
            "cooling": {"level": 1, "bonus": 0.1}
        }
        
        # Ajouter la gestion des bonus temporaires
        self.active_bonuses = {
            "stealth": [],  # [(bonus_value, end_time), ...]
            "hack": [],
            "detection": []
        }

    def execute_command(self, command, args):
        """Exécute une commande avec gestion d'erreurs"""
        try:
            if not self.is_running:
                return ["Session terminée"]
                
            if command not in self.commandes_disponibles:
                return [f"Commande inconnue: {command}"]
                
            # Vérifier si la commande nécessite une connexion
            requires_connection = ["crack", "inject", "exfiltrate", "ls", "analyze"]
            if command in requires_connection and not self.current_target:
                return ["Erreur: Aucune cible connectée"]
                
            # Vérifier si la commande nécessite un système compromis
            requires_compromise = ["inject", "exfiltrate", "ransom", "botnet", "miner"]
            if command in requires_compromise and not self.systeme_compromis:
                return ["Erreur: Système non compromis"]
                
            return self.commandes_disponibles[command](args)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution de {command}: {e}")
            return [f"Erreur: {str(e)}"]

    def cmd_scan(self, args):
        """Scanne les cibles potentielles"""
        if self.current_target:
            return ["Erreur: Déjà connecté à une cible"]
            
        results = ["Scan en cours..."]
        for target in self.available_targets:
            results.extend([
                f"\nCible détectée: {target.name}",
                f"IP: {target.ip}",
                f"Ports ouverts: {', '.join(map(str, target.ports))}",
                f"Niveau de sécurité: {target.security_level.value}"
            ])
            
        self.update_alert_level(5)  # Scan léger augmente peu l'alerte
        return results

    def cmd_connect(self, args):
        """Se connecte à une cible"""
        if not args:
            return ["Usage: connect <ip> [port]"]
            
        target_ip = args[0]
        target = None
        port = int(args[1]) if len(args) > 1 else None
        
        # Trouver la cible
        for t in self.available_targets:
            if t.ip == target_ip:
                target = t
                break
        
        if not target:
            return [f"Erreur: Cible {target_ip} non trouvée"]
            
        # Vérifier le port si spécifié
        if port and port not in target.ports:
            return [
                f"Erreur: Port {port} fermé",
                f"Ports disponibles: {', '.join(map(str, target.ports))}"
            ]
            
        # Déterminer le protocole utilisé
        protocol = self._get_protocol(port if port else target.ports[0])
        
        # Calculer le risque de détection
        detection_risk = self._calculate_detection_risk(target, protocol)
        
        # Mettre à jour l'état
        self.current_target = target
        self.update_alert_level(detection_risk)
        
        return [
            f"Connexion établie avec {target.name}",
            f"Protocol: {protocol}",
            f"Niveau de sécurité: {target.security_level.value}",
            f"Risque de détection: {detection_risk}%",
            "Utilisez 'analyze' pour scanner les vulnérabilités"
        ]

    def _get_protocol(self, port):
        """Détermine le protocole en fonction du port"""
        protocols = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            80: "HTTP",
            443: "HTTPS",
            445: "SMB",
            1433: "MSSQL",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            8080: "HTTP-ALT",
            8443: "HTTPS-ALT",
            9000: "API"
        }
        return protocols.get(port, "UNKNOWN")

    def _calculate_detection_risk(self, target, protocol):
        """Calcule le risque de détection lors de la connexion"""
        base_risk = 10  # Risque de base
        
        # Facteurs de risque selon le protocole
        protocol_risk = {
            "FTP": 15,
            "Telnet": 20,
            "HTTP": 5,
            "HTTPS": 2,
            "SSH": 3,
            "RDP": 15,
            "UNKNOWN": 25
        }
        
        # Calculer le risque total
        risk = base_risk + protocol_risk.get(protocol, 10)
        
        # Ajuster selon le niveau de sécurité
        security_multiplier = {
            SecurityLevel.LOW: 0.8,
            SecurityLevel.MEDIUM: 1.0,
            SecurityLevel.HIGH: 1.3,
            SecurityLevel.EXTREME: 1.6
        }
        risk *= security_multiplier.get(target.security_level, 1.0)
        
        # Réduire le risque si des outils de furtivité sont utilisés
        if "vpn" in self.player_data.get("tools", []):
            risk *= 0.7
            
        # Appliquer les bonus de faction pour la détection
        faction_bonus = self.apply_faction_bonus("detection")
        risk *= faction_bonus
        
        return min(int(risk), 100)  # Plafonner à 100%

    def cmd_crack(self, args):
        """Tente de craquer la sécurité de la cible"""
        if not self.current_target:
            return ["Erreur: Aucune cible connectée"]
            
        if self.systeme_compromis:
            return ["Système déjà compromis"]
            
        # Calcul des chances de succès
        base_chance = 0.7  # 70% de base
        security_penalty = self.current_target.security_level.value * 0.1
        tool_bonus = self.get_tool_bonus("crack")
        
        final_chance = base_chance - security_penalty + tool_bonus
        
        if random.random() < final_chance:
            self.systeme_compromis = True
            self.update_alert_level(20)
            return [
                "Cracking réussi !",
                "Système compromis",
                "Utilisez 'help' pour voir les commandes disponibles"
            ]
        else:
            self.update_alert_level(30)  # Échec augmente plus l'alerte
            return [
                "Échec du cracking",
                "La sécurité a été alertée",
                "Essayez une autre approche ou changez de cible"
            ]

    def cmd_analyze(self, args):
        """Analyse la cible actuelle en détail"""
        if not self.current_target:
            return ["Erreur: Aucune cible connectée"]
            
        # Analyse de base
        results = [
            f"=== Analyse de {self.current_target.name} ===",
            f"Type: {self.current_target.type.value}",
            f"Niveau de sécurité: {self.current_target.security_level.value}",
            "",
            "=== Ports et Services ===",
        ]
        
        # Analyse des ports
        for port in self.current_target.ports:
            protocol = self._get_protocol(port)
            risk = self._calculate_detection_risk(self.current_target, protocol)
            results.append(f"Port {port} ({protocol}) - Risque: {risk}%")
        
        # Analyse des vulnérabilités
        results.extend([
            "",
            "=== Vulnérabilités détectées ===",
        ])
        
        vuln_descriptions = {
            "SQL Injection": "Permet d'extraire des données de la base",
            "Weak Password": "Authentification faible, facilement contournable",
            "Default Password": "Mots de passe par défaut non changés",
            "Zero Day Exploit": "Vulnérabilité critique non corrigée",
            "Memory Leak": "Fuite de mémoire exploitable",
            "SCADA Exploit": "Vulnérabilité dans le système de contrôle",
            "RDP Exploit": "Accès distant compromis",
            "Service Misconfiguration": "Services mal configurés",
            "Container Escape": "Isolation des conteneurs compromise",
            "API Misconfiguration": "API mal sécurisée",
            "Backup System Flaw": "Système de backup vulnérable",
            "Admin Access Exploit": "Accès administrateur compromis",
            "SMB Exploit": "Partage de fichiers vulnérable",
            "Weak Backup Protocol": "Protocole de sauvegarde non sécurisé",
            "SNMP Exploit": "Protocole de surveillance compromis",
            "Control System Bypass": "Contournement du système de contrôle"
        }
        
        for vuln in self.current_target.vulnerabilities:
            results.append(f"- {vuln}")
            if vuln in vuln_descriptions:
                results.append(f"  Description: {vuln_descriptions[vuln]}")
        
        # Analyse des systèmes de sécurité
        results.extend([
            "",
            "=== Systèmes de sécurité ===",
        ])
        
        security_descriptions = {
            "firewall": "Pare-feu réseau",
            "ids": "Système de détection d'intrusion",
            "encryption": "Chiffrement des données"
        }
        
        for sys, active in self.current_target.security_systems.items():
            if sys in security_descriptions:
                status = "✓ Actif" if active else "✗ Inactif"
                results.append(f"{security_descriptions[sys]}: {status}")
        
        # Analyse des données disponibles
        if self.systeme_compromis:
            results.extend([
                "",
                "=== Données disponibles ===",
                f"Valeur totale estimée: {self.current_target.get_total_data_value()}¢",
                "",
                "Bases de données:",
                *[f"- {db}" for db in self.current_target.get_available_databases()],
                "",
                "Fichiers:",
                *[f"- {f}" for f in self.current_target.get_available_files()]
            ])
        
        # Augmenter légèrement le niveau d'alerte
        self.update_alert_level(5)  # Analyse discrète
        
        return results

    def get_tool_bonus(self, tool_type):
        """Calcule le bonus donné par les outils"""
        tools = self.player_data.get("tools", [])
        bonus = 1.0
        
        if tool_type == "stealth":
            if "vpn" in tools:
                bonus += 0.3  # -30% de détection
            if "cleaner" in tools:
                bonus += 0.2  # -20% de détection supplémentaire
                
        elif tool_type == "hack":
            if "rootkit" in tools:
                bonus += 0.4  # +40% de chance de succès
                
        # Appliquer les bonus de faction
        faction_bonus = self.apply_faction_bonus(tool_type)
        bonus *= faction_bonus
                
        return bonus

    def update_alert_level(self, amount):
        """Met à jour le niveau d'alerte avec les bonus de furtivité"""
        stealth_bonus = self.get_tool_bonus("stealth")
        actual_amount = amount * (1 / stealth_bonus)  # Réduction de l'alerte selon les outils
        self.alert_level = max(0, min(100, self.alert_level + actual_amount))
        
        if self.alert_level >= 80 and not self.detected:
            self.detected = True
            self.terminal.historique.append("! ALERTE ! Intrusion détectée !")
            self.handle_detection()

    def cmd_help(self, args):
        """Affiche l'aide des commandes disponibles"""
        commands = {
            'scan': 'Recherche des cibles',
            'connect': 'Se connecte à une cible',
            'crack': 'Tente de craquer la sécurité',
            'inject': 'Injecte un payload',
            'exploit': 'Exploite une vulnérabilité',
            'exfiltrate': 'Vole des données',
            'ransom': 'Gère les ransomwares',
            'botnet': 'Gère le botnet',
            'stealth': 'Actions furtives',
            'market': 'Accède au marché noir',
            'status': 'État de la mission',
            'mission': 'Détails des objectifs'
        }
        
        if not args:
            return ["Commandes disponibles:", *[f"{cmd} : {desc}" for cmd, desc in commands.items()]]
        elif args[0] in commands:
            return [f"Usage: {args[0]} - {commands[args[0]]}"]
        return ["Commande inconnue"]

    def cmd_status(self, args):
        """Affiche l'état actuel de la mission"""
        return [
            f"Niveau d'alerte: {self.alert_level}%",
            f"Détecté: {'Oui' if self.detected else 'Non'}",
            f"Système compromis: {'Oui' if self.systeme_compromis else 'Non'}",
            f"Données volées: {len(self.donnees_volees)}",
            f"Temps restant: {int((self.mission_duration - (time.time() - self.mission_start_time))/60)}min"
        ]

    def cmd_exfiltrate(self, args):
        """Exfiltre des données de la cible"""
        if not self.systeme_compromis:
            return ["Erreur: Système non compromis"]
            
        if not args:
            return [
                "Usage: exfiltrate <type> <nom>",
                "Types disponibles:",
                "- file     : Fichier spécifique",
                "- database : Base de données",
                "- all      : Toutes les données"
            ]
            
        data_type = args[0]
        if data_type == "all":
            total_value = 0
            # Exfiltrer les fichiers
            for name, data in self.current_target.files.items():
                if not data["encrypted"]:
                    self.donnees_volees.append(("file", (data["value"], name)))
                    total_value += data["value"]
            
            # Exfiltrer les bases de données
            for name, data in self.current_target.databases.items():
                if not data["encrypted"]:
                    self.donnees_volees.append(("database", (data["value"], name)))
                    total_value += data["value"]
                    
            self.update_alert_level(50)
        return [
                "Exfiltration massive en cours...",
                f"Données volées: {len(self.donnees_volees)}",
                f"Valeur totale: {total_value}¢"
            ]
            
        if len(args) < 2:
            return ["Erreur: Nom de la donnée requis"]
            
        name = args[1]
        if data_type == "file":
            if name not in self.current_target.files:
                return ["Fichier non trouvé"]
                
            file_data = self.current_target.files[name]
            if file_data["encrypted"]:
                return ["Erreur: Fichier chiffré"]
                
            self.donnees_volees.append(("file", (file_data["value"], name)))
            self.update_alert_level(20)
            return [
                f"Exfiltration de {name}",
                f"Taille: {file_data['size']}",
                f"Valeur: {file_data['value']}¢"
            ]
            
        elif data_type == "database":
            if name not in self.current_target.databases:
                return ["Base de données non trouvée"]
                
            db_data = self.current_target.databases[name]
            if db_data["encrypted"]:
                return ["Erreur: Base de données chiffrée"]
                
            self.donnees_volees.append(("database", (db_data["value"], name)))
            self.update_alert_level(30)
            return [
                f"Exfiltration de {name}",
                f"Taille: {db_data['size']}",
                f"Valeur: {db_data['value']}¢"
            ]
            
        return ["Type de donnée invalide"]

    def handle_detection(self):
        """Gère la détection de l'intrusion"""
        self.terminal.historique.extend([
            "! SYSTÈME DE SÉCURITÉ ACTIVÉ !",
            "Traçage de la connexion en cours...",
            "Recommandation: Terminer la mission"
        ])
        
        # 50% de chance de terminer la mission si détecté
        if random.random() < 0.5:
            self.is_running = False
            self.terminal.historique.append("Connexion terminée par la cible")

    def cmd_market(self, args):
        """Gère les transactions sur le marché noir"""
        if not args:
            return [
                "Usage: market <action> [item]",
                "Actions disponibles:",
                "- buy   : Acheter un item",
                "- sell  : Vendre des données",
                "- list  : Liste des items disponibles",
                "- price : Prix des données"
            ]
        
        action = args[0]
        if action == "list":
            return [
                "=== Marché Noir ===",
                "Outils disponibles:",
                "- decryptor : Décryptage (2000¢)",
                "- vpn       : Protection (1500¢)",
                "- rootkit   : Exploitation (3000¢)",
                "- cleaner   : Nettoyage (1000¢)",
                "",
                "Hardware disponible:",
                "- cpu_upgrade    : Processeur amélioré (5000¢)",
                "- ram_upgrade    : Mémoire augmentée (4000¢)",
                "- network_card   : Carte réseau pro (3500¢)",
                "- cooling_system : Système de refroidissement (2500¢)"
            ]
            
        elif action == "buy":
            if len(args) < 2:
                return ["Usage: market buy <item>"]
            return self.cmd_download([args[1]])
            
        elif action == "sell":
            if not self.donnees_volees:
                return ["Aucune donnée à vendre"]
                
            total_value = 0
            for data_type, (value, name) in self.donnees_volees:
                total_value += value
            
            self.player_data["credits"] += total_value
            sold_data = len(self.donnees_volees)
            self.donnees_volees = []
            
            return [
                f"Données vendues: {sold_data}",
                f"Valeur totale: {total_value}¢",
                f"Nouveau solde: {self.player_data['credits']}¢"
            ]
            
        elif action == "price":
            return [
                "Prix des données:",
                "- Données personnelles : 100-500¢",
                "- Données financières  : 500-2000¢",
                "- Secrets industriels  : 2000-5000¢",
                "- Données de recherche : 3000-8000¢"
            ]
            
        return ["Action invalide"]

    def cmd_botnet(self, args):
        """Gère le botnet"""
        if not args:
            return [
                "Usage: botnet <action>",
                "Actions disponibles:",
                "- add     : Ajoute la cible actuelle au botnet",
                "- list    : Liste les machines du botnet",
                "- attack  : Lance une attaque DDoS",
                "- mine    : Lance le minage de crypto",
                "- status  : État du botnet"
            ]
            
        action = args[0]
        if action == "add":
            if not self.systeme_compromis:
                return ["Erreur: Système non compromis"]
                
            if self.current_target.id in [t.id for t in self.available_targets if t in self.botnet_targets]:
                return ["Cette machine fait déjà partie du botnet"]
                
            self.botnet_size += 1
            self.botnet_targets.append(self.current_target)
            self.update_alert_level(20)
            return [f"Machine ajoutée au botnet", f"Taille actuelle: {self.botnet_size}"]
            
        elif action == "list":
            if self.botnet_size == 0:
                return ["Botnet vide"]
            return [
                "Machines dans le botnet:",
                *[f"- {t.name} ({t.ip})" for t in self.botnet_targets]
            ]
            
        elif action == "attack":
            if self.botnet_size < 3:
                return ["Erreur: Minimum 3 machines requises"]
            damage = self.botnet_size * 100
            self.update_alert_level(40)
            return [f"Attaque DDoS lancée", f"Dommages: {damage}"]
            
        elif action == "mine":
            if self.botnet_size == 0:
                return ["Erreur: Botnet vide"]
            credits = self.botnet_size * 50
            self.player_data["credits"] += credits
            self.update_alert_level(15)
            return [f"Minage en cours...", f"Gains: {credits}¢"]
            
        elif action == "status":
            return [
                f"Taille du botnet: {self.botnet_size}",
                f"Puissance: {self.botnet_size * 100}",
                f"Revenu/min: {self.botnet_size * 50}¢"
            ]
            
        return ["Action invalide"]

    def cmd_ransom(self, args):
        """Gère les ransomwares"""
        if not args:
            return [
                "Usage: ransom <action> [amount]",
                "Actions disponibles:",
                "- encrypt : Chiffre le système",
                "- demand  : Demande une rançon",
                "- status  : Vérifie le paiement",
                "- decrypt : Déchiffre le système (après paiement)"
            ]
            
        action = args[0]
        if action == "encrypt":
            if not self.systeme_compromis:
                return ["Erreur: Système non compromis"]
                
            target_id = self.current_target.id
            if target_id in self.encrypted_systems:
                return ["Système déjà chiffré"]
                
            self.encrypted_systems[target_id] = {
                "amount": 0,
                "paid": False,
                "encrypt_time": time.time(),
                "payment_deadline": None,
                "decrypted": False
            }
            self.update_alert_level(40)
            return ["Système chiffré avec succès"]
            
        elif action == "demand":
            if len(args) < 2:
                return ["Usage: ransom demand <amount>"]
                
            try:
                amount = int(args[1])
                if amount < 100:
                    return ["Erreur: Montant minimum 100¢"]
                    
                target_id = self.current_target.id
                if target_id not in self.encrypted_systems:
                    return ["Erreur: Système non chiffré"]
                    
                if self.encrypted_systems[target_id]["amount"] > 0:
                    return ["Une demande de rançon existe déjà"]
                    
                payment_deadline = time.time() + 300  # 5 minutes
                self.encrypted_systems[target_id].update({
                    "amount": amount,
                    "payment_deadline": payment_deadline
                })
                
                return [
                    f"Demande de rançon envoyée: {amount}¢",
                    "Message: 'Vos fichiers ont été chiffrés.'",
                    f"Délai de paiement: 5 minutes",
                    "Utilisez 'ransom status' pour vérifier l'état du paiement"
                ]
            except ValueError:
                return ["Erreur: Montant invalide"]
                
        elif action == "status":
            if not self.current_target:
                return ["Erreur: Aucune cible connectée"]
                
            target_id = self.current_target.id
            if target_id not in self.encrypted_systems:
                return ["Aucun ransomware actif sur cette cible"]
                
            ransom_info = self.encrypted_systems[target_id]
            
            # Vérifier si le paiement a été effectué
            if ransom_info["paid"]:
                return [
                    "État: PAYÉ",
                    f"Montant reçu: {ransom_info['amount']}¢",
                    "Utilisez 'ransom decrypt' pour déchiffrer"
                ]
                
            # Vérifier si le délai est dépassé
            if ransom_info["payment_deadline"]:
                time_left = ransom_info["payment_deadline"] - time.time()
                if time_left <= 0:
                    # Simuler une chance de paiement basée sur le montant
                    payment_chance = min(0.7, ransom_info["amount"] / 10000)  # Max 70% de chance
                    if random.random() < payment_chance:
                        ransom_info["paid"] = True
                        self.total_ransom += ransom_info["amount"]
                        self.player_data["stats"]["ransoms_collected"] = \
                            self.player_data["stats"].get("ransoms_collected", 0) + ransom_info["amount"]
                        return [
                            "! Paiement reçu !",
                            f"Montant: {ransom_info['amount']}¢",
                            "Utilisez 'ransom decrypt' pour déchiffrer"
                        ]
                    else:
                        return ["Délai expiré - Paiement refusé"]
                else:
                    return [
                        "État: EN ATTENTE",
                        f"Montant demandé: {ransom_info['amount']}¢",
                        f"Temps restant: {int(time_left)}s"
                    ]
            return ["Aucune demande de rançon active"]
            
        elif action == "decrypt":
            if not self.current_target:
                return ["Erreur: Aucune cible connectée"]
                
            target_id = self.current_target.id
            if target_id not in self.encrypted_systems:
                return ["Système non chiffré"]
                
            ransom_info = self.encrypted_systems[target_id]
            if not ransom_info["paid"]:
                return ["Erreur: Rançon non payée"]
                
            if ransom_info["decrypted"]:
                return ["Système déjà déchiffré"]
                
            # Vérifier si l'outil de déchiffrement est disponible
            if not self.has_decryption_tool():
                return ["Erreur: Outil de déchiffrement requis"]
                
            # Déchiffrer le système
            ransom_info["decrypted"] = True
            self.update_alert_level(10)
            
            return [
                "Déchiffrement en cours...",
                "Système restauré avec succès",
                "Opération terminée"
            ]
            
        return ["Action invalide"]

    def cmd_clear(self, args):
        """Efface l'écran du terminal"""
        self.terminal.historique = []
        return []

    def cmd_ls(self, args):
        """Liste les fichiers du système"""
        if not self.systeme_compromis:
            return ["Accès refusé: système non compromis"]
            
        if not self.current_target:
            return ["Erreur: Aucune cible connectée"]

        results = [
            "Bases de données disponibles:",
            *self.current_target.get_available_databases(),
            "",
            "Fichiers disponibles:",
            *self.current_target.get_available_files()
        ]
        
        return results

    def cmd_tools(self, args):
        """Liste les outils disponibles et leurs effets"""
        tools = self.player_data.get("tools", [])
        if not tools:
            return ["Aucun outil disponible"]
        
        tool_descriptions = {
            "decryptor": "Permet de déchiffrer les fichiers et bases de données cryptés",
            "vpn": "Réduit la détection de 30%",
            "rootkit": "Augmente les chances de hack de 40%",
            "cleaner": "Réduit la détection de 20% supplémentaire"
        }
        
        results = ["=== Outils actifs ==="]
        for tool in tools:
            durability = self.tool_durability.get(tool, 0)
            results.extend([
                f"- {tool.upper()}:",
                f"  {tool_descriptions.get(tool, 'Pas de description')}",
                f"  État: {durability}%",
                ""
            ])
            
        # Afficher les bonus actifs
        results.extend([
            "=== Bonus actifs ===",
            f"Furtivité: x{self.get_tool_bonus('stealth'):.1f}",
            f"Hacking: x{self.get_tool_bonus('hack'):.1f}"
        ])
        
        return results

    def cmd_stats(self, args):
        """Affiche les statistiques détaillées du joueur"""
        stats = self.player_data["stats"]
        faction_desc = FactionBonus.get_faction_description(self.player_data["faction"])
        
        results = [
            "=== Informations du Joueur ===",
            f"Niveau: {self.player_data['level']}",
            f"Faction: {self.player_data['faction'].value}",
            f"Spécialité: {faction_desc['specialite']}",
            "",
            "=== Statistiques Générales ===",
            f"Crédits: {self.player_data['credits']}¢",
            f"Missions complétées: {stats.get('missions_completed', 0)}",
            f"Gains totaux: {stats.get('total_earnings', 0)}¢",
            "",
            "=== Performance ===",
            f"Hacks réussis: {stats.get('successful_hacks', 0)}",
            f"Missions furtives: {stats.get('stealth_missions', 0)}",
            f"Plus grand botnet: {stats.get('largest_botnet', 0)} machines",
            f"Rançons collectées: {stats.get('total_ransom', 0)}¢",
            f"Valeur des données volées: {stats.get('data_stolen_value', 0)}¢",
            "",
            "=== Hardware ===",
            f"CPU: Niveau {self.hardware_stats['cpu']['level']} (Bonus: +{int(self.hardware_stats['cpu']['bonus'] * 100)}%)",
            f"RAM: Niveau {self.hardware_stats['ram']['level']} (Bonus: +{int(self.hardware_stats['ram']['bonus'] * 100)}%)",
            f"Réseau: Niveau {self.hardware_stats['network']['level']} (Bonus: +{int(self.hardware_stats['network']['bonus'] * 100)}%)",
            f"Refroidissement: Niveau {self.hardware_stats['cooling']['level']} (Bonus: +{int(self.hardware_stats['cooling']['bonus'] * 100)}%)",
            "",
            "=== Bonus Actifs ==="
        ]
        
        # Ajouter les bonus de faction
        results.extend(faction_desc["bonus"])
        
        # Ajouter les bonus temporaires actifs
        current_time = time.time()
        active_temp_bonuses = []
        for bonus_type, bonuses in self.active_bonuses.items():
            for value, end_time in bonuses:
                if end_time > current_time:
                    remaining = int((end_time - current_time) / 60)  # Minutes restantes
                    active_temp_bonuses.append(
                        f"- {bonus_type.capitalize()}: +{int(value * 100)}% ({remaining}min restantes)"
                    )
        
        if active_temp_bonuses:
            results.extend(["", "=== Bonus Temporaires ===", *active_temp_bonuses])
            
        # Ajouter les outils disponibles
        tools = self.player_data.get("tools", [])
        if tools:
            results.extend([
                "",
                "=== Outils ===",
                *[f"- {tool.upper()}: {self.tool_durability.get(tool, 0)}% durabilité" 
                  for tool in tools]
            ])
            
        return results

    def cmd_exit(self, args):
        """Quitte la mission en cours"""
        self.is_running = False
        return ["Déconnexion..."]

    def check_mission_objectives(self):
        """Vérifie l'état des objectifs de la mission"""
        mission_type = self.mission.type
        
        # Objectifs principaux
        if mission_type == MissionType.INFILTRATION:
            self.objectifs_completes[0] = self.systeme_compromis
            self.objectifs_completes[1] = len(self.donnees_volees) > 0
            self.objectifs_completes[2] = self.alert_level < 50
            
        elif mission_type == MissionType.DATA_THEFT:
            # Calculer la valeur totale des données volées
            total_value = sum(value for _, (value, _) in self.donnees_volees)
            self.objectifs_completes[0] = self.systeme_compromis
            self.objectifs_completes[1] = total_value >= 2000  # Seuil minimum
            self.objectifs_completes[2] = not self.detected  # Non détecté
            
        elif mission_type == MissionType.RANSOMWARE:
            total_ransom = sum(sys["amount"] for sys in self.encrypted_systems.values() if sys["paid"])
            self.objectifs_completes[0] = any(sys["paid"] for sys in self.encrypted_systems.values())
            self.objectifs_completes[1] = total_ransom >= 3000  # Seuil minimum
            self.objectifs_completes[2] = len(self.encrypted_systems) >= 2  # Au moins 2 systèmes
            
        elif mission_type == MissionType.BOTNET:
            self.objectifs_completes[0] = self.botnet_size >= 5
            self.objectifs_completes[1] = self.alert_level < 80
            self.objectifs_completes[2] = any(self.use_tool("miner", "intensive") for _ in range(3))
            
        elif mission_type == MissionType.SABOTAGE:
            # Vérifier si les systèmes critiques ont été compromis
            critical_systems = ["IND_001"]  # IDs des systèmes critiques
            compromised = [t.id for t in self.available_targets if t.id in critical_systems and self.systeme_compromis]
            self.objectifs_completes[0] = len(compromised) > 0
            self.objectifs_completes[1] = self.alert_level < 70
            self.objectifs_completes[2] = any(sys["modified"] for sys in self.current_target.security_systems.values() if isinstance(sys, dict))

    def check_random_events(self):
        """Gère les événements aléatoires pendant la mission"""
        if random.random() < 0.05:  # 5% de chance par vérification
            # Événements de base
            base_events = [
                ("Alerte de sécurité", "Scan de sécurité détecté...", 15),
                ("Maintenance", "Maintenance système en cours...", -10),
                ("Erreur réseau", "Instabilité réseau détectée...", 0)
            ]
            
            # Événements spécifiques selon le type de mission
            mission_events = {
                MissionType.INFILTRATION: [
                    ("Changement de mot de passe", "Les credentials ont été modifiés...", 20),
                    ("Mise à jour", "Mise à jour de sécurité en cours...", 25),
                    ("Audit", "Audit de sécurité en cours...", 30)
                ],
                MissionType.DATA_THEFT: [
                    ("Backup", "Sauvegarde des données en cours...", -5),
                    ("Archivage", "Compression des données...", -15),
                    ("Transfert", "Transfert de données détecté...", 10)
                ],
                MissionType.RANSOMWARE: [
                    ("Anti-virus", "Scan anti-virus en cours...", 20),
                    ("Backup", "Sauvegarde système programmée...", 25),
                    ("Restauration", "Point de restauration créé...", 15)
                ],
                MissionType.BOTNET: [
                    ("Maintenance réseau", "Vérification des connexions...", 15),
                    ("Mise à jour", "Mise à jour des firewalls...", 20),
                    ("Scan réseau", "Recherche d'activités suspectes...", 25)
                ],
                MissionType.SABOTAGE: [
                    ("Vérification système", "Diagnostic en cours...", 20),
                    ("Maintenance", "Maintenance préventive...", 15),
                    ("Supervision", "Contrôle des paramètres...", 25)
                ]
            }
            
            # Événements spécifiques aux factions
            faction_events = {
                Faction.SPECTRES: [
                    ("Faille de sécurité", "Une faille a été détectée dans le système...", -20),
                    ("Route alternative", "Route réseau alternative découverte...", -15),
                    ("Zone d'ombre", "Zone non surveillée détectée...", -25)
                ],
                Faction.FORGEURS: [
                    ("Vulnérabilité", "Nouvelle vulnérabilité découverte...", -15),
                    ("Exploit", "Exploit zero-day disponible...", -20),
                    ("Faille système", "Faille critique détectée...", -25)
                ],
                Faction.VEILLEURS: [
                    ("Analyse avancée", "Analyse approfondie en cours...", -10),
                    ("Contre-mesure", "Contre-mesure développée...", -20),
                    ("Optimisation", "Optimisation du système...", -15)
                ]
            }
            
            # Sélectionner les événements possibles
            possible_events = base_events + mission_events.get(self.mission.type, [])
            
            # Ajouter les événements de faction avec une plus grande probabilité
            if random.random() < 0.3:  # 30% de chance d'avoir un événement de faction
                faction_specific = faction_events.get(self.player_data["faction"], [])
                if faction_specific:
                    possible_events.extend(faction_specific)
            
            # Sélectionner un événement au hasard
            event = random.choice(possible_events)
            
            # Appliquer des modificateurs selon l'état du système
            alert_modifier = 1.0
            if self.systeme_compromis:
                alert_modifier *= 1.2  # +20% d'alerte si système compromis
            if len(self.donnees_volees) > 0:
                alert_modifier *= 1.1  # +10% d'alerte si données volées
            if any(sys["paid"] for sys in self.encrypted_systems.values()):
                alert_modifier *= 1.3  # +30% d'alerte si rançon payée
            
            # Appliquer les bonus de faction pour les événements
            if event in faction_events.get(self.player_data["faction"], []):
                alert_modifier *= 0.7  # -30% d'impact pour les événements de faction
            
            # Appliquer l'événement
            self.terminal.historique.append(f"! {event[0]} !")
            self.terminal.historique.append(event[1])
            self.update_alert_level(event[2] * alert_modifier)
            
            # Effets spéciaux selon le type d'événement
            if "faille" in event[0].lower() or "vulnérabilité" in event[0].lower():
                self.terminal.historique.append("Bonus temporaire de hacking activé")
                self.active_bonuses["hack"].append((0.2, time.time() + 300))  # +20% pendant 5min
            elif "route" in event[0].lower() or "zone" in event[0].lower():
                self.terminal.historique.append("Bonus temporaire de furtivité activé")
                self.active_bonuses["stealth"].append((0.2, time.time() + 300))  # +20% pendant 5min
            elif "analyse" in event[0].lower() or "optimisation" in event[0].lower():
                self.terminal.historique.append("Bonus temporaire d'analyse activé")
                self.active_bonuses["detection"].append((0.2, time.time() + 300))  # +20% pendant 5min

    def check_secondary_objectives(self):
        """Vérifie l'état des objectifs secondaires"""
        if not hasattr(self.mission, "objectifs_secondaires"):
            return []
            
        results = []
        for i, obj in enumerate(self.mission.objectifs_secondaires):
            completed = False
            
            # Vérifier les différents types d'objectifs
            if "non détecté" in obj.lower():
                completed = not self.detected
            elif "temps" in obj.lower():
                completed = (time.time() - self.mission_start_time) < (self.mission_duration * 0.75)
            elif "botnet" in obj.lower():
                completed = self.botnet_size >= 3
            elif "données" in obj.lower():
                total_value = sum(value for _, (value, _) in self.donnees_volees)
                completed = total_value >= 5000
            elif "furtif" in obj.lower():
                completed = self.alert_level < 30
            elif "ransomware" in obj.lower():
                completed = len(self.encrypted_systems) >= 2
            elif "modification" in obj.lower():
                completed = any(sys.get("modified", False) for sys in self.current_target.security_systems.values() if isinstance(sys, dict))
            
            results.append((obj, completed))
            
        return results

    def cmd_objectives(self, args):
        """Affiche l'état des objectifs principaux et secondaires"""
        results = [
            "=== Objectifs Principaux ===",
            *[f"{'[X]' if done else '[ ]'} {obj}" 
              for obj, done in zip(self.mission.objectifs, self.objectifs_completes)],
            ""
        ]
        
        # Ajouter les objectifs secondaires s'ils existent
        secondary = self.check_secondary_objectives()
        if secondary:
            results.extend([
                "=== Objectifs Secondaires ===",
                *[f"{'[X]' if done else '[ ]'} {obj}" 
                  for obj, done in secondary]
            ])
            
        return results

    def afficher(self):
        """Affiche et met à jour l'état de la mission"""
        try:
            # Vérifier les événements périodiques
            self.check_periodic_events()
            
            # Vérifier les effets des payloads
            self.check_payload_effects()
            
            # Sauvegarde automatique toutes les 5 minutes
            current_time = time.time()
            if current_time - self.last_save_time > 300:
                self.save_mission_state()
                self.last_save_time = current_time
            
            # Vérifier les objectifs et la complétion
            self.check_mission_objectives()
            if self.check_mission_completion():
                self.is_running = False
            
            # Vérifier le temps restant
            if current_time - self.mission_start_time > self.mission_duration:
                self.is_running = False
                self.terminal.historique.append("Temps écoulé - Mission terminée")
            
            # Mettre à jour l'affichage
            self.terminal.draw(self.ecran)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'affichage : {e}") 

    def cmd_download(self, args):
        """Télécharge un fichier ou une base de données"""
        if not args:
            return ["Usage: download <filename>"]
            
        if not self.systeme_compromis:
            return ["Erreur: Système non compromis"]
            
        if not self.current_target:
            return ["Erreur: Aucune cible connectée"]
            
        filename = args[0]
        
        # Vérifier dans les fichiers
        if filename in self.current_target.files:
            file_data = self.current_target.files[filename]
            if file_data["encrypted"] and not self.has_decryption_tool():
                return ["Erreur: Fichier chiffré - Outil de décryptage requis"]
                
            self.donnees_volees.append(("file", (file_data["value"], filename)))
            self.update_alert_level(15)
            return [
                f"Téléchargement de {filename}",
                f"Taille: {file_data['size']}",
                "Téléchargement terminé"
            ]
            
        # Vérifier dans les bases de données
        if filename in self.current_target.databases:
            db_data = self.current_target.databases[filename]
            if db_data["encrypted"] and not self.has_decryption_tool():
                return ["Erreur: Base de données chiffrée - Outil de décryptage requis"]
                
            self.donnees_volees.append(("database", (db_data["value"], filename)))
            self.update_alert_level(25)
            return [
                f"Extraction de {filename}",
                f"Taille: {db_data['size']}",
                "Extraction terminée"
            ]
            
        return [f"Fichier non trouvé: {filename}"]

    def has_decryption_tool(self):
        """Vérifie si le joueur possède l'outil de décryptage"""
        return "decryptor" in self.player_data.get("tools", [])

    def use_tool(self, tool_name, usage_type="normal"):
        """Gère l'utilisation et l'usure des outils"""
        if tool_name not in self.tool_durability:
            return False
            
        # Réduction de durabilité selon le type d'usage
        wear_rates = {
            "normal": 2,
            "intensive": 5,
            "careful": 1
        }
        
        self.tool_durability[tool_name] -= wear_rates.get(usage_type, 2)
        
        # Vérifier si l'outil est encore utilisable
        if self.tool_durability[tool_name] <= 0:
            self.player_data["tools"].remove(tool_name)
            del self.tool_durability[tool_name]
            self.terminal.historique.append(f"! Attention ! {tool_name} est hors service")

    def cmd_repair(self, args):
        """Répare les outils endommagés"""
        if not args:
            return ["Usage: repair <tool>"]
            
        tool = args[0].lower()
        if tool not in self.tool_durability:
            return ["Outil non trouvé"]
            
        repair_cost = int((100 - self.tool_durability[tool]) * 10)  # 10 crédits par % de réparation
        
        if self.player_data["credits"] < repair_cost:
            return [f"Crédits insuffisants ({repair_cost}¢ requis)"]
            
        self.player_data["credits"] -= repair_cost
        self.tool_durability[tool] = 100
        
        return [
            f"Réparation de {tool} effectuée",
            f"Coût: {repair_cost}¢",
            f"Crédits restants: {self.player_data['credits']}¢"
        ]

    def save_mission_state(self):
        """Sauvegarder l'état actuel de la mission"""
        try:
            mission_state = {
                "mission_id": self.mission.id,
                "alert_level": self.alert_level,
                "detected": self.detected,
                "systeme_compromis": self.systeme_compromis,
                "donnees_volees": self.donnees_volees,
                "botnet_size": self.botnet_size,
                "encrypted_systems": self.encrypted_systems,
                "objectifs_completes": self.objectifs_completes,
                "current_target": self.current_target.id if self.current_target else None,
                "tool_durability": self.tool_durability,
                "mission_start_time": self.mission_start_time
            }
            
            # Mettre à jour les statistiques du joueur
            self.player_data["stats"].update({
                "alert_level": self.alert_level,
                "systems_compromised": len([t for t in self.available_targets if self.systeme_compromis]),
                "data_stolen": len(self.donnees_volees),
                "botnet_size": self.botnet_size
            })
            
            # Sauvegarder via le save_manager
            self.save_manager.save_mission_state(mission_state)
            self.save_manager.save_player_data(
                self.player_data["faction"],
                self.player_data["level"],
                self.player_data["completed_missions"],
                self.player_data["stats"],
                self.player_data["hardware"],
                self.player_data["tools"]
            )
            
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde : {e}")
            return False

    def check_payload_effects(self):
        """Vérifie et applique les effets des payloads actifs"""
        current_time = time.time()
        if current_time - self.last_payload_check < 60:  # Vérifier toutes les minutes
            return
            
        self.last_payload_check = current_time
        
        for target_id, payloads in list(self.active_payloads.items()):
            for payload_type, timestamp in list(payloads.items()):
                # Vérifier si le payload est toujours actif (24h de durée de vie)
                if current_time - timestamp > 86400:  # 24 heures
                    del self.active_payloads[target_id][payload_type]
                    if not self.active_payloads[target_id]:
                        del self.active_payloads[target_id]
                    continue
                
                effect = self.payload_effects[payload_type]
                
                # Appliquer les effets
                if payload_type == "miner":
                    self.player_data["credits"] += effect["credits_rate"]
                elif payload_type in ["keylogger", "trojan"]:
                    # Chance de voler des données
                    if random.random() < 0.3:  # 30% de chance
                        data_value = effect["data_rate"]
                        self.donnees_volees.append(
                            ("automated", (data_value, f"Données {payload_type}"))
                        )
                
                # Augmenter le niveau d'alerte
                self.update_alert_level(effect["detection_rate"] * 0.1)

    def cmd_modify(self, args):
        """Modifie les paramètres d'un système"""
        if not self.current_target:
            return ["Erreur: Aucune cible connectée"]
            
        if not self.systeme_compromis:
            return ["Erreur: Système non compromis"]
            
        if not args:
            return [
                "Usage: modify <system> <parameter> <value>",
                "Systèmes disponibles:",
                "- production : Paramètres de production",
                "- security  : Paramètres de sécurité",
                "- network   : Configuration réseau"
            ]
            
        system = args[0]
        if len(args) < 3:
            return ["Erreur: Paramètres manquants"]
            
        parameter = args[1]
        value = args[2]
        
        # Vérifier si le système existe
        if system not in self.current_target.security_systems:
            self.current_target.security_systems[system] = {
                "modified": False,
                "parameters": {}
            }
        
        # Appliquer la modification
        try:
            self.current_target.security_systems[system]["parameters"][parameter] = value
            self.current_target.security_systems[system]["modified"] = True
            
            # Augmenter l'alerte en fonction du système modifié
            alert_levels = {
                "production": 35,
                "security": 25,
                "network": 20
            }
            self.update_alert_level(alert_levels.get(system, 30))
            
            return [
                f"Modification de {system}.{parameter} = {value}",
                "Changements appliqués",
                "Attention: Ces modifications peuvent être détectées"
            ]
        except Exception as e:
            return [f"Erreur lors de la modification: {str(e)}"]

    def check_periodic_events(self):
        """Vérifie et applique les événements périodiques"""
        current_time = time.time()
        
        # Vérifier les revenus du botnet (toutes les minutes)
        if current_time - self.last_botnet_check > 60:
            self.process_botnet_income()
            self.last_botnet_check = current_time
        
        # Vérifier la durabilité des outils (toutes les 5 minutes)
        if current_time - self.last_difficulty_check > 300:
            self.check_tools_durability()
            self.last_difficulty_check = current_time
        
        # Vérifier les bonus temporaires (toutes les secondes)
        self.check_active_bonuses()
        
        # Vérifier le niveau d'alerte (toutes les 30 secondes)
        if current_time - self.last_event_check > 30:
            self.process_alert_effects()
            self.last_event_check = current_time

    def process_botnet_income(self):
        """Traite les revenus générés par le botnet"""
        if self.botnet_size > 0:
            # Calculer les revenus de base
            base_income = self.botnet_size * 50
            
            # Appliquer les bonus du hardware
            cpu_bonus = 1 + (self.hardware_stats["cpu"]["bonus"] * self.hardware_stats["cpu"]["level"])
            network_bonus = 1 + (self.hardware_stats["network"]["bonus"] * self.hardware_stats["network"]["level"])
            
            # Calculer le revenu final
            final_income = int(base_income * cpu_bonus * network_bonus)
            
            # Ajouter les crédits
            self.player_data["credits"] += final_income
            
            # Augmenter légèrement le niveau d'alerte
            self.update_alert_level(self.botnet_size * 0.5)

    def check_tools_durability(self):
        """Vérifie et met à jour la durabilité des outils"""
        for tool, durability in list(self.tool_durability.items()):
            # Réduire la durabilité en fonction de l'utilisation
            if self.systeme_compromis:
                reduction = 2  # Usure normale
                if tool == "vpn":
                    reduction = 3  # VPN s'use plus vite
                elif tool == "rootkit":
                    reduction = 4  # Rootkit s'use encore plus vite
                
                # Appliquer le bonus de cooling
                cooling_bonus = 1 - (self.hardware_stats["cooling"]["bonus"] * self.hardware_stats["cooling"]["level"])
                reduction *= cooling_bonus
                
                # Mettre à jour la durabilité
                self.tool_durability[tool] = max(0, durability - reduction)
                
                # Vérifier si l'outil est cassé
                if self.tool_durability[tool] <= 0:
                    self.player_data["tools"].remove(tool)
                    del self.tool_durability[tool]
                    self.terminal.historique.append(f"! Attention ! {tool} est hors service")

    def check_active_bonuses(self):
        """Vérifie et met à jour les bonus temporaires"""
        current_time = time.time()
        
        for bonus_type in self.active_bonuses:
            # Filtrer les bonus expirés
            active = [(value, end_time) for value, end_time in self.active_bonuses[bonus_type] if end_time > current_time]
            self.active_bonuses[bonus_type] = active

    def process_alert_effects(self):
        """Traite les effets du niveau d'alerte"""
        if self.alert_level > 0:
            # Réduction naturelle de l'alerte
            reduction = 0.5  # Réduction de base
            
            # Bonus de furtivité
            if "vpn" in self.player_data.get("tools", []):
                reduction *= 1.5
            if "cleaner" in self.player_data.get("tools", []):
                reduction *= 1.3
                
            # Appliquer la réduction
            self.alert_level = max(0, self.alert_level - reduction)
            
        # Effets selon le niveau d'alerte
        if self.alert_level >= 90:
            # Risque critique
            if random.random() < 0.1:  # 10% de chance
                self.terminal.historique.append("! ALERTE CRITIQUE ! Déconnexion imminente")
                self.is_running = False
        elif self.alert_level >= 75:
            # Haute sécurité
            if random.random() < 0.2:  # 20% de chance
                self.terminal.historique.append("! Sécurité renforcée activée !")
                self.update_alert_level(5)
        elif self.alert_level >= 50:
            # Surveillance accrue
            if random.random() < 0.15:  # 15% de chance
                self.terminal.historique.append("! Surveillance accrue détectée !")
                self.update_alert_level(2) 

    def cmd_inject(self, args):
        """Injecte un payload dans le système"""
        if not self.current_target:
            return ["Erreur: Aucune cible connectée"]
            
        if not self.systeme_compromis:
            return ["Erreur: Système non compromis"]
            
        if not args:
            return [
                "Usage: inject <payload>",
                "Payloads disponibles:",
                "- keylogger : Capture les frappes clavier",
                "- backdoor  : Installe une porte dérobée",
                "- miner     : Installe un mineur de crypto",
                "- trojan    : Installe un cheval de Troie"
            ]
            
        payload = args[0]
        valid_payloads = ["keylogger", "backdoor", "miner", "trojan"]
        
        if payload not in valid_payloads:
            return ["Payload invalide"]
            
        # Vérifier si un payload est déjà actif
        target_id = self.current_target.id
        if target_id in self.active_payloads and payload in self.active_payloads[target_id]:
            return ["Ce payload est déjà actif sur cette cible"]
            
        # Chance de succès basée sur le niveau de sécurité
        success_chance = 0.8 - (self.current_target.security_level.value * 0.1)
        if random.random() < success_chance:
            # Activer le payload
            if target_id not in self.active_payloads:
                self.active_payloads[target_id] = {}
            self.active_payloads[target_id][payload] = time.time()
            
            self.update_alert_level(15)
            return [
                f"Injection du payload {payload}...",
                "Injection réussie",
                "Payload actif"
            ]
        else:
            self.update_alert_level(30)
            return ["Échec de l'injection", "Payload détecté et bloqué"]

    def check_mission_completion(self):
        """Vérifie si la mission est terminée et attribue les récompenses"""
        # Vérifier si tous les objectifs principaux sont complétés
        if all(self.objectifs_completes):
            # Calculer le bonus basé sur les objectifs secondaires
            bonus_count = 0
            secondary_objectives = self.check_secondary_objectives()
            if secondary_objectives:
                bonus_count = sum(1 for _, completed in secondary_objectives if completed)
            bonus_multiplier = 1.0 + (bonus_count * 0.2)  # +20% par objectif secondaire
            
            # Calculer les bonus supplémentaires
            stealth_bonus = 1.5 if not self.detected else 1.0  # +50% si non détecté
            time_bonus = 1.2 if (time.time() - self.mission_start_time) < (self.mission_duration * 0.75) else 1.0  # +20% si rapide
            
            # Appliquer le bonus de faction pour ce type de mission
            faction_bonus = FactionBonus.get_mission_bonus(self.player_data["faction"], self.mission.type)
            
            # Calculer la récompense finale
            base_reward = self.mission.recompense
            final_reward = int(base_reward * bonus_multiplier * stealth_bonus * time_bonus * faction_bonus)
            
            # Mettre à jour les données du joueur
            self.player_data["credits"] += final_reward
            self.player_data["completed_missions"].append(self.mission.id)
            self.player_data["level"] += 1
            
            # Mettre à jour les statistiques
            self.player_data["stats"].update({
                "missions_completed": self.player_data["stats"].get("missions_completed", 0) + 1,
                "total_earnings": self.player_data["stats"].get("total_earnings", 0) + final_reward,
                "successful_hacks": self.player_data["stats"].get("successful_hacks", 0) + 1 if self.systeme_compromis else 0,
                "stealth_missions": self.player_data["stats"].get("stealth_missions", 0) + 1 if not self.detected else 0,
                "data_stolen_value": self.player_data["stats"].get("data_stolen_value", 0) + sum(value for _, (value, _) in self.donnees_volees),
                "largest_botnet": max(self.player_data["stats"].get("largest_botnet", 0), self.botnet_size),
                "total_ransom": self.player_data["stats"].get("total_ransom", 0) + self.total_ransom
            })
            
            # Débloquer des récompenses selon le niveau
            if self.player_data["level"] % 5 == 0:  # Tous les 5 niveaux
                self.unlock_level_rewards()
            
            # Sauvegarder l'état
            self.save_manager.save_player_data(
                self.player_data["faction"],
                self.player_data["level"],
                self.player_data["completed_missions"],
                self.player_data["stats"],
                self.player_data["hardware"],
                self.player_data["tools"]
            )
            
            # Informer le joueur
            faction_desc = FactionBonus.get_faction_description(self.player_data["faction"])
            self.terminal.historique.extend([
                "=== Mission Accomplie ! ===",
                f"Récompense de base : {base_reward}¢",
                f"Bonus furtivité : x{stealth_bonus:.1f}",
                f"Bonus temps : x{time_bonus:.1f}",
                f"Bonus objectifs secondaires : x{bonus_multiplier:.1f}",
                f"Bonus de faction : x{faction_bonus:.1f}",
                f"Récompense finale : {final_reward}¢",
                "",
                "=== Statistiques de Mission ===",
                f"Données volées : {len(self.donnees_volees)}",
                f"Niveau d'alerte final : {self.alert_level}%",
                f"Taille du botnet : {self.botnet_size}",
                f"Systèmes compromis : {len([t for t in self.available_targets if self.systeme_compromis])}",
                "",
                "=== Progression ===",
                f"Niveau atteint : {self.player_data['level']}",
                f"Missions complétées : {self.player_data['stats']['missions_completed']}",
                f"Crédits totaux : {self.player_data['credits']}¢",
                "",
                "=== Bonus de Faction ===",
                f"Faction : {self.player_data['faction'].value}",
                f"Spécialité : {faction_desc['specialite']}",
                *faction_desc['bonus']
            ])
            
            return True
        return False

    def unlock_level_rewards(self):
        """Débloque les récompenses basées sur le niveau du joueur"""
        level = self.player_data["level"]
        rewards = []
        
        # Récompenses tous les 5 niveaux
        if level % 5 == 0:
            # Débloquer un nouvel outil
            new_tool = self.get_level_tool(level)
            if new_tool:
                self.player_data["tools"].append(new_tool)
                rewards.append(f"Nouvel outil débloqué : {new_tool}")
            
            # Améliorer le hardware
            hardware_upgrade = self.get_level_hardware(level)
            if hardware_upgrade:
                hw_type, hw_bonus = hardware_upgrade
                self.player_data["hardware"][hw_type] = self.player_data["hardware"].get(hw_type, 0) + hw_bonus
                rewards.append(f"Amélioration hardware : {hw_type} +{hw_bonus}")
            
            # Bonus de crédits
            credit_bonus = level * 500
            self.player_data["credits"] += credit_bonus
            rewards.append(f"Bonus de crédits : {credit_bonus}¢")
        
        # Afficher les récompenses
        if rewards:
            self.terminal.historique.extend([
                "=== Récompenses de Niveau ===",
                *rewards
            ])
    
    def get_level_tool(self, level):
        """Retourne l'outil à débloquer pour un niveau donné"""
        tools = {
            5: "keylogger",
            10: "rootkit",
            15: "cryptolocker",
            20: "botnet_manager",
            25: "system_eraser",
            30: "network_scanner",
            35: "data_extractor",
            40: "system_analyzer",
            45: "stealth_kit",
            50: "master_toolkit"
        }
        return tools.get(level)
    
    def get_level_hardware(self, level):
        """Retourne l'amélioration hardware pour un niveau donné"""
        hardware = {
            5: ("cpu", 0.2),
            10: ("ram", 0.2),
            15: ("network", 0.2),
            20: ("cooling", 0.2),
            25: ("cpu", 0.3),
            30: ("ram", 0.3),
            35: ("network", 0.3),
            40: ("cooling", 0.3),
            45: ("cpu", 0.4),
            50: ("network", 0.4)
        }
        return hardware.get(level)

    def cmd_exploit(self, args):
        """Exploite une vulnérabilité spécifique"""
        if not self.current_target:
            return ["Erreur: Aucune cible connectée"]
            
        if not args:
            vulns = self.current_target.vulnerabilities
            return [
                "Vulnérabilités détectées:",
                *[f"- {vuln}" for vuln in vulns],
                "\nUsage: exploit <vulnerability>"
            ]
            
        vuln = " ".join(args)
        if vuln not in self.current_target.vulnerabilities:
            return ["Vulnérabilité non trouvée"]
            
        # Chance de succès basée sur les outils et le niveau de sécurité
        base_chance = 0.6
        security_penalty = self.current_target.security_level.value * 0.1
        tool_bonus = self.get_tool_bonus("exploit")
        
        final_chance = base_chance - security_penalty + tool_bonus
        
        if random.random() < final_chance:
            self.systeme_compromis = True
            self.update_alert_level(15)  # Exploit ciblé génère moins d'alerte
            
            # Ajouter des effets spéciaux selon la vulnérabilité
            if vuln == "SQL Injection":
                self.donnees_volees.append(("database", (1000, "Base de données compromise")))
            elif vuln == "Weak Password":
                self.update_alert_level(-5)
            elif vuln == "Default Password":
                self.update_alert_level(-10)
            elif vuln == "Zero Day Exploit":
                self.update_alert_level(30)
            elif vuln == "Memory Leak":
                self.player_data["credits"] += 500
            elif vuln == "SCADA Exploit":
                self.current_target.security_systems["production"] = {"modified": True}
            elif vuln == "RDP Exploit":
                self.update_alert_level(20)
            elif vuln == "Service Misconfiguration":
                self.update_alert_level(-8)
            elif vuln == "Container Escape":
                self.update_alert_level(25)
            elif vuln == "API Misconfiguration":
                self.donnees_volees.append(("api", (800, "Données API")))
            elif vuln == "Backup System Flaw":
                self.donnees_volees.append(("backup", (1200, "Données de backup")))
            elif vuln == "Admin Access Exploit":
                self.update_alert_level(35)
            elif vuln == "SMB Exploit":
                self.donnees_volees.append(("files", (600, "Fichiers partagés")))
            elif vuln == "Weak Backup Protocol":
                self.donnees_volees.append(("backup", (900, "Données de sauvegarde")))
            elif vuln == "SNMP Exploit":
                self.update_alert_level(15)
            elif vuln == "Control System Bypass":
                self.current_target.security_systems["control"] = {"modified": True}
            
            return [
                f"Exploitation de {vuln} réussie !",
                "Système compromis",
                "Utilisez 'help' pour voir les commandes disponibles"
            ]
        else:
            self.update_alert_level(25)
            return [
                "Échec de l'exploitation",
                "La sécurité a été alertée",
                "Essayez une autre vulnérabilité"
            ]

    def cmd_mission(self, args):
        """Affiche les détails et objectifs de la mission"""
        results = [
            f"=== Mission : {self.mission.titre} ===",
            f"Type: {self.mission.type.value}",
            f"Difficulté: {self.mission.difficulte}",
            f"Récompense: {self.mission.recompense}¢",
            "",
            "=== Objectifs Principaux ===",
            *[f"{'[X]' if done else '[ ]'} {obj}" 
              for obj, done in zip(self.mission.objectifs, self.objectifs_completes)]
        ]
        
        # Ajouter les objectifs secondaires s'ils existent
        secondary = self.check_secondary_objectives()
        if secondary:
            results.extend([
                "",
                "=== Objectifs Secondaires ===",
                *[f"{'[X]' if done else '[ ]'} {obj}" 
                  for obj, done in secondary]
            ])
        
        # Ajouter les informations de progression
        results.extend([
            "",
            "=== Progression ===",
            f"Temps écoulé: {int((time.time() - self.mission_start_time) / 60)}min",
            f"Temps restant: {int((self.mission_duration - (time.time() - self.mission_start_time)) / 60)}min",
            f"Niveau d'alerte: {self.alert_level}%",
            f"Détection: {'Oui' if self.detected else 'Non'}",
            "",
            "=== Statistiques ===",
            f"Données volées: {len(self.donnees_volees)}",
            f"Systèmes compromis: {len([t for t in self.available_targets if self.systeme_compromis])}",
            f"Taille du botnet: {self.botnet_size}",
            f"Rançons collectées: {self.total_ransom}¢"
        ])
        
        return results

    def cmd_stealth(self, args):
        """Gère les actions furtives"""
        if not args:
            return [
                "Usage: stealth <action>",
                "Actions disponibles:",
                "- clean : Nettoie les logs",
                "- hide  : Cache votre présence",
                "- trace : Vérifie les traces",
                "- route : Change votre route réseau"
            ]
            
        action = args[0]
        if action == "clean":
            if not self.systeme_compromis:
                return ["Erreur: Système non compromis"]
                
            # Vérifier si l'outil cleaner est disponible
            if "cleaner" not in self.player_data.get("tools", []):
                return ["Erreur: Outil cleaner requis"]
                
            # Utiliser l'outil
            self.use_tool("cleaner", "intensive")
            self.update_alert_level(-15)
            return ["Nettoyage des logs...", "Traces effacées"]
            
        elif action == "hide":
            # Calculer les chances de succès
            stealth_bonus = self.get_tool_bonus("stealth")
            hardware_bonus = 1 + (self.hardware_stats["network"]["bonus"] * self.hardware_stats["network"]["level"])
            success_chance = 0.6 * stealth_bonus * hardware_bonus
            
            if random.random() < success_chance:
                self.update_alert_level(-20)
                return [
                    "Masquage réussi",
                    "Présence dissimulée",
                    f"Niveau d'alerte réduit à {self.alert_level}%"
                ]
            else:
                self.update_alert_level(10)
                return ["Échec du masquage", "Activité suspecte détectée"]
            
        elif action == "trace":
            results = [
                f"Niveau d'alerte: {self.alert_level}%",
                f"Détection: {'Oui' if self.detected else 'Non'}",
                "",
                "Traces actives:"
            ]
            
            # Analyser les différentes sources de traces
            if self.systeme_compromis:
                results.append("- Système compromis (Risque élevé)")
            if self.donnees_volees:
                results.append("- Données exfiltrées (Risque moyen)")
            if self.botnet_size > 0:
                results.append("- Activité botnet (Risque continu)")
            if any(sys["paid"] for sys in self.encrypted_systems.values()):
                results.append("- Ransomware actif (Risque critique)")
                
            # Ajouter les bonus de furtivité actifs
            active_tools = []
            if "vpn" in self.player_data.get("tools", []):
                active_tools.append("VPN (-30% détection)")
            if "cleaner" in self.player_data.get("tools", []):
                active_tools.append("Cleaner (-20% détection)")
                
            if active_tools:
                results.extend(["", "Protections actives:", *[f"- {tool}" for tool in active_tools]])
            
            return results
            
        elif action == "route":
            if "vpn" not in self.player_data.get("tools", []):
                return ["Erreur: VPN requis"]
                
            # Utiliser l'outil
            self.use_tool("vpn", "normal")
            self.update_alert_level(-10)
            
            return [
                "Changement de route réseau...",
                "Nouvelle route établie",
                "Traces précédentes effacées"
            ]
            
        return ["Action inconnue"]

    def calculate_hardware_bonus(self, hardware_type):
        """Calcule le bonus donné par le hardware"""
        if hardware_type not in self.hardware_stats:
            return 1.0
            
        stats = self.hardware_stats[hardware_type]
        base_bonus = stats["bonus"]
        level_multiplier = stats["level"]
        
        # Calculer le bonus total
        total_bonus = 1.0 + (base_bonus * level_multiplier)
        
        # Appliquer les modificateurs de faction
        if hardware_type == "cpu" and self.player_data["faction"] == Faction.FORGEURS:
            total_bonus *= 1.2  # +20% pour les Forgeurs
        elif hardware_type == "network" and self.player_data["faction"] == Faction.SPECTRES:
            total_bonus *= 1.2  # +20% pour les Spectres
        elif hardware_type == "cooling" and self.player_data["faction"] == Faction.VEILLEURS:
            total_bonus *= 1.2  # +20% pour les Veilleurs
            
        # Appliquer les bonus temporaires actifs
        current_time = time.time()
        if hardware_type in self.active_bonuses:
            for bonus_value, end_time in self.active_bonuses[hardware_type]:
                if end_time > current_time:
                    total_bonus *= (1 + bonus_value)
                    
        return total_bonus

    def apply_faction_bonus(self, action_type):
        """Applique les bonus de faction selon le type d'action"""
        faction = self.player_data["faction"]
        bonus = 1.0
        
        if faction == Faction.SPECTRES:
            if action_type == "stealth":
                bonus = 1.3  # +30% en furtivité
            elif action_type == "detection":
                bonus = 0.8  # -20% de détection
                
        elif faction == Faction.FORGEURS:
            if action_type == "hack":
                bonus = 1.4  # +40% en hacking
            elif action_type == "exploit":
                bonus = 1.3  # +30% en exploitation
                
        elif faction == Faction.VEILLEURS:
            if action_type == "analyze":
                bonus = 1.5  # +50% en analyse
            elif action_type == "defense":
                bonus = 1.3  # +30% en défense
                
        # Appliquer les bonus de niveau
        level_bonus = 1.0 + (self.player_data["level"] * 0.02)  # +2% par niveau
        
        return bonus * level_bonus

class Target:
    def __init__(self, id, name, type, security_level, ip, vulnerabilities, ports, data_value, description, security_systems):
        self.id = id
        self.name = name
        self.type = type
        self.security_level = security_level
        self.ip = ip
        self.vulnerabilities = vulnerabilities
        self.ports = ports
        self.data_value = data_value
        self.description = description
        self.security_systems = security_systems
        
        # Initialiser les données spécifiques au type
        self._init_type_specific_data()

    def _init_type_specific_data(self):
        """Initialise les données spécifiques au type de cible"""
        if self.type == TargetType.CORPORATE:
            self.databases = {
                "users.db": {"size": "2.3GB", "value": 1500, "encrypted": True},
                "financial.db": {"size": "1.8GB", "value": 2500, "encrypted": True},
                "emails.db": {"size": "3.1GB", "value": 1000, "encrypted": False}
            }
            self.files = {
                "passwords.txt": {"size": "156KB", "value": 800, "encrypted": False},
                "contracts.pdf": {"size": "2.1GB", "value": 1200, "encrypted": True},
                "employee_data.xlsx": {"size": "250MB", "value": 1500, "encrypted": False}
            }
        elif self.type == TargetType.BANK:
            self.databases = {
                "transactions.db": {"size": "5.0GB", "value": 5000, "encrypted": True},
                "accounts.db": {"size": "3.2GB", "value": 4000, "encrypted": True},
                "audit_logs.db": {"size": "1.5GB", "value": 2000, "encrypted": True}
            }
            self.files = {
                "swift_codes.txt": {"size": "50KB", "value": 3000, "encrypted": True},
                "trading_algo.py": {"size": "1.2MB", "value": 5000, "encrypted": True}
            }
        elif self.type == TargetType.RESEARCH:
            self.databases = {
                "research_data.db": {"size": "8.5GB", "value": 5000, "encrypted": True},
                "experiments.db": {"size": "3.2GB", "value": 2500, "encrypted": True},
                "prototypes.db": {"size": "2.1GB", "value": 4000, "encrypted": True}
            }
            self.files = {
                "research_notes.pdf": {"size": "450MB", "value": 3000, "encrypted": True},
                "prototype_specs.dwg": {"size": "250MB", "value": 4000, "encrypted": True},
                "test_results.xlsx": {"size": "180MB", "value": 2000, "encrypted": False}
            }
        elif self.type == TargetType.INFRASTRUCTURE:
            self.databases = {
                "network_config.db": {"size": "1.2GB", "value": 2000, "encrypted": True},
                "monitoring.db": {"size": "4.5GB", "value": 1500, "encrypted": False},
                "security_logs.db": {"size": "3.0GB", "value": 1800, "encrypted": True}
            }
            self.files = {
                "access_codes.txt": {"size": "42KB", "value": 2500, "encrypted": True},
                "network_map.pdf": {"size": "15MB", "value": 1000, "encrypted": False},
                "security_policy.doc": {"size": "2.5MB", "value": 800, "encrypted": False}
            }
        else:  # Type par défaut
            self.databases = {
                "system.db": {"size": "1.0GB", "value": 500, "encrypted": False},
                "backup.db": {"size": "2.0GB", "value": 800, "encrypted": True}
            }
            self.files = {
                "config.txt": {"size": "128KB", "value": 200, "encrypted": False},
                "logs.txt": {"size": "500MB", "value": 300, "encrypted": False}
            }

    def get_available_files(self):
        """Retourne la liste des fichiers disponibles"""
        return [
            f"{name} ({data['size']}) - {data['encrypted'] and '🔒' or '📄'}"
            for name, data in self.files.items()
        ]

    def get_available_databases(self):
        """Retourne la liste des bases de données disponibles"""
        return [
            f"{name} ({data['size']}) - {data['encrypted'] and '🔒' or '🗃️'}"
            for name, data in self.databases.items()
        ] 

    def get_total_data_value(self):
        """Calcule la valeur totale des données disponibles"""
        total = 0
        for data in self.databases.values():
            total += data["value"]
        for data in self.files.values():
            total += data["value"]
        return total 

class FactionBonus:
    """Gestion des bonus de faction"""
    @staticmethod
    def get_faction_description(faction):
        descriptions = {
            Faction.SPECTRES: {
                "specialite": "Furtivité et infiltration",
                "bonus": [
                    "- Détection réduite de 20%",
                    "- Bonus de furtivité de 30%",
                    "- Bonus réseau de 20%"
                ]
            },
            Faction.FORGEURS: {
                "specialite": "Exploitation et piratage",
                "bonus": [
                    "- Chances de hack +40%",
                    "- Bonus d'exploitation de 30%",
                    "- Bonus CPU de 20%"
                ]
            },
            Faction.VEILLEURS: {
                "specialite": "Surveillance et contrôle",
                "bonus": [
                    "- Bonus d'analyse de 50%",
                    "- Bonus de défense de 30%",
                    "- Bonus de refroidissement de 20%"
                ]
            }
        }
        return descriptions.get(faction, {"specialite": "Inconnue", "bonus": []})

    @staticmethod
    def get_mission_bonus(faction, mission_type):
        """Calcule le bonus de faction pour un type de mission"""
        bonuses = {
            Faction.SPECTRES: {
                MissionType.INFILTRATION: 1.5,   # +50% pour infiltration
                MissionType.DATA_THEFT: 1.3,     # +30% pour vol de données
                MissionType.RANSOMWARE: 1.0,     # Pas de bonus
                MissionType.BOTNET: 1.1,         # +10% pour botnet
                MissionType.SABOTAGE: 1.2        # +20% pour sabotage
            },
            Faction.FORGEURS: {
                MissionType.INFILTRATION: 1.1,   # +10% pour infiltration
                MissionType.DATA_THEFT: 1.2,     # +20% pour vol de données
                MissionType.RANSOMWARE: 1.5,     # +50% pour ransomware
                MissionType.BOTNET: 1.3,         # +30% pour botnet
                MissionType.SABOTAGE: 1.4        # +40% pour sabotage
            },
            Faction.VEILLEURS: {
                MissionType.INFILTRATION: 1.2,   # +20% pour infiltration
                MissionType.DATA_THEFT: 1.1,     # +10% pour vol de données
                MissionType.RANSOMWARE: 1.3,     # +30% pour ransomware
                MissionType.BOTNET: 1.5,         # +50% pour botnet
                MissionType.SABOTAGE: 1.4        # +40% pour sabotage
            }
        }
        return bonuses.get(faction, {}).get(mission_type, 1.0)