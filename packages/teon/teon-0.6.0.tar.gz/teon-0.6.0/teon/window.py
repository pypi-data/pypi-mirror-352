import pygame,ctypes
from teon.attributes import Vec2,WindowPosition
from ctypes import wintypes
from teon.other import ICON_BYTES

class Window:

    def get_kwargs(self,**kwargs):

        pygame.display.init()
        
        self._size = (0,0)
        self._fullscreen = False
        self._position = WindowPosition(0,0)
        self._position._entity = self
        self._caption = "Teon"
        self._icon = None
        self._resizable = False
        self._borderless = False

        self.size = Vec2(kwargs.get("size",(1920,1080)))

        self._hwnd = pygame.display.get_wm_info()['window']
        
        self.fullscreen = kwargs.get("fullscreen",False)
        self.caption = kwargs.get("caption","Teon")
        self.icon = kwargs.get("icon",pygame.image.fromstring(ICON_BYTES,(32,32),"RGBA"))
        self.resizable = kwargs.get("resizable",False)
        self.borderless = kwargs.get("borderless",False)
        
        self.position = kwargs.get("position",None)

    @property
    def size(self):
        return Vec2(self._size.x,self._size.y)

    @size.setter
    def size(self,size):
        self._size = Vec2(size[0],size[1])
        self._apply_properties()
        self._core._renderer._update_info()

        if hasattr(self._core,"_ctx"):
            self._core._ctx.viewport = (0,0,self.size.x,self.size.y)

    @property
    def game_size(self):
        return Vec2(self.size.x / self.size.y * 2,2)

    @property
    def fullscreen(self):
        return self._fullscreen
    
    def _apply_properties(self):
        if self._resizable:
            if self._borderless:
                self._display = pygame.display.set_mode((self.size.x,self.size.y),pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE | pygame.NOFRAME)
            else:
                self._display = pygame.display.set_mode((self.size.x,self.size.y),pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
        else:
            if self._borderless:
                self._display = pygame.display.set_mode((self.size.x,self.size.y),pygame.DOUBLEBUF | pygame.OPENGL | pygame.NOFRAME)
            else:
                self._display = pygame.display.set_mode((self.size.x,self.size.y),pygame.DOUBLEBUF | pygame.OPENGL)

    @fullscreen.setter
    def fullscreen(self,fullscreen):
        self._fullscreen = fullscreen
        if self._fullscreen:
            self.size = pygame.display.get_desktop_sizes()[0]
            self.position = (0,0)

    def _get_window_frame_size(self,style, ex_style):
        rect = wintypes.RECT(0, 0, 100, 100)
        ctypes.windll.user32.AdjustWindowRectEx(ctypes.byref(rect), style, False, ex_style)
        width_offset = rect.left * -1
        height_offset = rect.top * -1
        return width_offset, height_offset


    @property
    def borderless(self):
        return self._borderless
    
    @borderless.setter
    def borderless(self,borderless):
        self._borderless = borderless
        self._apply_properties()

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self,position):
        if position == 'center':
            size = pygame.display.get_desktop_sizes()[0]
            self._position.x = (size[0] - self.size.x) / 2
            self._position.y = (size[1] - self.size.y) / 2
        elif not position == None:
            self._position.x = position[0]
            self._position.y = position[1]

        if position == 'center' or not position == None:
            self._update_position()
    
    def _update_position(self):
        style = ctypes.windll.user32.GetWindowLongW(self._hwnd, -16)
        ex_style = ctypes.windll.user32.GetWindowLongW(self._hwnd, -20)
        offset_x, offset_y = self._get_window_frame_size(style, ex_style)

        ctypes.windll.user32.MoveWindow(
            self._hwnd,
            int(self._position.x - offset_x),
            int(self._position.y - offset_y),
            self.size.x,
            self.size.y,
            False
        )

    @property
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self,caption):
        self._caption = caption
        pygame.display.set_caption(caption)

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self,icon):
        self._icon = icon
        pygame.display.set_icon(icon)

    @property
    def resizable(self):
        return self._resizable

    @resizable.setter
    def resizable(self,resizable):
        self._resizable = resizable
        self._apply_properties()

window = Window()