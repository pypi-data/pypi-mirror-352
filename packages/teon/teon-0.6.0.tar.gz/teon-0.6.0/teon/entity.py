import moderngl
import numpy as np

from teon.functions import _get_info,load_image,convert_color,colliding
from teon.attributes import Position,Vec2

from teon.collider import RectCollider

from teon.other import ColliderDict

class Entity:
    _renderer = 0
    def __init__(self,**kwargs):
        if Entity._renderer == 0:
            raise Exception("Main game class is not initiated")
        
        self._info = _get_info()

        self._anchor = kwargs.get("anchor","center")

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

        self.scale = kwargs.get("scale",1)
        self.position = kwargs.get("position",(0,0))

        self._parent_offset = None if self._parent == None else Vec2(self.position.x - self._parent.position.x,self.position.y - self._parent.position.y)

        self.collider = RectCollider((0,0),(1,1),self) if kwargs.get("collider") == True else (None if kwargs.get("collider",None) == None else RectCollider(kwargs.get("collider")[0],kwargs.get("collider")[1],self))

        self.alpha = kwargs.get("alpha",1)

        if kwargs.get("image") != None:
            if isinstance(kwargs.get('image'),str):
                self.image = load_image(kwargs.get("image"))
            else:
                self.image = kwargs.get("image")
        else:
            self.image = self._get_color_tex(convert_color(kwargs.get("color","white"),"rgb"))
            self.color = kwargs.get("color","white")
        
        self._renderer = Entity._renderer

        self.visible = kwargs.get("visible",True)

        self._z = 0
        self.z = kwargs.get("z",0)

        self.level_index = kwargs.get("level_index",self._renderer.active_level.index)

        self.collide = kwargs.get("collide",False)

        self._recalculate_vertices()

        self._update_colliders()

    @property
    def anchor(self):
        return self._anchor
    
    @anchor.setter
    def anchor(self,anchor):
        self._anchor = anchor
        self._recalculate_vertices()

    def _update_all(self):
        if self._parent == None:
            self._parent_offset = None
        else:
            if hasattr(self,"_parent_offset"):
                self.position._set(self._position.x,self._position.y)
        self._recalculate_vertices()
        self._update_children()
        self._update_colliders()

    def _update_children(self):
        for child in self.children:
            child._update_all()

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self,parent):
        if self._parent != None:
            self._parent.children.pop(self)
        self._parent = parent
        self._parent.children.append(self)

    def _resolve_collision(self,other):
        horizontal_overlap = min(self.right,other.right) - max(self.left,other.left)
        vertical_overlap = min(self.top,other.top) - max(self.bottom,other.bottom)
        print(horizontal_overlap,vertical_overlap)
        if horizontal_overlap < vertical_overlap:
            if self.position.x < other.position.x:
                self.right =  other.collider.left + (self.scale.x - self.collider._scale.x) / 2
            else:
                self.left = other.collider.right - (self.scale.x - self.collider._scale.x) / 2
        elif horizontal_overlap > vertical_overlap:
            if self.position.y < other.position.y:
                self.top = other.collider.bottom + (self.scale.y - self.collider._scale.y) / 2
            else:
                self.bottom = other.collider.top - (self.scale.y - self.collider._scale.y) / 2
        else:
            if round(horizontal_overlap,15) == min(self.scale.x,other.scale.x):
                horizontal_tendency = min(max(self.right,other.right) - min(self.right,other.right),max(self.left,other.left) - min(self.left,other.left))
                vertical_tendency = min(max(self.top,other.top) - min(self.top,other.top),max(self.bottom,other.bottom) - min(self.bottom,other.bottom))
                print(horizontal_tendency,vertical_tendency)
                if horizontal_tendency < vertical_tendency:
                    if max(self.right,other.right) - min(self.right,other.right) > max(self.left,other.left) - min(self.left,other.left):
                        self.right =  other.collider.left + (self.scale.x - self.collider._scale.x) / 2
                    else:
                        self.left = other.collider.right - (self.scale.x - self.collider._scale.x) / 2
                elif vertical_tendency <= horizontal_tendency:
                    if max(self.top,other.top) - min(self.top,other.top) < max(self.bottom,other.bottom - min(self.bottom,other.bottom)):
                        self.top = other.collider.bottom + (self.scale.y - self.collider._scale.y) / 2
                    else:
                        self.bottom = other.collider.top - (self.scale.y - self.collider._scale.y) / 2

    def _update_colliders(self):
        for collider in self.colliders.items():
            collider[1]._parent = self
            collider[1]._update()
        if self.collider:
            self.collider._update()

    @property
    def image(self):
        return self._image
    
    @image.setter
    def image(self,image):
        if isinstance(image,str):
            self._image = load_image(image)
        else:
            self._image = image

    @property
    def level_index(self):
        return self._level_index
    
    @level_index.setter
    def level_index(self,level_index):
        self._level_index = level_index
        self._renderer._add_entity(self)

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
    
    @left.setter
    def left(self,val):
        self.topleft = (val,self.topleft.y)

    @right.setter
    def right(self,val):
        self.topright = (val,self.topright.y)

    @top.setter
    def top(self,val):
        self.topleft = (self.topleft.x,val)

    @bottom.setter
    def bottom(self,val):
        self.bottomleft = (self.bottomleft.x,val)

    @property
    def scale(self):
        return self._scale
    
    @property
    def alpha(self):
        return self._alpha
    
    @alpha.setter
    def alpha(self,alpha):
        self._alpha = alpha
    
    def _get_color_tex(self,color):
        white_pixel = bytes([round(color[0] * 255),round(color[1] * 255),round(color[2] * 255),255])  # RGBA
        texture = self._info["ctx"].texture((1, 1), components=4, data=white_pixel)
        
        return texture
    
    @scale.setter
    def scale(self,scale):
        if isinstance(scale,int) or isinstance(scale,float):
            self._scale.x = scale
            self._scale.y = scale
        else:
            self._scale.x = scale[0]
            self._scale.y = scale[1]

    @property
    def position(self):
        return self._position
    
    @property
    def color(self):
        return self.color
    
    @color.setter
    def color(self,color):
        self._color = color
        self.image = self._get_color_tex(convert_color(self._color,"rgb"))

    @position.setter
    def position(self,position):
        self._position.x = position[0]
        self._position.y = position[1]
    
    def update(self):
        pass

    @property
    def topleft(self):
        x = self.position.x - self.scale.x / 2
        y = self.position.y + self.scale.y / 2
            
        if self._anchor in ["topleft","tl"]:
            x += self.scale.x / 2
            y -= self.scale.y / 2
        elif self._anchor in ["midtop","mt"]:
            y -= self.scale.y / 2
        elif self._anchor in ["topright","tr"]:
            x -= self.scale.x / 2
            y -= self.scale.y / 2
        elif self._anchor in ["midleft","ml"]:
            x += self.scale.x / 2
        elif self._anchor in ["midright","mr"]:
            x -= self.scale.x / 2
        elif self._anchor in ["bottomleft","bl"]:
            y += self.scale.y / 2
            x += self.scale.x / 2
        elif self._anchor in ["midbottom","mb"]:
            y += self.scale.y / 2
        elif self._anchor in ["bottomright","br"]:
            y += self.scale.y / 2
            x -= self.scale.x / 2
        return Vec2(x,y)

    @property
    def midtop(self):
        return self.topleft + (self.scale.x / 2,0)
    
    @property
    def topright(self):
        return self.topleft + (self.scale.x,0)
    
    @property
    def midleft(self):
        return self.topleft + (0,-self.scale.y / 2)
    
    @property
    def center(self):
        return self.topleft + (self.scale.x / 2,-self.scale.y / 2)
    
    @property
    def midright(self):
        return self.topleft + (self.scale.x,-self.scale.y / 2)
    
    @property
    def bottomleft(self):
        return self.topleft + (0,-self.scale.y)
    
    @property
    def midbottom(self):
        return self.topleft + (self.scale.x / 2,-self.scale.y)
    
    @property
    def bottomright(self):
        return self.topleft + (self.scale.x,-self.scale.y)
    
    @topleft.setter
    def topleft(self,pos):
        self.position = (pos[0] + self.scale.x / 2,pos[1] - self.scale.y / 2)

    @midtop.setter
    def midtop(self,pos):
        self.position = (pos[0],pos[1] - self.scale.y / 2)
    
    @topright.setter
    def topright(self,pos):
        self.position = (pos[0] - self.scale.x / 2,pos[1] - self.scale.y / 2)
    
    @midleft.setter
    def midleft(self,pos):
        self.position = (pos[0] + self.scale.x / 2,pos[1])
    
    @center.setter
    def center(self,pos):
        self.position = (pos[0],pos[1])
    
    @midright.setter
    def midright(self,pos):
        self.position = (pos[0] - self.scale.x / 2,pos[1])
    
    @bottomleft.setter
    def bottomleft(self,pos):
        self.position = (pos[0] + self.scale.x / 2,pos[1] + self.scale.y / 2)
    
    @midbottom.setter
    def midbottom(self,pos):
        self.position = (pos[0],pos[1] + self.scale.y / 2)
    
    @bottomright.setter
    def bottomright(self,pos):
        self.position = (pos[0] - self.scale.x / 2,pos[1] + self.scale.y / 2)

    tl = topleft
    mt = midtop
    tr = topright
    ml = midleft
    c  = center
    mr = midright
    bl = bottomleft
    mb = midbottom
    br = bottomright

    @property
    def x(self):
        return self.position.x
    
    @property
    def y(self):
        return self.position.y
    
    @x.setter
    def x(self,x):
        self.position.x = x

    @y.setter
    def y(self,y):
        self.position.y = y

    def input(self,key):
        pass

    def _update(self):
        if self.collider and self.collide:
            for other in self._renderer.active_level:
                if not other is self and other.collider:
                    if colliding(self,other):
                        self._resolve_collision(other)

    def _recalculate_vertices(self):
        diff = 1 / max(self._info["size"])
        xs,ys = self._info["size"]
        if self._anchor in ["center","c"]:
            sx,bx = (self.position.x - self.scale.x / 2) * diff * ys,(self.position.x + self.scale.x / 2) * diff * ys
            sy,by = (self.position.y - self.scale.y / 2) * diff * xs,(self.position.y + self.scale.y / 2) * diff * xs
        elif self._anchor in ["topleft","tl"]:
            sx,bx = (self.position.x) * diff * ys,(self.position.x + self.scale.x) * diff * ys
            sy,by = (self.position.y - self.scale.y) * diff * xs,(self.position.y) * diff * xs
        elif self._anchor in ["midtop","mt"]:
            sx,bx = (self.position.x - self.scale.x / 2) * diff * ys,(self.position.x + self.scale.x / 2) * diff * ys
            sy,by = (self.position.y - self.scale.y) * diff * xs,(self.position.y) * diff * xs
        elif self._anchor in ["topright","tr"]:
            sx,bx = (self.position.x - self.scale.x) * diff * ys,(self.position.x) * diff * ys
            sy,by = (self.position.y - self.scale.y) * diff * xs,(self.position.y) * diff * xs
        elif self._anchor in ["midleft","ml"]:
            sx,bx = (self.position.x) * diff * ys,(self.position.x + self.scale.x) * diff * ys
            sy,by = (self.position.y - self.scale.y / 2) * diff * xs,(self.position.y + self.scale.y / 2) * diff * xs
        elif self._anchor in ["midright","mr"]:
            sx,bx = (self.position.x - self.scale.x) * diff * ys,(self.position.x) * diff * ys
            sy,by = (self.position.y - self.scale.y / 2) * diff * xs,(self.position.y + self.scale.y / 2) * diff * xs
        elif self._anchor in ["bottomleft","bl"]:
            sx,bx = (self.position.x) * diff * ys,(self.position.x + self.scale.x) * diff * ys
            sy,by = (self.position.y) * diff * xs,(self.position.y + self.scale.y) * diff * xs
        elif self._anchor in ["midbottom","mb"]:
            sx,bx = (self.position.x - self.scale.x / 2) * diff * ys,(self.position.x + self.scale.x / 2) * diff * ys
            sy,by = (self.position.y) * diff * xs,(self.position.y + self.scale.y) * diff * xs
        elif self._anchor in ["bottomright","br"]:
            sx,bx = (self.position.x - self.scale.x) * diff * ys,(self.position.x) * diff * ys
            sy,by = (self.position.y) * diff * xs,(self.position.y + self.scale.y) * diff * xs
        else:
            raise Exception(f"The given anchor <{self._anchor}> does not represent a point on the Entity")

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
        self._renderer._core._prog['camera_offset'].write(self._renderer._core._camera._pos_offset.tobytes())
        self._renderer._core._prog['zoom'].value = self._renderer._core._camera.zoom


        self.vao.render(moderngl.TRIANGLE_STRIP)