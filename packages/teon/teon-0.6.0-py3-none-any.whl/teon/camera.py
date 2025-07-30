from teon.attributes import Vec2,CameraPosition
import numpy as np
from teon.functions import _get_info,scale_def
class Camera:
    def __init__(self):
        self._position = CameraPosition(0,0)
        self.position._entity = self

        self._offset = CameraPosition(0,0)
        self.offset._entity = self

    def _get_kwargs(self,**kwargs):

        self.position = kwargs.get("camera_position",(0,0))
        self.offset = kwargs.get("offset",(0,0))
        
        self.zoom = kwargs.get("zoom",1)
        
        self._recalculate_offset()

    def _recalculate_offset(self):
        diff = 1 / max(self._core._window.size)
        xs,ys = self._core._window.size
        self._pos_offset = np.array([(self.position.x + self.offset.x) * diff * ys,(self.position.y + self.offset.y) * diff * xs], dtype='f4') 

    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self,position):
        self._position.x = position[0]
        self._position.y = position[1]

        self._recalculate_offset()

    @property
    def offset(self):
        return self._offset
    
    @offset.setter
    def offset(self,offset):
        self._offset.x = offset[0]
        self._offset.y = offset[1]

        self._recalculate_offset()

camera = Camera()