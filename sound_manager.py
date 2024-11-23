# sound_manager.py

import pygame
import os

class SoundManager:
    def __init__(self):
        self.sounds = {}

    def load_sound(self, name, filepath, volume=1.0):
        if os.path.exists(filepath):
            sound = pygame.mixer.Sound(filepath)
            sound.set_volume(volume)
            self.sounds[name] = sound
        else:
            print(f"Warning: Sound file {filepath} not found.")

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()
        else:
            print(f"Warning: Sound {name} not loaded.")
