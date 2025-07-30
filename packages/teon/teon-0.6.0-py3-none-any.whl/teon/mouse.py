from teon.attributes import Vec2

from teon.functions import scale_def

import pygame

class Mouse:
    def __init__(self):
        self._position = Vec2(0,0)
    
    def _update(self,window):
        mxy = min(self._core._window.size)

        pos = Vec2(pygame.mouse.get_pos())
        pos.y = pos.y - window.size.y / 2
        pos.x = pos.x - window.size.x / 2
        if not scale_def() == 0:
            self.position.x =  (pos.x / mxy * 2) / self._core._camera.zoom + self._core._camera.position.x
            self.position.y = -(pos.y / mxy * 2) / self._core._camera.zoom + self._core._camera.position.y

    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self,position):
        self._position.x = position[0]
        self._position.y = position[1]

mouse = Mouse()