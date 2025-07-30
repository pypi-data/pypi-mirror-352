import moderngl,pygame,sys

from teon.window import window
from teon.time import time

from teon.other import _key_dict_inverted
import time as tm

from teon.renderer import Renderer
from teon.level import Level

from teon.mouse import mouse

from teon.camera import camera

from teon.entity import Entity

from teon.functions import convert_color
from teon.shader import VERTEX_SHADER,FRAGMENT_SHADER

class Teon:
    _instance = 0
    def __init__(self,**kwargs):

        Teon._instance = self

        self.fps = kwargs.get("fps",60)
        self._background_color = convert_color(kwargs.get("background_color",(255,255,255)),"rgb")

        self.key_press_time = kwargs.get("key_press_time",0.2)

        self._time = time

        self._clock = pygame.time.Clock()

        self._renderer = Renderer()
        Level(0)
        self._renderer.set_active_level(0)
        Entity._renderer = self._renderer
        self._renderer._core = self

        self.debug = kwargs.get("debug",False)

        self._window = window
        self._window._core = self
        self._window.get_kwargs(**kwargs)

        self._camera = camera
        self._camera._core = self
        self._camera._get_kwargs(**kwargs)
        
        self._mouse = mouse
        self._mouse._core = self
        
        self._ctx = moderngl.create_context()

        self._ctx.enable(moderngl.BLEND)
        self._ctx.blend_func = (moderngl.SRC_ALPHA,moderngl.ONE_MINUS_SRC_ALPHA,moderngl.ONE,moderngl.ONE_MINUS_SRC_ALPHA,)


        self._prog = self._ctx.program(VERTEX_SHADER,FRAGMENT_SHADER)

    @property
    def entities(self):
        entities = []
        for level in self._renderer.levels:
            for entity in level:
                entities.append[entity]
        return entities

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self,color):
        self._background_color = color
    
    def _update_func(self):
        pass

    def _input_func(self,key):
        pass

    def run(self):
        self._update_func = sys.modules["__main__"].__dict__.get("update") if callable(sys.modules["__main__"].__dict__.get("update")) else self._update_func
            
        self._input_func = sys.modules["__main__"].__dict__.get("input") if callable(sys.modules["__main__"].__dict__.get("input")) else self._input_func

        while True:

            call_input = False
            key = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                
                if event.type == pygame.MOUSEMOTION:
                    self._mouse._update(self._window)

                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    key_pressed = event.key if event.type == pygame.KEYDOWN else event.button
                    key_pressed_time = tm.time()
                
                elif event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                    if key_pressed != None:
                        key_released = event.key if event.type == pygame.KEYUP else event.button
                        if key_pressed == key_released:
                            key_released_time = tm.time()
                            if key_released_time - key_pressed_time <= self.key_press_time and key_pressed in [tup[0] for tup in _key_dict_inverted.items()]:
                                for entity in self._renderer.active_level:
                                    entity.input(_key_dict_inverted[key_pressed])
                                call_input = True
                                key = key_pressed
            
                                
                        key_pressed = None

            self._ctx.clear(0,0,0)

            x = self._clock.get_fps()
            self._time.fps = x
            if x != 0:
                self._time._update(1/x)
                    
            self._update_func()
            if call_input and key in [tup[0] for tup in _key_dict_inverted.items()]:
                self._input_func(_key_dict_inverted[key])

            self._renderer._update()
            self._renderer._render()

            if self.debug:
                for entity in self._renderer.active_level:
                    for collider in entity.colliders.items():
                        collider[1]._draw()
                    if entity.collider:
                        entity.collider._draw()

            pygame.display.flip()
            self._clock.tick(self.fps)

    

    def quit(self):
        pygame.quit()
        sys.exit()

def _get_main():
    return Teon._instance