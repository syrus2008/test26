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