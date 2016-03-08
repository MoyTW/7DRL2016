import libtcodpy as libtcod
import math
import textwrap
import shelve
from constants import *  # TODO: Bad programmer!
import render
from utils import LinePath


class Tile(object):
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.explored = False

        # That's...basically shadowing. Reassignment! Hiss! Boo!
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight


class Rect(object):
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        return (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2

    def intersect(self, other):
        return self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1


def is_blocked(gm, x, y):
    if gm[x][y].blocked:
        return True
    for o in objects:
        if o.blocks and o.x == x and o.y == y:
            return True
    return False


def create_room(gm, room):
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            gm[x][y].blocked = False
            gm[x][y].block_sight = False


def create_h_tunnel(gm, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        gm[x][y].blocked = False
        gm[x][y].block_sight = False


def create_v_tunnel(gm, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        gm[x][y].blocked = False
        gm[x][y].block_sight = False


def place_objects(gm, room):
    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])
    monster_chances = {'orc': 1,
                       'troll': from_dungeon_level([[9999, 1], [30, 5], [60, 7]])}  # TODO: Enum?

    max_items = from_dungeon_level([[2, 1], [3, 4]])
    item_chances = {'heal': 35,
                    'lightning': from_dungeon_level([[15, 1], [30, 3], [45, 5]]),
                    'fireball': from_dungeon_level([[5, 2], [25, 5]]),
                    'confuse': from_dungeon_level([[5, 3], [25, 6]]),
                    'sword': 25,
                    'shield': 25}  # TODO: Enum?

    num_monsters = libtcod.random_get_int(0, 0, max_monsters)
    for _ in range(num_monsters):
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        if not is_blocked(gm, x, y):
            choice = random_choice(monster_chances)

            if choice == 'orc':
                fighter_component = Fighter(hp=10, defense=0, power=3, xp=35, death_function=monster_death)
                ai_component = BasicMonster()

                monster = Object(x, y, 'o', 'orc', libtcod.desaturated_green, blocks=True, fighter=fighter_component,
                                 ai=ai_component)
            elif choice == 'troll':
                fighter_component = Fighter(hp=10, defense=0, power=3, xp=100, death_function=monster_death)
                ai_component = TosserMonster()

                monster = Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True, fighter=fighter_component,
                                 ai=ai_component)

            objects.append(monster)

    # Place items
    num_items = libtcod.random_get_int(0, 0, max_items)
    for _ in range(num_items):
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        if not is_blocked(gm, x, y):
            choice = random_choice(item_chances)

            if choice == 'heal':
                item_component = Item(use_function=cast_heal)
                item = Object(x, y, '!', 'healing potion', libtcod.violet, always_visible=True, item=item_component)
            elif choice == 'lightning':
                item_component = Item(use_function=cast_lightning)
                item = Object(x, y, '#', 'scroll of lightning bolt', libtcod.light_yellow, always_visible=True,
                              item=item_component)
            elif choice == 'fireball':
                item_component = Item(use_function=cast_fireball)
                item = Object(x, y, '#', 'scroll of fireball', libtcod.orange, always_visible=True, item=item_component)
            elif choice == 'confuse':
                item_component = Item(use_function=cast_confuse)
                item = Object(x, y, '#', 'scroll of confuse', libtcod.light_blue, always_visible=True,
                              item=item_component)
            elif choice == 'sword':
                equipment_component = Equipment(slot='right hand', power_bonus=3)  # TODO: Slot as string
                item = Object(x, y, '/', 'sword', libtcod.sky, equipment=equipment_component)
            elif choice == 'shield':
                equipment_component = Equipment(slot='left hand', defense_bonus=1)  # TODO: Slot as string
                item = Object(x, y, '[', 'shield', libtcod.sky, equipment=equipment_component)

            objects.append(item)
            item.send_to_back()


def make_game_map():
    # OH GOD! WHAT IS SCOPE EVEN
    global objects, stairs

    objects = [player]

    gm = [[Tile(True)
           for _ in range(MAP_HEIGHT)]
          for _ in range(MAP_WIDTH)]

    rooms = []
    # You could just use the count of rooms here, couldn't you?
    num_rooms = 0

    for r in range(MAX_ROOMS):
        # Size of room
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        # Position of room
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        new_room = Rect(x, y, w, h)

        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            create_room(gm, new_room)
            (new_x, new_y) = new_room.center()

            place_objects(gm, new_room)

            if num_rooms == 0:
                player.x = new_x
                player.y = new_y
            else:
                # Connect to the last room in the room vector
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                if libtcod.random_get_int(0, 0, 1):
                    create_h_tunnel(gm, prev_x, new_x, prev_y)
                    create_v_tunnel(gm, prev_y, new_y, new_x)
                else:
                    create_v_tunnel(gm, prev_y, new_y, new_x)
                    create_h_tunnel(gm, prev_x, new_x, prev_y)

            rooms.append(new_room)
            num_rooms += 1

    # TODO: Having trouble keeping track of scope/assignment!
    stairs = Object(new_x, new_y, '<', 'stairs', libtcod.white, always_visible=True,)
    objects.append(stairs)
    stairs.send_to_back()

    return gm


def random_choice_index(chances):
    """ Given a list of probabilities, chooses the index of one according to their values. Technically can take any list
    of numbers, but probabilities are the most intuitive.

    :param chances: The list of probabilities (i.e. [15, 20, 15, 50])
    :return: The index of the chosen probability
    """
    dice = libtcod.random_get_int(0, 1, sum(chances))

    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w
        if dice <= running_sum:
            return choice
        choice += 1


def random_choice(chances_dict):
    chances = chances_dict.values()
    strings = chances_dict.keys()
    return strings[random_choice_index(chances)]


# TODO: Pass the dang thing in
def from_dungeon_level(table):
    """Given a table, return the value for the current dungeon level.
    :param table: The table, formatted as a list of [value, level] pairs.
    :return: The value for the current dungeon level
    """
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0


# Object is using 'con' as the buffer, which is unbound! Does that...work?
class Object(object):
    def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None, item=None,
                 equipment=None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.always_visible = always_visible

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

            # TODO: Equipment must have an Item as well - bit of a mess here!
            if self.item:
                raise ValueError('Cannot construct with an Item and Equipment! Use Equipment only!')
            self.item = Item()
            self.item.owner = self

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        blocked = is_blocked(game_map, new_x, new_y)  # TODO: Scoping!
        # SCOPING DEAR OH GOD WHY FIX THIS AFTER THE TUTORIAL
        if not blocked:
            self.x += dx
            self.y += dy
        return blocked


    # TODO: Pull AI logic out of base Object class!
    # TODO: Take other instead of x/y!
    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        return self.move(dx, dy)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    # TODO: Have draw take the buffer to draw to as a parameter!
    def draw(self):
        if libtcod.map_is_in_fov(fov_map, self.x, self.y) or \
                (self.always_visible and game_map[self.x][self.y].explored):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    # TODO: Have clear take the buffer to draw to as a parameter!
    def clear(self):
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

    def send_to_back(self):
        global objects
        objects.remove(self)
        objects.insert(0, self)


class Fighter(object):
    def __init__(self, hp, defense, power, xp, death_function=None):
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp
        self.death_function = death_function

    @property
    def max_hp(self):
        bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
        return self.base_max_hp + bonus

    @property
    def defense(self):
        bonus = sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner))
        return self.base_defense + bonus

    @property
    def power(self):
        bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
        return self.base_power + bonus

    def attack(self, target):
        damage = self.power - target.fighter.defense
        if damage > 0:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage), libtcod.yellow)
            target.fighter.take_damage(damage)
        else:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it does no damage', libtcod.green)

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage

        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner)
                # TODO: Don't overload xp to be both how much you have and how much you're worth!
                if self.owner != player:
                    player.fighter.xp += self.xp

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp


class BasicMonster(object):
    def take_turn(self):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)


class TosserMonster(object):
    def take_turn(self):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            cast_throw_rock(caster=monster, target=player)


class ProjectileAI(object):
    def __init__(self, x, y, target_x, target_y, _objects):
        self.path = LinePath(x, y, target_x, target_y)
        self.objects = _objects

    def take_turn(self):
        monster = self.owner

        (next_x, next_y) = self.path.step()
        blocked = monster.move_towards(next_x, next_y)

        if blocked:
            for obj in objects:  # TODO: Ugh this is still gnarly
                if obj.x == next_x and obj.y == next_y and obj.fighter and obj != monster:
                    monster.fighter.attack(obj)
                    break
            monster.fighter.death_function(monster)


class ConfusedMonster(object):
    def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.num_turns > 0:
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
        else:
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)


class Item(object):
    def __init__(self, use_function=None):
        self.use_function = use_function

    def pick_up(self):
        if len(inventory) >= 26:
            message('Your inventory is full! Cannot pick up ' + self.owner.name + '.', libtcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', libtcod.green)

            # Auto-equip picked-up items
            equipment = self.owner.equipment
            if equipment and get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()

    def use(self):
        # TODO: Special case for equipment - a bit of a mess!
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return

        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used!')
        else:
            if self.use_function() != 'cancelled':  # TODO: please stop using strings for this!
                inventory.remove(self.owner)

    def drop(self):
        # Special case: unequip equipped item before dropping
        if self.owner.equipment:
            self.owner.equipment.dequip()

        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        self.owner.send_to_back()


class Equipment(object):
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.slot = slot
        self.is_equipped = False
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus

    def toggle_equip(self):
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):
        # Unequip previous item in slot
        old_equipment = get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()

        self.is_equipped = True
        message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)

    def dequip(self):
        if not self.is_equipped:
            return
        self.is_equipped = False
        message('Dequipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_yellow)


def get_equipped_in_slot(slot):
    for obj in inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None


def get_all_equipped(obj):
    if obj == player:
        equipped_list = []
        for item in inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return []


def player_move_or_attack(dx, dy):
    global fov_recompute

    x = player.x + dx
    y = player.y + dy

    target = None
    for obj in objects:
        if obj.fighter and obj.x == x and obj.y == y:
            target = obj
            break

    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute = True


def menu(header, options, width):
    if len(options) > 26:
        raise ValueError('Max menu options is 26 (a-z)')

    # Determine height of menu, in number of lines
    if header == '':
        header_height = 0
    else:
        header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)

    height = len(options) + header_height

    window = libtcod.console_new(width, height)

    # print header
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    # print options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    # blit
    x = SCREEN_WIDTH / 2 - width / 2
    y = SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    # hold window
    libtcod.console_flush()
    k = libtcod.console_wait_for_keypress(True)

    # return selection
    index = k.c - ord('a')
    if 0 <= index < len(options):
        return index
    return None


def inventory_menu(header):
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in inventory:
            text = item.name
            if item.equipment and item.equipment.is_equipped:
                text = text + ' (on ' + item.equipment.slot + ')'
            options.append(text)

    index = menu(header, options, INVENTORY_WIDTH)
    if index is None or len(inventory) == 0:
        return None
    return inventory[index].item


def msgbox(text, width=50):
    menu(text, [], width)


# uuuugh scoping
def handle_keys():
    # TODO: scope
    global key

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'

    if game_state == 'playing':
        # movement keys
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            player_move_or_attack(0, -1)
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            player_move_or_attack(0, 1)
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            player_move_or_attack(-1, 0)
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            player_move_or_attack(1, 0)
        elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
            player_move_or_attack(-1, -1)
        elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
            player_move_or_attack(1, -1)
        elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
            player_move_or_attack(-1, 1)
        elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
            player_move_or_attack(1, 1)
        elif key.vk == libtcod.KEY_KP5:
            pass
        else:
            # Test for other keys? What?
            key_char = chr(key.c)

            # Items don't take a turn to pick up right now
            if key_char == 'g':
                for o in objects:
                    if o.x == player.x and o.y == player.y and o.item:
                        o.item.pick_up()
                        break
            elif key_char == 'i':
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()
            elif key_char == 'd':
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()
            elif key_char == '<':
                if stairs.x == player.x and stairs.y == player.y:
                    next_level()
            elif key_char == 'c':
                level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
                msgbox('Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' +
                       str(player.fighter.xp) + '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' +
                       str(player.fighter.max_hp) + '\nAttack: ' + str(player.fighter.power) + '\nDefense: ' +
                       str(player.fighter.defense),
                       CHARACTER_SCREEN_WIDTH)

            return 'didnt-take-turn'  # TODO: Enum


def check_level_up():
    level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.fighter.xp >= level_up_xp:
        player.level += 1
        player.fighter.xp -= level_up_xp
        message('Level up. Now level ' + str(player.level) + '!', libtcod.green)

        choice = None
        while choice is None:
            choice = menu('Level up! Choose a stat to raise:\n',
                          ['HP + 20, (from ' + str(player.fighter.base_max_hp) + ')',
                           'STR + 1, (from ' + str(player.fighter.base_power) + ')',
                           'DEF + 1, (from ' + str(player.fighter.base_defense) + ')'],
                          LEVEL_SCREEN_WIDTH)
        if choice == 0:
            player.fighter.base_max_hp += 20
            player.fighter.hp += 20
        elif choice == 1:
            player.fighter.base_power += 1
        elif choice == 2:
            player.fighter.base_defense += 1


def player_death(_):
    global game_state
    message('You died!', libtcod.red)
    game_state = 'dead'  # TODO: Enum

    player.char = '%'
    player.color = libtcod.dark_red


def monster_death(monster):
    message(monster.name.capitalize() + ' is dead! You gain ' + str(monster.fighter.xp) + ' xp!', libtcod.red)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'Remains of ' + monster.name
    monster.send_to_back()


def projectile_death(projectile):
    objects.remove(projectile)


def target_tile(max_range=None):
    """Blocks until keypress or click. If the key is ESCAPE or right-click, exits; otherwise waits for a left-click on
    an in-FOV, in-range tile and returns (x, y) of the tile."""
    global key, mouse  # TODO: Scoping
    while True:
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        render.render_all(fov_recompute=fov_recompute, player=player, objects=objects, fov_map=fov_map,
                          game_map=game_map, con=con, panel=panel, game_msgs=game_msgs, dungeon_level=dungeon_level,
                          mouse=mouse)

        (x, y) = (mouse.cx, mouse.cy)

        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return None, None

        if mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and \
                (max_range is None or player.distance(x, y) <= max_range):
            return x, y


def target_monster(max_range=None):
    while True:
        (x, y) = target_tile(max_range)
        if x is None:
            return None

        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != player:  # TODO: Make this check a function
                return obj


# TODO: Generalize to target
def cast_heal():
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health!', libtcod.red)
        return 'cancelled'  # TODO: const not str

    message('You are healed for ' + str(HEAL_AMOUNT) + '!', libtcod.light_violet)
    player.fighter.heal(HEAL_AMOUNT)


def closest_monster(max_range):
    closest_enemy = None
    closest_dist = max_range + 1

    for obj in objects:
        if obj.fighter and not obj == player and libtcod.map_is_in_fov(fov_map, obj.x, obj.y):
            dist = player.distance_to(obj)
            if dist <= closest_dist:
                closest_enemy = obj
                closest_dist = dist

    return closest_enemy


def cast_lightning():
    monster = closest_monster(LIGHTNING_RANGE)

    if monster is None:
        message('No valid targets for Lightning spell!', libtcod.red)
        return 'cancelled'  # TODO: fix this

    message('Lightning used on ' + monster.name + ' for ' + str(LIGHTNING_DAMAGE) + ' damage!', libtcod.light_yellow)
    monster.fighter.take_damage(LIGHTNING_DAMAGE)


def cast_fireball():
    message('Left-click a tile to target the Fireball spell, ESC/right-click to cancel.', libtcod.orange)
    (x, y) = target_tile()
    if x is None:
        message('Fireball targeting cancelled.', libtcod.orange)
        return 'cancelled'  # TODO: Enum
    message('Fireball at (' + str(x) + ',' + str(y) + ') with radius ' + str(FIREBALL_RADIUS) + '.')

    for obj in objects:
        if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
            message('The ' + obj.name + ' takes ' + str(FIREBALL_DAMAGE) + ' damage from the fireball.', libtcod.orange)
            obj.fighter.take_damage(FIREBALL_DAMAGE)


def cast_confuse():
    message('Left-click on the confuse target, ESC/right-click to cancel.', libtcod.light_blue)
    monster = target_monster(CONFUSE_RANGE)
    if monster is None:
        message('Confuse cancelled.', libtcod.light_blue)
        return 'cancelled'  # TODO: enum

    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster
    message('Confused ' + monster.name + '!', libtcod.light_blue)


def cast_throw_rock(caster, target):
    fighter_component = Fighter(hp=1, defense=0, power=0, xp=0, death_function=projectile_death)
    ai_component = ProjectileAI(caster.x, caster.y, target.x, target.y, objects)
    projectile = Object(caster.x, caster.y, '*', 'rock', libtcod.grey, blocks=False, fighter=fighter_component,
                        ai=ai_component)
    objects.append(projectile)


def save_game():
    save_file = shelve.open('save_game', 'n')
    save_file['game_map'] = game_map
    save_file['objects'] = objects
    save_file['player_index'] = objects.index(player)
    save_file['inventory'] = inventory
    save_file['game_msgs'] = game_msgs
    save_file['game_state'] = game_state
    save_file['stairs_index'] = objects.index(stairs)
    save_file['dungeon_level'] = dungeon_level
    save_file.close()


def load_game():
    global game_map, objects, player, inventory, game_msgs, game_state, stairs, dungeon_level

    save_file = shelve.open('save_game', 'r')
    game_map = save_file['game_map']
    objects = save_file['objects']
    player = objects[save_file['player_index']]
    inventory = save_file['inventory']
    game_msgs = save_file['game_msgs']
    game_state = save_file['game_state']
    stairs = objects[save_file['stairs_index']]
    dungeon_level = save_file['dungeon_level']
    save_file.close()

    initialize_fov()


def message(new_msg, color=libtcod.white):
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        game_msgs.append((line, color))


def clear_objects():
    for o in objects:
        o.clear()


# =================================================== MAIN LOOP ==================================================
def new_game():
    global player, inventory, game_msgs, game_state, dungeon_level, game_map

    player_fighter = Fighter(hp=30, defense=2, power=2, xp=0, death_function=player_death)  # TODO: Don't overload xp!
    player = Object(0, 0, '@', 'player', libtcod.white, blocks=True, fighter=player_fighter)

    # TODO: Don't just add random properties that's silly.
    player.level = 1

    dungeon_level = 1
    game_map = make_game_map()
    initialize_fov()

    game_state = 'playing'  # TODO: Enum?
    inventory = []

    game_msgs = []
    message('Initial Message')

    # Initial equipment
    equipment_component = Equipment(slot='right hand', power_bonus=2)
    obj = Object(0, 0, '-', 'dagger', libtcod.sky, equipment=equipment_component)
    inventory.append(obj)
    equipment_component.equip()
    obj.always_visible = True


def next_level():
    global dungeon_level, game_map

    message('Healing before going down to the next level.', libtcod.light_violet)
    player.fighter.heal(player.fighter.max_hp / 2)

    dungeon_level += 1
    message('Going down! Entering level ' + str(dungeon_level), libtcod.white)
    game_map = make_game_map()
    initialize_fov()


def initialize_fov():
    global fov_recompute, fov_map

    fov_recompute = True
    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not game_map[x][y].block_sight, not game_map[x][y].blocked)

    libtcod.console_clear(con)


def play_game():
    global key, mouse

    mouse = libtcod.Mouse()
    key = libtcod.Key()
    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        libtcod.console_set_default_foreground(0, libtcod.white)

        render.render_all(fov_recompute=fov_recompute, player=player, objects=objects, fov_map=fov_map,
                          game_map=game_map, con=con, panel=panel, game_msgs=game_msgs, dungeon_level=dungeon_level,
                          mouse=mouse)
        libtcod.console_flush()

        check_level_up()

        clear_objects()

        player_action = handle_keys()
        if player_action == 'exit':
            save_game()
            break

        if game_state == 'playing' and player_action != 'didnt-take-turn':
            for o in objects:
                if o.ai:
                    o.ai.take_turn()


def main_menu():
    img = libtcod.image_load('star.png')

    while not libtcod.console_is_window_closed():
        # background image
        libtcod.image_blit_2x(img, 0, 0, 0)

        # title and credits
        libtcod.console_set_default_foreground(0, libtcod.red)
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER, 'TEST GAME')
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2-3, libtcod.BKGND_NONE, libtcod.CENTER, 'by MoyTW')

        # menu + choice
        choice = menu('', ['New game', 'Continue game', 'Quit'], 24)
        if choice == 0:
            new_game()
            play_game()
        elif choice == 1:
            try:
                load_game()
            except:
                msgbox('\n Error loading game.\n', 24)
                continue
            play_game()
        elif choice == 2:
            break

# Set font
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

# Initialize windows/buffers
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'tutorial roguelike! whooo!', False)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

# I don't want this to be real-time, so this line effectively does nothing!
libtcod.sys_set_fps(LIMIT_FPS)

main_menu()
