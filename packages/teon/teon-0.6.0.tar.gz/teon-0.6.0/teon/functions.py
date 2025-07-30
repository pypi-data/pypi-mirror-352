import pygame,moderngl
from teon.other import _color_dict,_color_dict_inverted,_key_dict
from PIL import Image

def convert_color(color, return_type):
    def to_float_tuple(rgb):
        if max(rgb) > 1:
            return tuple(v / 255 for v in rgb)
        return rgb

    def to_int_tuple(rgb):
        if max(rgb) <= 1:
            return tuple(int(round(v * 255)) for v in rgb)
        return tuple(int(v) for v in rgb)

    if return_type.lower() == "rgb":
        if isinstance(color, tuple):
            return to_float_tuple(color)
        if color.startswith("#"):
            color = color.lstrip("#")
            rgb_int = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
            return to_float_tuple(rgb_int)
        return to_float_tuple(_color_dict[color])

    elif return_type.lower() in ("hex", "hexadecimal"):
        if isinstance(color, tuple):
            r, g, b = to_int_tuple(color)
            return "#{:02X}{:02X}{:02X}".format(r, g, b)
        if color.startswith("#"):
            return color
        return convert_color(_color_dict[color], "hex")

    elif return_type.lower() in ("str", "string"):
        if isinstance(color, tuple):
            return _color_dict_inverted[to_int_tuple(color)]
        if color.startswith("#"):
            rgb_f = convert_color(color, "rgb")
            return _color_dict_inverted[to_int_tuple(rgb_f)]
        return color

    else:
        raise ValueError(f"Unsupported return_type: {return_type}")

        
def scale_def():
    size = pygame.display.get_surface().get_size()
    return min(size[0],size[1]) / max(size[0],size[1])

def key_pressed(key):
    return pygame.key.get_pressed()[_key_dict[key]]

def colliding(entity1,entity2,collider1 = None,collider2 = None):
        if collider1 == None and collider2 == None:
            horizontal_overlap = min(entity1.collider.right,entity2.collider.right) - max(entity1.collider.left,entity2.collider.left)
            vertical_overlap = min(entity1.collider.top,entity2.collider.top) - max(entity1.collider.bottom,entity2.collider.bottom)
        
            colliding = round(horizontal_overlap,15) > 0 and round(vertical_overlap,15) > 0

            return CollidingType(colliding)


class CollidingType:
    def __init__(self,colliding):
        self.colliding = colliding

    def __bool__(self):
        return self.colliding
    
    def __repr__(self):
        return f"{self.colliding}"

def _get_info():
    from teon.core import Teon
    main = Teon._instance
    return {"size":main._window.size,"ctx":main._ctx,"prog":main._prog,"scale_def":scale_def()}

def load_image(path):
    img = Image.open(path).convert("RGBA")
    img_data = img.transpose(Image.FLIP_TOP_BOTTOM).tobytes()
    img_width,img_height = img.size

    tex = _get_info()["ctx"].texture((img_width, img_height), 4, img_data)
    tex.filter = (moderngl.NEAREST, moderngl.NEAREST)

    return tex