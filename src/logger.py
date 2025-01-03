import logging
from pathlib import Path

def setup_logger():
    logger = logging.getLogger('cyberhack')
    logger.setLevel(logging.DEBUG)
    
    # Handler fichier
    fh = logging.FileHandler('logs/game.log')
    fh.setLevel(logging.DEBUG)
    
    # Handler console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger 