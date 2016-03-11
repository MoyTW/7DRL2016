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


def get_all_equipped(obj, player, inventory):
    if obj == player:
        equipped_list = []
        for item in inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return []


class Fighter(object):
    def __init__(self, player, hp, defense, power, xp, base_speed=100, death_function=None, inventory=None):
        self.player = player  # TODO: This is a nasty kludge
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp
        self.base_speed = base_speed
        self.time_until_turn = self.speed
        self.death_function = death_function
        self.inventory = inventory

    @property
    def max_hp(self):
        bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner, self.player, self.inventory))
        return self.base_max_hp + bonus

    @property
    def defense(self):
        bonus = sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner, self.player, self.inventory))
        return self.base_defense + bonus

    @property
    def power(self):
        bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner, self.player, self.inventory))
        return self.base_power + bonus

    # TODO: Speed-altering equipment?
    @property
    def speed(self):
        return self.base_speed

    def end_turn(self):
        self.time_until_turn = self.speed

    def attack(self, target):
        damage = self.power - target.fighter.defense
        if damage > 0:
            # message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage), libtcod.yellow)
            target.fighter.take_damage(damage)
        else:
            pass
            # message(self.owner.name.capitalize() +
            # ' attacks ' + target.name + ' but it does no damage', libtcod.green)

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage

        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner)
                # TODO: Don't overload xp to be both how much you have and how much you're worth!
                if self.owner != self.player:
                    self.player.fighter.xp += self.xp

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
