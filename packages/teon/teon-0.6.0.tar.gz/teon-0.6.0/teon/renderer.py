from teon.functions import _get_info


class Renderer:
    _instance = 0
    def __init__(self):
        self.levels = []
        self.active_level = None

        self._no_levels = []

        Renderer._instance = self

    def _update_info(self):
        for level in self.levels:
            for entity in level:
                entity._info = _get_info()
                entity._recalculate_vertices()

    def _update_lists(self,entity):
        for level in self.levels:
            if entity in level.entities:
                level.entities.pop(entity)

    def add(self,level):
        x = True
        for l in self.levels:
            if level.index == l.index:
                x = False
        if x:
            self.levels.append(level)

        added = []
        for ent in self._no_levels:
            if ent.level_index == level.index:
                level.entities.append(ent)
                added.append(ent)
        for ent in added:
            self._no_levels.pop(self._no_levels.index(ent))

    def set_active_level(self,index):
        for level in self.levels:
            if level.index == index:
                level.active = True
                self.active_level = level
            else:
                level.active = False

    def _add_entity(self,entity):
        try:
            self.get_level(entity.level_index).add(entity)
        except AttributeError:
            self._no_levels.append(entity)

    def get_level(self,index):
        for level in self.levels:
            if level.index == index:
                return level
            
    def _update(self):
        for ent in self.active_level:
            ent.update()
            ent._update()

    def _render(self):
        self.active_level._draw()