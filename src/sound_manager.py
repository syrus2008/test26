import pygame
from pathlib import Path

class SoundManager:
    def __init__(self):
        self.sounds = {
            'click': self.load_sound('click.wav'),
            'window_open': self.load_sound('window_open.wav'),
            'window_close': self.load_sound('window_close.wav'),
            'error': self.load_sound('error.wav'),
            'success': self.load_sound('success.wav')
        }
        
    def load_sound(self, filename):
        try:
            sound_path = Path('assets/sounds') / filename
            return pygame.mixer.Sound(str(sound_path))
        except:
            print(f"Couldn't load sound: {filename}")
            return None
            
    def play(self, sound_name):
        if sound := self.sounds.get(sound_name):
            sound.play() 