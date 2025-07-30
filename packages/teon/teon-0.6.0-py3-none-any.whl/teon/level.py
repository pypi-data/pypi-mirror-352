from teon.renderer import Renderer

class Level:
    def __init__(self,index):
        self.index = index
        self.active = False

        self.entities = []

        Renderer._instance.add(self)

        self._renderer = Renderer._instance

    def _draw(self):
        cam_y = self._renderer._core._camera.position.y
        entities = sorted(self.entities, key=lambda ent: (ent.z,-(ent.bottom - (cam_y if getattr(ent, "is_ui", False) else 0))))
        for entity in entities:
            if entity.visible:
                entity._draw()

    def add(self,entity):
        self._renderer._update_lists(entity)
        self.entities.append(entity)

    def __iter__(self):
        return iter(self.entities)
    
    def __len__(self):
        return len(self.entities)