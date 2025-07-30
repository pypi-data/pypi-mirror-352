import pygame

pygame.mixer.init()

class Audio:
    def __init__(self, path):
        self.song = pygame.mixer.Sound(path)
        self.channel = None

    def play(self, loops=0):
        self.channel = self.song.play(loops=loops)

    def stop(self):
        if self.channel:
            self.channel.stop()

    def pause(self):
        if self.channel and self.channel.get_busy():
            self.channel.pause()

    def unpause(self):
        if self.channel:
            self.channel.unpause()

    def set_volume(self, volume):
        self.song.set_volume(volume)

def load_audio(path):
    return Audio(path)