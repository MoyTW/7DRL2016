import libtcodpy as libtcod
from entities import is_blocked


class Tile(object):
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.explored = False

        # That's...basically shadowing. Reassignment! Hiss! Boo!
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight


class Zone(object):
    def __init__(self, x, y, w, h, name):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        self.name = 'Zone ' + str(name)

        self._enemies = []
        self._items = []

        self._finalized = False
        self.summary = self._build_summary(False)

    def _build_summary(self, has_intel):
        (x, y) = self.center()
        top_line = self.name + ': (' + str(x) + ',' + str(y) + ')'

        if has_intel:
            item_names = map(lambda i: i.name, self._items)
            item_line = 'Items: ' + ','.join(item_names)

            enemy_names = map(lambda e: e.name, self._enemies)
            enemy_line = 'Enemies: ' + ','.join(enemy_names)
        else:
            item_line = 'Items: UNKNOWN'
            enemy_line = 'Enemies: UNKNOWN'

        return top_line + '\n' + enemy_line + '\n' + item_line + '\n'

    def center(self):
        return (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2

    def random_coordinates(self):
        x = libtcod.random_get_int(0, self.x1 + 1, self.x2 - 1)
        y = libtcod.random_get_int(0, self.y1 + 1, self.y2 - 1)
        return x, y

    def random_unblocked_coordinates(self, game_map, objects):
        (x, y) = self.random_coordinates()
        while is_blocked(x, y, game_map, objects):
            (x, y) = self.random_coordinates()
        return x, y

    def intersect(self, other):
        return self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1

    def register_enemy(self, enemy):
        if not self._finalized:
            self._enemies.append(enemy)
        else:
            raise ValueError('Attempted to register enemy with finalized zone')

    def register_item(self, item):
        if not self._finalized:
            self._items.append(item)
        else:
            raise ValueError('Attempted to register item with finalized Zone')

    def finalize(self, has_intel):
        if not self._finalized:
            self.summary = self._build_summary(has_intel)
            self._finalized = True
            self._enemies = None
            self._items = None
