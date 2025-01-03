from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import random
from enums import SecurityLevel, TargetType

@dataclass
class Target:
    id: str
    name: str
    type: TargetType
    security_level: SecurityLevel
    description: str
    ip: str
    ports: List[int]
    vulnerabilities: List[str]
    data_value: int
    security_systems: Dict[str, bool]
    mission_id: Optional[str] = None

    def __post_init__(self):
        """Initialise les fichiers et bases de données en fonction du type de cible"""
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
        elif self.type == TargetType.DATACENTER:
            self.databases = {
                "client_data.db": {"size": "5.2GB", "value": 3000, "encrypted": True},
                "logs.db": {"size": "1.2GB", "value": 800, "encrypted": False},
                "metrics.db": {"size": "2.5GB", "value": 1200, "encrypted": False}
            }
            self.files = {
                "access_codes.txt": {"size": "42KB", "value": 2000, "encrypted": True},
                "network_map.pdf": {"size": "15MB", "value": 1000, "encrypted": False},
                "backup_config.xml": {"size": "2MB", "value": 500, "encrypted": False}
            }
        elif self.type == TargetType.RESEARCH:
            self.databases = {
                "research_data.db": {"size": "8.5GB", "value": 5000, "encrypted": True},
                "experiments.db": {"size": "3.2GB", "value": 2500, "encrypted": True},
                "personnel.db": {"size": "1.1GB", "value": 1000, "encrypted": False}
            }
            self.files = {
                "research_notes.pdf": {"size": "450MB", "value": 3000, "encrypted": True},
                "prototype_specs.dwg": {"size": "250MB", "value": 4000, "encrypted": True},
                "lab_schedule.xlsx": {"size": "1.2MB", "value": 300, "encrypted": False}
            }
        else:
            # Type par défaut
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

class TargetGenerator:
    def __init__(self):
        self.target_templates = {
            TargetType.CORPORATE: {
                "name_prefix": ["Global", "Mega", "Tech", "Cyber", "Data"],
                "name_suffix": ["Corp", "Industries", "Systems", "Solutions", "Tech"],
                "ports": [80, 443, 22, 3389],
                "security_level": SecurityLevel.MEDIUM,
                "vulnerabilities": [
                    "SQL Injection",
                    "Weak Password",
                    "Default Password",
                    "Service Misconfiguration"
                ]
            },
            TargetType.BANK: {
                "name_prefix": ["First", "Global", "Secure", "Digital", "World"],
                "name_suffix": ["Bank", "Financial", "Trust", "Banking", "Capital"],
                "ports": [443, 8443, 22],
                "security_level": SecurityLevel.HIGH,
                "vulnerabilities": [
                    "Zero Day Exploit",
                    "Memory Leak",
                    "API Misconfiguration",
                    "Weak Backup Protocol"
                ]
            },
            TargetType.RESEARCH: {
                "name_prefix": ["Advanced", "Future", "Quantum", "Bio", "Nano"],
                "name_suffix": ["Labs", "Research", "Science", "Institute", "Technologies"],
                "ports": [80, 443, 22, 8080],
                "security_level": SecurityLevel.MEDIUM,
                "vulnerabilities": [
                    "Container Escape",
                    "API Misconfiguration",
                    "Backup System Flaw",
                    "Service Misconfiguration"
                ]
            },
            TargetType.INFRASTRUCTURE: {
                "name_prefix": ["Power", "Grid", "Network", "City", "Smart"],
                "name_suffix": ["Grid", "Systems", "Control", "Infrastructure", "Network"],
                "ports": [80, 443, 22, 502],
                "security_level": SecurityLevel.EXTREME,
                "vulnerabilities": [
                    "SCADA Exploit",
                    "Control System Bypass",
                    "Default Password",
                    "Service Misconfiguration"
                ]
            },
            TargetType.GOVERNMENT: {
                "name_prefix": ["Gov", "State", "Federal", "National", "Central"],
                "name_suffix": ["Agency", "Department", "Office", "Bureau", "Authority"],
                "ports": [443, 8443, 22, 1433],
                "security_level": SecurityLevel.EXTREME,
                "vulnerabilities": [
                    "Zero Day Exploit",
                    "Admin Access Exploit",
                    "SMB Exploit",
                    "SNMP Exploit"
                ]
            }
        }

    def generate_ip(self):
        """Génère une adresse IP aléatoire"""
        return ".".join(str(random.randint(1, 255)) for _ in range(4))

    def get_targets_for_mission(self, mission_id):
        """Génère les cibles principales pour une mission"""
        mission_type = mission_id.split("_")[0]
        
        # Sélectionner les types de cibles appropriés
        if mission_type == "INF":  # Infiltration
            target_types = [TargetType.CORPORATE, TargetType.RESEARCH]
        elif mission_type == "DAT":  # Vol de données
            target_types = [TargetType.BANK, TargetType.RESEARCH]
        elif mission_type == "RAN":  # Ransomware
            target_types = [TargetType.CORPORATE, TargetType.INFRASTRUCTURE]
        elif mission_type == "BOT":  # Botnet
            target_types = [TargetType.CORPORATE, TargetType.INFRASTRUCTURE]
        elif mission_type == "SAB":  # Sabotage
            target_types = [TargetType.INFRASTRUCTURE, TargetType.GOVERNMENT]
        else:
            target_types = list(TargetType)
            
        # Générer 1-3 cibles principales
        num_targets = random.randint(1, 3)
        targets = []
        
        for i in range(num_targets):
            target_type = random.choice(target_types)
            template = self.target_templates[target_type]
            
            # Générer le nom
            name = (
                random.choice(template["name_prefix"]) + 
                random.choice(template["name_suffix"])
            )
            
            # Sélectionner les vulnérabilités
            num_vulns = random.randint(2, 4)
            vulnerabilities = random.sample(template["vulnerabilities"], num_vulns)
            
            # Sélectionner les ports
            num_ports = random.randint(2, len(template["ports"]))
            ports = random.sample(template["ports"], num_ports)
            
            # Générer la valeur des données
            data_value = random.randint(1000, 5000)
            
            # Créer la cible
            target = Target(
                id=f"{mission_type}_{i+1}",
                name=name,
                type=target_type,
                security_level=template["security_level"],
                ip=self.generate_ip(),
                vulnerabilities=vulnerabilities,
                ports=ports,
                data_value=data_value,
                description=f"Cible principale de la mission {mission_id}",
                security_systems={
                    "firewall": True,
                    "ids": random.choice([True, False]),
                    "encryption": random.choice([True, False])
                }
            )
            targets.append(target)
            
        return targets

    def get_secondary_targets_for_mission(self, mission_id):
        """Génère les cibles secondaires pour une mission"""
        # Générer 0-2 cibles secondaires
        num_targets = random.randint(0, 2)
        targets = []
        
        for i in range(num_targets):
            target_type = random.choice(list(TargetType))
            template = self.target_templates[target_type]
            
            # Générer le nom
            name = (
                random.choice(template["name_prefix"]) + 
                random.choice(template["name_suffix"])
            )
            
            # Sélectionner les vulnérabilités (moins que les cibles principales)
            num_vulns = random.randint(1, 2)
            vulnerabilities = random.sample(template["vulnerabilities"], num_vulns)
            
            # Sélectionner les ports
            num_ports = random.randint(1, len(template["ports"]))
            ports = random.sample(template["ports"], num_ports)
            
            # Générer la valeur des données (moins que les cibles principales)
            data_value = random.randint(500, 2000)
            
            # Créer la cible
            target = Target(
                id=f"SEC_{mission_id}_{i+1}",
                name=name,
                type=target_type,
                security_level=SecurityLevel.MEDIUM,  # Plus facile que les principales
                ip=self.generate_ip(),
                vulnerabilities=vulnerabilities,
                ports=ports,
                data_value=data_value,
                description=f"Cible secondaire de la mission {mission_id}",
                security_systems={
                    "firewall": True,
                    "ids": False,
                    "encryption": False
                }
            )
            targets.append(target)
            
        return targets

    def generate_target_description(self, target):
        """Génère une description détaillée d'une cible"""
        security_desc = {
            SecurityLevel.LOW: "Sécurité basique, idéale pour débuter",
            SecurityLevel.MEDIUM: "Sécurité standard, vigilance requise",
            SecurityLevel.HIGH: "Haute sécurité, expertise nécessaire",
            SecurityLevel.EXTREME: "Sécurité maximale, extrême prudence"
        }
        
        type_desc = {
            TargetType.CORPORATE: "Entreprise avec des données sensibles",
            TargetType.BANK: "Institution financière hautement sécurisée",
            TargetType.RESEARCH: "Centre de recherche avec données confidentielles",
            TargetType.INFRASTRUCTURE: "Infrastructure critique",
            TargetType.GOVERNMENT: "Organisation gouvernementale"
        }
        
        return [
            f"=== {target.name} ===",
            f"Type: {type_desc[target.type]}",
            f"Sécurité: {security_desc[target.security_level]}",
            f"IP: {target.ip}",
            "",
            "Ports ouverts:",
            *[f"- {port} ({self._get_protocol(port)})" for port in target.ports],
            "",
            "Vulnérabilités détectées:",
            *[f"- {vuln}" for vuln in target.vulnerabilities],
            "",
            "Systèmes de sécurité:",
            *[f"- {sys}: {'Actif' if active else 'Inactif'}" 
              for sys, active in target.security_systems.items()],
            "",
            f"Valeur estimée des données: {target.data_value}¢"
        ]

    def _get_protocol(self, port):
        """Retourne le protocole associé à un port"""
        protocols = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            80: "HTTP",
            443: "HTTPS",
            445: "SMB",
            502: "Modbus",
            1433: "MSSQL",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            8080: "HTTP-ALT",
            8443: "HTTPS-ALT",
            9000: "API"
        }
        return protocols.get(port, "UNKNOWN") 