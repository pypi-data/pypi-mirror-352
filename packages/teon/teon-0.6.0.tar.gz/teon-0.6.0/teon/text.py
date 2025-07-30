import pygame,moderngl
import numpy as np

from teon.entity import Entity
from teon.attributes import Position,Vec2
from teon.functions import convert_color,_get_info
from teon.collider import RectCollider
from teon.other import ColliderDict

pygame.font.init()

class Text(Entity):
    def __init__(self,**kwargs):

        self._info = _get_info()

        self._parent = kwargs.get("parent",None)
        if self._parent != None:
            self._parent.children.append(self)

        self.children = kwargs.get("children",[])

        self.colliders = ColliderDict(kwargs.get("colliders",{}))
        self.colliders._parent = self

        self.collider = None
        
        self._position = Position()
        self._position._entity = self

        self._scale = Position()
        self._scale._entity = self

        self._parent_offset = None if self._parent == None else Vec2(self.position.x - self._parent.position.x,self.position.y - self._parent.position.y)

        self.collider = RectCollider((0,0),(1,1),self) if kwargs.get("collider") == True else (None if kwargs.get("collider",None) == None else RectCollider(kwargs.get("collider")[0],kwargs.get("collider")[1],self))

        self.scale = kwargs.get("scale",1)
        self.position = kwargs.get("position",(0,0))

        self.alpha = kwargs.get("alpha",1)
        
        self._renderer = Entity._renderer

        self.visible = kwargs.get("visible",True)

        self.is_ui = kwargs.get("is_ui",True)

        self._z = 0
        self.z = kwargs.get("z",0)

        self.level_index = kwargs.get("level_index",self._renderer.active_level.index)

        self.collide = kwargs.get("collide",False)

        self._recalculate_vertices()

        self._last_instance = (self.top,self.left,self.right,self.bottom,self.position.x,self.position.y)

        self._text = kwargs.get("text","Empty Text")

        self._color = kwargs.get("color",(255,255,255))
        self._antialias = kwargs.get("antialias",False)
        self._font_size = kwargs.get("font_size",200)
        self._size = kwargs.get("size",1)
        self._font = kwargs.get("font",None)
        self._background_color = kwargs.get("background_color",None)

        self._texture = None

        self._render_text()

    def _rgb255(self,color):
        return (int(color[0] * 255),int(color[1] * 255),int(color[2] * 255))

        
    def _render_text(self):
        text = pygame.font.Font(self._font,self._font_size).render(self._text,self._antialias,self._rgb255(convert_color(self._color,"rgb")),self._rgb255(convert_color(self._background_color,"rgb")) if not self._background_color == None else None).convert_alpha()
        pygame.image.save(text,"ski.png")
        text_data = pygame.image.tostring(text, "RGBA", True)

        self._texture = text

        self.scale = (1 * self._size,text.get_size()[1] / text.get_size()[0] * self._size)

        tex = self._info['ctx'].texture(text.get_size(), 4, text_data)
        tex.build_mipmaps()

        self._image = tex

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self,size):
        self._size = size
        self.scale = (1 * self._size,self._texture.get_size()[1] / self._texture.get_size()[0] * self._size)

    def font_size(self):
        return 
    
    def font_size(self,size):
        self._font_size = size
        self._render_text()

    @property
    def font(self):
        return self._font
    
    @font.setter
    def font(self,font):
        self._font = font
        self._render_text()

    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self,color):
        self._color = color
        self._render_text()

    @property
    def antialias(self):
        return self._antialias
    
    @antialias.setter
    def font(self,antialias):
        self._antialias = antialias
        self._render_text()

    @property
    def background_color(self):
        return self._background_color
    
    @background_color.setter
    def background_color(self,background_color):
        self._background_color = background_color
        self._render_text()

    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self,text):
        self._text = text
        self._render_text()

    def _recalculate_vertices(self):
        if self.is_ui == False:
            super()._recalculate_vertices()
        else:
            sx,bx = (self.position.x - self.scale.x / 2),(self.position.x + self.scale.x / 2)
            sy,by = (self.position.y - self.scale.y / 2),(self.position.y + self.scale.y / 2)
            self.vertices = np.array([
                sx,sy,0.0,0.0,
                bx,sy,1.0,0.0,
                sx,by,0.0,1.0,
                bx,by,1.0,1.0
            ],dtype = 'f4')

            self.vbo = self._info["ctx"].buffer(self.vertices.tobytes())
            self.vao = self._info["ctx"].simple_vertex_array(self._info["prog"], self.vbo, 'in_pos', 'in_uv')

            self._update_colliders()

    def _draw(self):
        self._image.use(location = 0)
        self._renderer._core._prog['tex'].value = 0
        self._renderer._core._prog['u_alpha'].value = self.alpha
        
        self._renderer._core._prog['zoom'].value = self._renderer._core._camera.zoom

        if not self.is_ui:
            self._renderer._core._prog['camera_offset'].write(self._renderer._core._camera._offset.tobytes())
        else:
            self._renderer._core._prog['camera_offset'].write(np.array([0,0],dtype = 'f4').tobytes())

        self.vao.render(moderngl.TRIANGLE_STRIP)