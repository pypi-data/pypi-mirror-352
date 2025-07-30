from teon.attributes import Vec2,OffsetPosition
from teon.functions import convert_color
import numpy as np
import moderngl

class RectCollider:
    def __init__(self,position_offset,scale_offset,parent,**kwargs):
        self._position_offset = OffsetPosition(position_offset)
        self._scale_offset = OffsetPosition(scale_offset)

        self._position_offset._entity = self
        self._scale_offset._entity = self

        self._parent = parent

        self.name = kwargs.get("name",None)
        self.color = kwargs.get("color",(255,0,0))
        self.visible = kwargs.get("visible",True)
        self.debug = kwargs.get("debug",False)
        self._scalable = kwargs.get("scalable",True)

        self._position = Vec2()
        self._scale = Vec2()

        self._update()

    @property
    def left(self):
        return self.topleft.x
    
    @property
    def right(self):
        return self.topright.x
    
    @property
    def top(self):
        return self.topleft.y
    
    @property
    def bottom(self):
        return self.bottomleft.y

    @property
    def topleft(self):
        return Vec2(self._position.x - self._scale.x / 2,self._position.y + self._scale.y / 2)

    @property
    def midtop(self):
        return Vec2(self._position.x,self._position.y + self._scale.y / 2)
    
    @property
    def topright(self):
        return Vec2(self._position.x + self._scale.x / 2,self._position.y + self._scale.y / 2)
    
    @property
    def midleft(self):
        return Vec2(self._position.x - self._scale.x / 2,self._position.y)
    
    @property
    def center(self):
        return Vec2(self._position.x,self._position.y)
    
    @property
    def midright(self):
        return Vec2(self._position.x + self._scale.x / 2,self._position.y)
    
    @property
    def bottomleft(self):
        return Vec2(self._position.x - self._scale.x / 2,self._position.y - self._scale.y / 2)
    
    @property
    def midbottom(self):
        return Vec2(self._position.x,self._position.y - self._scale.y / 2)
    
    @property
    def bottomright(self):
        return Vec2(self._position.x + self._scale.x / 2,self._position.y - self._scale.y / 2)

    @property
    def scale_offset(self):
        return self._scale_offset

    @scale_offset.setter
    def scale_offset(self,scale):
        if isinstance(scale,int) or isinstance(scale,float):
            self._scale_offset.x = scale
            self._scale_offset.y = scale
        else:
            self._scale_offset.x = scale[0]
            self._scale_offset.y = scale[1]

    @property
    def position_offset(self):
        return self._position_offset

    @position_offset.setter
    def position_offset(self,position):
        self._position_offset.x = position[0]
        self._position_offset.y = position[1]

    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self,color):
        self._color = color
        self._image = self._parent._get_color_tex(convert_color(color,"rgb"))

    def _update(self):
        self._position.x,self._position.y = (self._parent.position.x + self._position_offset[0],self._parent.position.y + self._position_offset[1])
        if self._scalable:
            self._scale.x,self._scale.y = (self._parent.scale.x * self._scale_offset[0],self._parent.scale.y * self._scale_offset[1])
        else:
            self._scale.x,self._scale.y = (self._scale_offset)

        self._recalculate_vertices()

    def _recalculate_vertices(self):
        self.vertices = np.array([
            (self._position.x - self._scale.x / 2) / self._parent._info["size"][0] * self._parent._info["size"][1],self._position.y - self._scale.y / 2,0.0,0.0,
            ((self._position.x - self._scale.x / 2) / self._parent._info["size"][0] * self._parent._info["size"][1] + self._scale.x * self._parent._info["scale_def"]),self._position.y - self._scale.y / 2,1.0,0.0,
            (self._scale.x * self._parent._info["scale_def"] + (self._position.x - self._scale.x / 2) / self._parent._info["size"][0] * self._parent._info["size"][1]),(self._position.y + self._scale.y * self._parent._info["scale_def"] * self._parent._info["size"][0] / self._parent._info["size"][1]) - self._scale.y / 2,0.0,1.0,
            (self._position.x - self._scale.x / 2) / self._parent._info["size"][0] * self._parent._info["size"][1],(self._position.y + self._scale.y * self._parent._info["scale_def"] * self._parent._info["size"][0] / self._parent._info["size"][1]) - self._scale.y / 2,1.0,1.0
        ],dtype = 'f4')

        self.vbo = self._parent._info["ctx"].buffer(self.vertices.tobytes())
        self.vao = self._parent._info["ctx"].simple_vertex_array(self._parent._info["prog"], self.vbo, 'in_pos', 'in_uv')

    def _draw(self):
        self._image.use(location = 0)
        self._parent._renderer._core._prog['tex'].value = 0
        self._parent._renderer._core._prog['u_alpha'].value = 1
        self._parent._renderer._core._prog['camera_offset'].write(self._parent._renderer._core._camera._offset.tobytes())
        self._parent._renderer._core._prog['zoom'].value = self._parent._renderer._core._camera.zoom


        self.vao.render(moderngl.LINE_LOOP)