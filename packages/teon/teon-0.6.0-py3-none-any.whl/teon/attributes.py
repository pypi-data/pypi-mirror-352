class Vec2:
    def __init__(self,x = (0,0),y = None):
        if y != None:
            self.x = x
            self.y = y
        else:
            self.x,self.y = x[0],x[1]

    def __repr__(self):
        return f"({self.x},{self.y})"
    
    def __getitem__(self, index):
        return (self.x,self.y)[index]
    
    def __add__(self,other):
        if isinstance(other,(float,int)):
            return Vec2(self.x + other,self.y + other)
        else:
            return Vec2(self.x + other[0],self.y + other[1])
    
    def __sub__(self,other):
        if isinstance(other,(float,int)):
            return Vec2(self.x - other,self.y - other)
        else:
            return Vec2(self.x - other[0],self.y - other[1])
    
    def __mul__(self,other):
        if isinstance(other,(float,int)):
            return Vec2(self.x * other,self.y * other)
        else:
            return Vec2(self.x * other[0],self.y * other[1])
        
    def __truediv__(self,other):
        if isinstance(other,(float,int)):
            return Vec2(self.x / other,self.y / other)
        else:
            return Vec2(self.x / other[0],self.y / other[1])
        
    def __iadd__(self,other):
        if isinstance(other,(float,int)):
            self.x += other
            self.y += other
        else:
            self.x += other[0]
            self.y += other[1]
        return self
    
    def __isub__(self,other):
        if isinstance(other,(float,int)):
            self.x -= other
            self.y -= other
        else:
            self.x -= other[0]
            self.y -= other[1]
        return self
    
    def __imul__(self,other):
        if isinstance(other,(float,int)):
            self.x *= other
            self.y *= other
        else:
            self.x *= other[0]
            self.y *= other[1]
        return self
    
    def __itruediv__(self,other):
        if isinstance(other,(float,int)):
            self.x /= other
            self.y /= other
        else:
            self.x /= other[0]
            self.y /= other[1]
        return self
        
class Position(Vec2):
    def __init__(self,x = (0,0),y = None):
        if y != None:
            self._x = x
            self._y = y
        else:
            self._x,self._y = x[0],x[1]

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self,x):
        self._x = x
        self._entity._update_all()

    def _set(self,x = None,y = None):
        if y == None:
            self._x = x if self._entity._parent_offset == None else (self._entity._parent.position.x + self._entity._parent_offset.x)
        elif x == None:
            self._y = y if self._entity._parent_offset == None else (self._entity._parent.position.y + self._entity._parent_offset.y)
        else:
            self._x = x if self._entity._parent_offset == None else (self._entity._parent.position.x + self._entity._parent_offset.x)
            self._y = y if self._entity._parent_offset == None else (self._entity._parent.position.y + self._entity._parent_offset.y)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self,y):
        self._y = y
        self._entity._update_all()
    
class WindowPosition(Vec2):
    def __init__(self,x = (0,0),y = None):
        if y != None:
            self._x = x
            self._y = y
        else:
            self._x,self._y = x[0],x[1]

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self,x):
        self._x = x
        self._entity._update_position()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self,y):
        self._y = y
        self._entity._update_position()
    
class CameraPosition(Vec2):
    def __init__(self,x = (0,0),y = None):
        if y != None:
            self._x = x
            self._y = y
        else:
            self._x,self._y = x[0],x[1]

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self,x):
        self._x = x
        self._entity._recalculate_offset()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self,y):
        self._y = y
        self._entity._recalculate_offset()

class UVec2(Vec2):
    def __init__(self,x = (0,0),y = None):
        if y != None:
            self._x = x
            self._y = y
        else:
            self._x,self._y = x[0],x[1]

    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self,x):
        pass
    
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self,y):
        pass

class OffsetPosition(Vec2):
    def __init__(self,x = (0,0),y = None):
        if y != None:
            self._x = x
            self._y = y
        else:
            self._x,self._y = x[0],x[1]

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self,x):
        self._x = x
        self._entity._update()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self,y):
        self._y = y
        self._entity._update()