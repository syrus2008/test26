class GameError(Exception):
    """Classe de base pour les exceptions du jeu"""
    pass

# Alias pour la compatibilité
CyberHackError = GameError

class SaveError(GameError):
    """Erreur de sauvegarde"""
    pass

class MissionError(GameError):
    """Erreur de mission"""
    pass

class SecurityError(GameError):
    """Erreur de sécurité"""
    pass

class HardwareError(GameError):
    """Erreur liée au hardware"""
    pass 