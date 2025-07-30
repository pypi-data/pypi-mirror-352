from teon.entity import Entity
import numpy as np
import moderngl

class Widget(Entity):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.is_ui = True

    def _recalculate_vertices(self):
        diff = 1 / max(self._info["size"])
        xs,ys = self._info["size"]
        if self._anchor in ["center","c"]:
            sx,bx = self.position.x - self.scale.x / 2 * diff * ys,self.position.x + self.scale.x / 2 * diff * ys
            sy,by = self.position.y - self.scale.y / 2 * diff * xs,self.position.y + self.scale.y / 2 * diff * xs
        elif self._anchor in ["topleft","tl"]:
            sx,bx = self.position.x,self.position.x + self.scale.x * diff * ys
            sy,by = self.position.y - self.scale.y * diff * xs,self.position.y
        elif self._anchor in ["midtop","mt"]:
            sx,bx = self.position.x - self.scale.x / 2 * diff * ys,self.position.x + self.scale.x / 2 * diff * ys
            sy,by = self.position.y - self.scale.y * diff * xs,self.position.y
        elif self._anchor in ["topright","tr"]:
            sx,bx = self.position.x - self.scale.x * diff * ys,self.position.x
            sy,by = self.position.y - self.scale.y * diff * xs,self.position.y
        elif self._anchor in ["midleft","ml"]:
            sx,bx = self.position.x,self.position.x + self.scale.x * diff * ys
            sy,by = self.position.y - self.scale.y / 2 * diff * xs,self.position.y + self.scale.y / 2 * diff * xs
        elif self._anchor in ["midright","mr"]:
            sx,bx = self.position.x - self.scale.x * diff * ys,self.position.x
            sy,by = self.position.y - self.scale.y / 2 * diff * xs,self.position.y + self.scale.y / 2 * diff * xs
        elif self._anchor in ["bottomleft","bl"]:
            sx,bx = self.position.x,self.position.x + self.scale.x * diff * ys
            sy,by = self.position.y,self.position.y + self.scale.y * diff * xs
        elif self._anchor in ["midbottom","mb"]:
            sx,bx = self.position.x - self.scale.x / 2 * diff * ys,self.position.x + self.scale.x / 2 * diff * ys
            sy,by = self.position.y,self.position.y + self.scale.y * diff * xs
        elif self._anchor in ["bottomright","br"]:
            sx,bx = self.position.x - self.scale.x * diff * ys,self.position.x
            sy,by = self.position.y,self.position.y + self.scale.y * diff * xs

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
        self._renderer._core._prog['camera_offset'].write(np.array([0,0],dtype = 'f4').tobytes())

        self.vao.render(moderngl.TRIANGLE_STRIP)