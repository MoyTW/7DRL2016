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
        self.summary = self._build_summary()

    def _build_summary(self):
        (x, y) = self.center()
        top_line = self.name + ': (' + str(x) + ',' + str(y) + ')'

        item_names = map(lambda i: i.name, self._items)
        item_line = 'Items: ' + ','.join(item_names)

        enemy_names = map(lambda e: e.name, self._enemies)
        enemy_line = 'Enemies: ' + ','.join(enemy_names)

        return top_line + '\n' + enemy_line + '\n' + item_line + '\n'

    def center(self):
        return (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2

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

    def finalize(self):
        if not self._finalized:
            self.summary = self._build_summary()
            self._finalized = True
            self._enemies = None
            self._items = None
