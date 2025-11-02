import pygame
import os
from .utils import get_sound_path

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()

    def load_sounds(self):
        sound_files = {
            "eat": "eat.wav",
            "fanfare": "fanfare.wav",
            "game": "game.wav",
            "gameover": "gameover.wav",
            "level": "level.wav",
            "lost": "lost.wav",
            "start": "start.wav",
            "walk": "walk.wav",
            "win": "win.wav"
        }
        for name, filename in sound_files.items():
            path = get_sound_path(filename)
            try:
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                else:
                    print(f"Warning: Sound file not found at {path}")
            except pygame.error as e:
                print(f"Warning: Could not load sound file {path}: {e}")

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def stop(self, name):
        if name in self.sounds:
            self.sounds[name].stop()

    def play_music(self, name, loops=-1):
        sound_path = get_sound_path(name + ".wav")
        try:
            if os.path.exists(sound_path):
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play(loops)
            else:
                print(f"Warning: Music file not found at {sound_path}")
        except pygame.error as e:
            print(f"Warning: Could not load music file {sound_path}: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()
