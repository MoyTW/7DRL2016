import libtcodpy as libtcod
import math
import render


def is_blocked(x, y, _game_map, _objects):
    if _game_map[x][y].blocked:
        return True
    for obj in _objects:
        if obj.blocks and obj.x == x and obj.y == y:
            return True
    return False


class Object(object):
    def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, is_projectile=False, fighter=None,
                 ai=None, item=None, equipment=None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.always_visible = always_visible
        self.is_projectile = is_projectile

        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.item = item
        if self.item:
            self.item.owner = self

        self.equipment = equipment
        if self.equipment:
            self.equipment.owner = self
            if not self.item:
                raise ValueError('Cannot construct with an Item and Equipment! Use Equipment only!')

    def move(self, dx, dy, game_map, objects):
        new_x = self.x + dx
        new_y = self.y + dy
        blocked = is_blocked(new_x, new_y, game_map, objects)
        # SCOPING DEAR OH GOD WHY FIX THIS AFTER THE TUTORIAL
        if not blocked:
            self.x += dx
            self.y += dy
        return blocked

    # TODO: Pull AI logic out of base Object class!
    # TODO: Take other instead of x/y!
    def move_towards(self, target_x, target_y, game_map, objects):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        return self.move(dx, dy, game_map, objects)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def draw(self, console, fov_map, game_map, camera_x, camera_y):
        if libtcod.map_is_in_fov(fov_map, self.x, self.y) or \
                (self.always_visible and game_map[self.x][self.y].explored):
            (x, y) = render.to_camera_coordinates(self.x, self.y, camera_x, camera_y)

            if x is not None:
                libtcod.console_set_default_foreground(console, self.color)
                libtcod.console_put_char(console, x, y, self.char, libtcod.BKGND_NONE)

    def clear(self, console, camera_x, camera_y):
        (x, y) = render.to_camera_coordinates(self.x, self.y, camera_x, camera_y)
        libtcod.console_put_char(console, x, y, ' ', libtcod.BKGND_NONE)

    def send_to_back(self, _objects):
        _objects.remove(self)
        _objects.insert(0, self)