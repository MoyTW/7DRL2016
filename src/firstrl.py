import libtcodpy as libtcod
import textwrap
import shelve
from constants import *  # TODO: Bad programmer!
from render import Renderer
from paths import LinePath, ReversePath
from entities import Object, is_blocked, Fighter
from ais import ProjectileAI
from game_map import Tile, Zone
import utils
import tables


def place_objects(gm, zone, safe=False):
    if not safe:
        enemies = tables.choose_encounter_for_level(dungeon_level)
    else:
        enemies = []
    for choice in enemies:
        (x, y) = zone.random_coordinates()

        if not is_blocked(x, y, gm, objects):
            if choice == SCOUT:
                fighter_component = Fighter(player=player, hp=10, defense=0, power=0, xp=30, base_speed=75,
                                            death_function=monster_death)
                ai_component = ScoutMonster()
                monster = Object(x, y, 'S', SCOUT, libtcod.darker_green, blocks=True, fighter=fighter_component,
                                 ai=ai_component)
            elif choice == FIGHTER:
                fighter_component = Fighter(player=player, hp=30, defense=0, power=0, xp=50, base_speed=125,
                                            death_function=monster_death)
                ai_component = FighterMonster()
                monster = Object(x, y, 'F', FIGHTER, libtcod.darker_green, blocks=True, fighter=fighter_component,
                                 ai=ai_component)
            elif choice == GUNSHIP:
                fighter_component = Fighter(player=player, hp=50, defense=4, power=3, xp=100, base_speed=100,
                                            death_function=monster_death)
                ai_component = GunshipMonster()
                monster = Object(x, y, 'G', GUNSHIP, libtcod.darker_green, blocks=True, fighter=fighter_component,
                                 ai=ai_component)
            elif choice == FRIGATE:
                fighter_component = Fighter(player=player, hp=150, defense=10, power=3, xp=200, base_speed=250,
                                            death_function=monster_death)
                ai_component = FrigateMonster()
                monster = Object(x, y, 'R', FRIGATE, libtcod.darker_green, blocks=True, fighter=fighter_component,
                                 ai=ai_component)
            elif choice == DESTROYER:
                fighter_component = Fighter(player=player, hp=200, defense=15, power=0, xp=500, base_speed=300,
                                            death_function=monster_death)
                ai_component = DestroyerMonster()
                monster = Object(x, y, 'D', DESTROYER, libtcod.darker_green, blocks=True,
                                 fighter=fighter_component, ai=ai_component)
            elif choice == CRUISER:
                fighter_component = Fighter(player=player, hp=300, defense=10, power=0, xp=1000, base_speed=400,
                                            death_function=monster_death)
                ai_component = CruiserMonster()
                monster = Object(x, y, 'C', CRUISER, libtcod.darker_green, blocks=True,
                                 fighter=fighter_component, ai=ai_component)
            elif choice == CARRIER:
                fighter_component = Fighter(player=player, hp=500, defense=0, power=0, xp=2000, base_speed=200,
                                            death_function=monster_death)
                ai_component = CarrierMonster()
                monster = Object(x, y, 'A', CARRIER, libtcod.darker_green, blocks=True,
                                 fighter=fighter_component, ai=ai_component)
            elif choice == 'placeholder':
                print('placeholder encounter')
                fighter_component = Fighter(player=player, hp=10, defense=0, power=0, xp=30, base_speed=75,
                                            death_function=projectile_death)
                ai_component = ScoutMonster()
                monster = Object(x, y, 'P', 'placeholder', libtcod.darker_green, blocks=True, fighter=fighter_component,
                                 ai=ai_component)

            zone.register_enemy(monster)
            objects.append(monster)

    max_items = utils.from_dungeon_level(dungeon_level, [[1, 1], [2, 4], [3, 6]])
    item_chances = {ITEM_DUCT_TAPE: 45,
                    ITEM_EXTRA_BATTERY: 25,
                    ITEM_RED_PAINT: 10,
                    ITEM_EMP: 10}

    # Place items
    num_items = libtcod.random_get_int(0, 0, max_items)
    for _ in range(num_items):
        (x, y) = zone.random_coordinates()

        if not is_blocked(x, y, gm, objects):
            choice = utils.random_choice(item_chances)

            if choice == ITEM_DUCT_TAPE:
                item_component = Item(use_function=use_repair_player)
                item = Object(x, y, 't', ITEM_DUCT_TAPE, libtcod.violet, always_visible=True, item=item_component)
            elif choice == ITEM_EXTRA_BATTERY:
                item_component = Item(use_function=boost_player_power)
                item = Object(x, y, 'b', ITEM_EXTRA_BATTERY, libtcod.light_yellow, always_visible=True,
                              item=item_component)
            elif choice == ITEM_EMP:
                item_component = Item(use_function=cast_area_disable)
                item = Object(x, y, 'p', ITEM_EMP, libtcod.light_blue, always_visible=True,
                              item=item_component)
            elif choice == ITEM_RED_PAINT:
                item = Object(x, y, 'r', ITEM_RED_PAINT, libtcod.light_red, always_visible=True,
                              item=Item(use_function=boost_player_speed))

            objects.append(item)
            zone.register_item(item)
            item.send_to_back(objects)

    num_satellites = utils.from_dungeon_level(dungeon_level, SATELLITES_PER_LEVEL)
    for _ in range(num_satellites):
        (x, y) = zone.random_coordinates()

        if not is_blocked(x, y, gm, objects):
            fighter_component = Fighter(player=player, hp=1, defense=9999, power=0, xp=0,
                                        death_function=projectile_death)
            monster = Object(x, y, '#', 'satellite', libtcod.white, blocks=True, fighter=fighter_component)
            objects.append(monster)
            # TODO: Hack!
            gm[x][y].blocked = True


def make_game_map():
    # OH GOD! WHAT IS SCOPE EVEN
    global objects, stairs, zones  # TODO: Haha I'm making it WORSE

    objects = [player]

    gm = [[Tile(False)
           for _ in range(MAP_HEIGHT)]
          for _ in range(MAP_WIDTH)]

    # Create border walls to prevent objects running off the map
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if x == 0 or x == MAP_WIDTH - 2 or x == MAP_WIDTH - 1\
                    or y == 0 or y == MAP_HEIGHT - 2 or x == MAP_HEIGHT - 1:
                gm[x][y].blocked = True
                gm[x][y].block_sight = True

    zones = []

    zone_gen_attempts = 0
    while zone_gen_attempts < MAX_ZONE_GEN_ATTEMPTS and len(zones) < MAX_ZONES:
        # Size of zone
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        # Position of zone
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        new_zone = Zone(x, y, w, h, len(zones))

        failed = False
        for other_zone in zones:
            if new_zone.intersect(other_zone):
                failed = True
                break

        if not failed:
            (new_x, new_y) = new_zone.center()

            place_objects(gm, new_zone, len(zones) == 0)

            if len(zones) == 0:
                player.x = new_x
                player.y = new_y

            zones.append(new_zone)

    # If you're on the last level, generate the diplomat
    if dungeon_level == 10:
        (diplomat_x, diplomat_y) = zones[0].random_unblocked_coordinates(gm, objects)
        fighter_component = Fighter(player=player, hp=10, defense=0, power=0, xp=0, base_speed=50,
                                    death_function=diplomat_death)
        ai_component = DiplomatMonster()
        diplomat = Object(diplomat_x, diplomat_y, 'D', DIPLOMAT, libtcod.darker_green, blocks=True, fighter=fighter_component,
                          ai=ai_component)
        objects.append(diplomat)

    # Generate the stairs
    stairs_zone = zones[libtcod.random_get_int(0, 1, len(zones) - 1)]
    (stairs_x, stairs_y) = stairs_zone.random_unblocked_coordinates(gm, objects)
    stairs = Object(stairs_x, stairs_y, 'J', 'jump point', libtcod.white, always_visible=True)
    stairs_zone.register_item(stairs)
    objects.append(stairs)
    stairs.send_to_back(objects)

    # Generate the intel
    intel_zone = zones[libtcod.random_get_int(0, 1, len(zones) - 1)]
    (intel_x, intel_y) = intel_zone.random_unblocked_coordinates(gm, objects)

    # Intel gives you vision of the next level
    def use_fn():
        zone_intel[dungeon_level + 1] = True
        message('Intel for zones in Sector ' + str(dungeon_level + 1) + ' loaded!', libtcod.light_violet)

    intel = Object(intel_x, intel_y, 'I', 'intel', libtcod.light_violet, always_visible=True,
                   item=Item(auto_use=True, use_function=use_fn))
    intel_zone.register_item(intel)
    objects.append(intel)
    intel.send_to_back(objects)

    # Make Zones read-only (well not really, but the summaries become read-only)
    for zone in zones:
        zone.finalize(True)
        # zone.finalize(zone_intel.get(dungeon_level, False))

    return gm


class MonsterAI(object):
    def __init__(self, activated=False):
        self.activated = activated
        self.owner = None

    def is_activated(self):
        if self.activated:
            return True
        elif libtcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y):
            self.activated = True
            return True
        else:
            return False

    def take_turn(self):
        raise NotImplementedError('Subclass this before usage please.')


class ScoutMonster(MonsterAI):
    def __init__(self, activated=False):
        super(ScoutMonster, self).__init__(activated=activated)

    def take_turn(self):
        if self.is_activated():
            if self.owner.distance_to(player) >= 5:
                self.owner.path_towards(player.x, player.y, game_map, objects, fov_map)
            elif player.fighter.hp > 0:
                fire_small_shotgun(caster=self.owner, target=player, spread=2, pellets=3)


class FighterMonster(MonsterAI):
    def __init__(self, activated=False):
        super(FighterMonster, self).__init__(activated=activated)

    def take_turn(self):
        if self.is_activated():
            self.owner.path_towards(player.x, player.y, game_map, objects, fov_map)
            if player.fighter.hp > 0:
                fire_small_gatling(caster=self.owner, target=player)
                fire_small_gatling(caster=self.owner, target=player)
                fire_small_gatling(caster=self.owner, target=player)


class GunshipMonster(MonsterAI):
    def __init__(self, cooldown=4):
        super(GunshipMonster, self).__init__()
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.move = True

    def take_turn(self):
        if self.is_activated():
            if self.move and self.owner.distance_to(player) >= 5:
                self.owner.path_towards(player.x, player.y, game_map, objects, fov_map)
                self.move = False
            else:
                self.move = True
            if self.current_cooldown == 0:
                fire_small_shotgun(caster=self.owner, target=player)
                self.current_cooldown += self.cooldown
            else:
                fire_small_cannon(caster=self.owner, target=player)
        if self.current_cooldown > 0:
            self.current_cooldown -= 1


class FrigateMonster(MonsterAI):
    def __init__(self):
        super(FrigateMonster, self).__init__()
        self.reverse_cooldown = 3
        self.current_reverse_cooldown = 0

    def take_turn(self):
        if self.is_activated():
            self.owner.path_towards(player.x, player.y, game_map, objects, fov_map)
            if self.current_reverse_cooldown == 0:
                fire_returning_shot(caster=self.owner, target=player)
                fire_small_cannon(caster=self.owner, target=player)
                self.current_reverse_cooldown += self.reverse_cooldown
            else:
                fire_small_cannon(caster=self.owner, target=player)
                fire_small_gatling(caster=self.owner, target=player)
                fire_small_shotgun(caster=self.owner, target=player, pellets=2, spread=3)
        if self.current_reverse_cooldown > 0:
            self.current_reverse_cooldown -= 1


class DestroyerMonster(MonsterAI):
    def __init__(self):
        super(DestroyerMonster, self).__init__()
        self.volly_cooldown = 5
        self.current_cooldown = 0

    def take_turn(self):
        if self.is_activated():
            self.owner.path_towards(player.x, player.y, game_map, objects, fov_map)

            if self.current_cooldown == 0:
                fire_small_shotgun(caster=self.owner, target=player, spread=7, pellets=30)
                fire_small_cannon(caster=self.owner, target=player)
                self.current_cooldown += self.volly_cooldown
            else:
                fire_small_shotgun(caster=self.owner, target=player, spread=1, pellets=2)
        if self.current_cooldown > 0:
            self.current_cooldown -= 1


class CruiserMonster(MonsterAI):
    def __init__(self):
        super(CruiserMonster, self).__init__()
        self.railgun_cooldown = 3
        self.current_railgun_cooldown = 0
        self.flak_cooldown = 10
        self.current_flak_cooldown = 0

    def take_turn(self):
        if self.is_activated():
            # Movement
            if self.owner.distance_to(player) >= 7:
                self.owner.path_towards(player.x, player.y, game_map, objects, fov_map)

            # Always attempt to fire railgun and cannon complement
            fire_small_cannon(caster=self.owner, target=player)
            if self.current_railgun_cooldown == 0:
                fire_railgun(caster=self.owner, target=player)
                self.current_railgun_cooldown += self.railgun_cooldown

            # If the player is too close, flak burst
            if self.owner.distance_to(player) <= 4 and self.current_flak_cooldown == 0:
                fire_small_shotgun(caster=self.owner, target=player, spread=5, pellets=30)
                self.current_flak_cooldown += self.flak_cooldown

        if self.current_railgun_cooldown > 0:
            self.current_railgun_cooldown -= 1
        if self.current_flak_cooldown > 0:
            self.current_flak_cooldown -= 1


# TODO: Make fighters not shoot each other, and path around each other!
class CarrierMonster(MonsterAI):
    def __init__(self):
        super(CarrierMonster, self).__init__()
        self.launch_table = {SCOUT: 5,
                             FIGHTER: 10}
        self.flak_cooldown = 10
        self.current_flak_cooldown = 0

    def take_turn(self):
        if self.is_activated():
            # Launch
            choice = utils.random_choice(self.launch_table)
            # TODO: Use pathfinding here! Otherwise you can spawn into a blocked square!
            (x, y) = LinePath(self.owner.x, self.owner.y, player.x, player.y).project(1)[0]
            if choice == SCOUT:
                fighter_component = Fighter(player=player, hp=10, defense=0, power=0, xp=30, base_speed=75,
                                            death_function=projectile_death)
                ai_component = ScoutMonster(activated=True)
                self.owner = Object(x, y, 'S', SCOUT, libtcod.darker_green, blocks=True, fighter=fighter_component,
                                    ai=ai_component)
            elif choice == FIGHTER:
                fighter_component = Fighter(player=player, hp=30, defense=0, power=0, xp=50, base_speed=125,
                                            death_function=projectile_death)
                ai_component = FighterMonster(activated=True)
                self.owner = Object(x, y, 'F', FIGHTER, libtcod.darker_green, blocks=True,
                                    fighter=fighter_component, ai=ai_component)
            objects.append(self.owner)

            # If the player is too close, flak burst
            if self.owner.distance_to(player) <= 4 and self.current_flak_cooldown == 0:
                fire_small_shotgun(caster=self.owner, target=player, spread=5, pellets=30)
                self.current_flak_cooldown += self.flak_cooldown

        if self.current_flak_cooldown > 0:
            self.current_flak_cooldown -= 1


class DiplomatMonster(object):
    def take_turn(self):
        monster = self.owner

        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            message('Please do not attack! We are a peaceful diplomatic vessel!', libtcod.light_violet)


class DisabledMonster(object):
    def __init__(self, old_ai, num_turns=AREA_DISABLE_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.num_turns > 0:
            self.num_turns -= 1
        else:
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' has managed to restore power!', libtcod.red)


class Item(object):
    def __init__(self, use_function=None, auto_use=False):
        self.use_function = use_function
        self.auto_use = auto_use

    def pick_up(self):
        if self.auto_use:
            inventory.append(self.owner)
            objects.remove(self.owner)
            self.use()
        elif len(inventory) >= 26:
            message('Your inventory is full! Cannot pick up ' + self.owner.name + '', libtcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', libtcod.green)

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
            if self.use_function() != ACTION_CANCELLED:
                inventory.remove(self.owner)

    def drop(self):
        # Special case: unequip equipped item before dropping
        if self.owner.equipment:
            self.owner.equipment.dequip()

        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        self.owner.send_to_back(objects)


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


def player_move(dx, dy):
    player.move(dx, dy, game_map, objects)
    renderer.fov_recompute = True

    closest_enemy = closest_monster(CUTTING_LASER_RANGE)
    if closest_enemy:
        fire_cutting_laser(player, closest_enemy)


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
    libtcod.console_wait_for_keypress(True)  # Necessary to flush input buffer; otherwise will instantly return
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

    if game_state == GAME_STATE_PLAYING:
        # movement keys
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            player_move(0, -1)
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            player_move(0, 1)
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            player_move(-1, 0)
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            player_move(1, 0)
        elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
            player_move(-1, -1)
        elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
            player_move(1, -1)
        elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
            player_move(-1, 1)
        elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
            player_move(1, 1)
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
                       str(player.fighter.defense) + '\nSpeed: ' + str(player.fighter.speed),
                       CHARACTER_SCREEN_WIDTH)
            elif key_char == 'r':
                zone_summaries = map(lambda z: z.summary, zones)
                position_header = 'Your position: (' + str(player.x) + ',' + str(player.y) + ')'
                msg = position_header + '\n\n' + '\n'.join(zone_summaries)
                msgbox(msg)

            return GAME_STATE_DIDNT_TAKE_TURN


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
                           'POWER + 5, (from ' + str(player.fighter.base_power) + ')',
                           'DEFENSE + 1, (from ' + str(player.fighter.base_defense) + ')'],
                          LEVEL_SCREEN_WIDTH)
        if choice == 0:
            player.fighter.base_max_hp += 20
            player.fighter.hp += 20
        elif choice == 1:
            player.fighter.base_power += 5
        elif choice == 2:
            player.fighter.base_defense += 1


def player_death(_):
    global game_state
    message('You have perished!', libtcod.red)
    game_state = GAME_STATE_PLAYER_DEAD

    player.char = '%'
    player.color = libtcod.dark_red
    msgbox("Oh no! Our last hope has perished to the Earthlings! We are doomed! DOOMED!\n\n"
           "What's that you say? We dug up another skiff in subhanger 8392? There's hope yet! Prime it for launch and "
           "find me a new captain!")


def monster_death(monster):
    message(monster.name.capitalize() + ' has been destroyed! You gain ' + str(monster.fighter.xp) + ' xp!',
            libtcod.red)
    objects.remove(monster)


def projectile_death(projectile):
    objects.remove(projectile)


def diplomat_death(diplomat):
    global game_state
    msgbox("You have assassinated the diplomat! You have won the game, congratulations!\n\n"
           "Press any key to exit.")
    game_state = GAME_STATE_VICTORY


def target_tile(max_range=None):
    """Blocks until keypress or click. If the key is ESCAPE or right-click, exits; otherwise waits for a left-click on
    an in-FOV, in-range tile and returns (x, y) of the tile."""
    global key  # TODO: Scoping
    while True:
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        renderer.render_all(player=player, objects=objects, game_map=game_map, con=con, panel=panel,
                            game_msgs=game_msgs, dungeon_level=dungeon_level, mouse=mouse)

        (x, y) = (renderer.camera_x + mouse.cx, renderer.camera_y + mouse.cy)

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


def use_repair_player():
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health!', libtcod.red)
        return 'cancelled'  # TODO: const not str

    message('You are repaired for ' + str(REPAIR_AMOUNT) + '!', libtcod.light_violet)
    player.fighter.heal(REPAIR_AMOUNT)


def closest_monster(max_range):
    closest_enemy = None
    closest_dist = max_range + 1

    for obj in objects:
        if obj.fighter and obj.ai and not obj.is_projectile and not obj == player and \
                libtcod.map_is_in_fov(fov_map, obj.x, obj.y):
            dist = player.distance_to(obj)
            if dist <= closest_dist:
                closest_enemy = obj
                closest_dist = dist

    return closest_enemy


def boost_player_power():
    player.fighter.apply_power_buff(20, 450)
    message('You supercharge your laser! Power +20 for 450 TUs!', libtcod.light_yellow)


def boost_player_speed():
    if player.fighter.speed < 100:
        message("You can't make your ride any redder than it already is!")
        return ACTION_CANCELLED
    else:
        player.fighter.apply_speed_buff(75, 300)
        message("You spray red paint on your ride. You'll move (and fire) four times as fast for the next 300 TUs!")


def cast_area_disable():
    message('Detonated pulse blast! Enemies within a ' + str(AREA_DISABLE_RANGE) + ' tile radius will be disabled!',
            libtcod.light_blue)
    enemies = utils.enemies_in_range(player, objects, AREA_DISABLE_RANGE)
    for enemy in enemies:
        old_ai = enemy.ai
        enemy.ai = DisabledMonster(old_ai)
        enemy.ai.owner = enemy
        message('The ' + enemy.name + ' was disabled for ' + str(AREA_DISABLE_TURNS) + ' turns !', libtcod.light_blue)


def fire_railgun(caster, target):
    fighter_component = Fighter(player=player, hp=1, defense=0, power=15, xp=0, base_speed=20,
                                death_function=projectile_death)
    path = LinePath(caster.x, caster.y, target.x, target.y)
    ai_component = ProjectileAI(path, game_map, objects, message)
    projectile = Object(caster.x, caster.y, 'l', 'railgun slug', libtcod.red, blocks=False, is_projectile=True,
                        fighter=fighter_component, ai=ai_component)
    objects.append(projectile)
    projectile.send_to_back(objects)


def fire_returning_shot(caster, target):
    fighter_component = Fighter(player=player, hp=1, defense=0, power=2, xp=0, base_speed=33,
                                death_function=projectile_death)
    path = ReversePath(caster.x, caster.y, target.x, target.y, overshoot=4)
    ai_component = ProjectileAI(path, game_map, objects, message)
    projectile = Object(caster.x, caster.y, 'r', 'reverser shot', libtcod.red, blocks=False, is_projectile=True,
                        fighter=fighter_component, ai=ai_component)
    objects.append(projectile)
    projectile.send_to_back(objects)


def single_small_shotgun(source_x, source_y, target_x, target_y):
    fighter_component = Fighter(player=player, hp=1, defense=0, power=1, xp=0, base_speed=25,
                                death_function=projectile_death)
    path = LinePath(source_x, source_y, target_x, target_y)
    ai_component = ProjectileAI(path, game_map, objects, message)
    projectile = Object(source_x, source_y, 's', 'small shotgun shell', libtcod.red, blocks=False, is_projectile=True,
                        fighter=fighter_component, ai=ai_component)
    objects.append(projectile)
    projectile.send_to_back(objects)


def fire_small_shotgun(caster, target, spread=5, pellets=5):
    for _ in range(pellets):
        dx = libtcod.random_get_int(0, 0, spread*2 + 1) - 2
        dy = libtcod.random_get_int(0, 0, spread*2 + 1) - 2
        single_small_shotgun(caster.x, caster.y, target.x + dx, target.y + dy)


def fire_small_gatling(caster, target):
    fighter_component = Fighter(player=player, hp=1, defense=0, power=2, xp=0, base_speed=50,
                                death_function=projectile_death)
    path = LinePath(caster.x, caster.y, target.x, target.y)
    ai_component = ProjectileAI(path, game_map, objects, message)
    projectile = Object(caster.x, caster.y, 'g', 'small gatling shell', libtcod.red, blocks=False, is_projectile=True,
                        fighter=fighter_component, ai=ai_component)
    objects.append(projectile)
    projectile.send_to_back(objects)


def fire_small_cannon(caster, target):
    fighter_component = Fighter(player=player, hp=1, defense=0, power=5, xp=0, base_speed=50,
                                death_function=projectile_death)
    path = LinePath(caster.x, caster.y, target.x, target.y)
    ai_component = ProjectileAI(path, game_map, objects, message)
    projectile = Object(caster.x, caster.y, 'c', 'small cannon shell', libtcod.red, blocks=False, is_projectile=True,
                        fighter=fighter_component, ai=ai_component)
    objects.append(projectile)
    projectile.send_to_back(objects)


def fire_cutting_laser(caster, target):
    fighter_component = Fighter(player=player, hp=1, defense=0, power=player.fighter.power, xp=0, base_speed=1,
                                death_function=projectile_death)
    path = LinePath(caster.x, caster.y, target.x, target.y)
    ai_component = ProjectileAI(path, game_map, objects, message)
    projectile = Object(caster.x, caster.y, '*', 'cutting beam', libtcod.red, blocks=False, is_projectile=True,
                        fighter=fighter_component, ai=ai_component)
    objects.append(projectile)
    projectile.send_to_back(objects)


def message(new_msg, color=libtcod.white):
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        game_msgs.append((line, color))


# =================================================== MAIN LOOP ==================================================
def new_game():
    global player, inventory, zone_intel, game_msgs, game_state, dungeon_level, game_map

    game_state = GAME_STATE_PLAYING
    inventory = []
    zone_intel = {1: True}

    # TODO: Don't overload xp!
    # TODO: Hahaha that's a terrible kludge here, creating the fighter and then setting the player to it later!
    # TODO: Seriously this is terrible and The Worst. If you have time fix it please.
    # Though to be fair it is a 7-day thing so you...probably won't, as much as it hurts to admit it.
    player_fighter = Fighter(player=None, hp=30, defense=0, power=25, xp=0, death_function=player_death,
                             inventory=inventory)
    player = Object(0, 0, '@', 'player', libtcod.white, blocks=True, is_player=True, fighter=player_fighter)
    player.fighter.player = player

    # TODO: Don't just add random properties that's silly.
    player.level = 1

    dungeon_level = 1
    game_map = make_game_map()
    initialize_fov()

    game_msgs = []
    message('Good luck, captain! Remember to not die!')


def next_level():
    global dungeon_level, game_map

    message('Healing before going down to the next level.', libtcod.light_violet)
    player.fighter.heal(player.fighter.max_hp / 2)

    dungeon_level += 1
    message('Going down! Entering level ' + str(dungeon_level), libtcod.white)
    game_map = make_game_map()
    initialize_fov()


def initialize_fov():
    global renderer, fov_map

    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not game_map[x][y].block_sight, not game_map[x][y].blocked)

    renderer = Renderer(fov_map, fov_recompute=True)

    libtcod.console_clear(con)


def time_to_next_event(_objects):
    time = 9999
    for obj in _objects:
        if obj.fighter:
            if obj.fighter.time_until_turn < time:
                time = obj.fighter.time_until_turn
    return time


def play_game():
    global key, mouse

    mouse = libtcod.Mouse()
    key = libtcod.Key()

    tutorial = True

    while not libtcod.console_is_window_closed():
        if game_state == GAME_STATE_VICTORY or game_state == GAME_STATE_PLAYER_DEAD:
            break

        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        libtcod.console_set_default_foreground(0, libtcod.white)

        renderer.render_all(player=player, objects=objects, game_map=game_map, con=con, panel=panel,
                            game_msgs=game_msgs, dungeon_level=dungeon_level, mouse=mouse)

        libtcod.console_flush()

        renderer.clear_objects(con, objects)

        if tutorial:
            msgbox("Welcome to the game!\n\n"
                   "You're tasked with a very important mission! The most talented diplomat the Earthlings have is "
                   "travelling to Epsilon Gruis I, where he'll attend peace talks with The Safe Ones and possibly gain "
                   "their support! Obviously this cannot happen, so you must ASSASSINATE THE DIPLOMAT!\n\n"
                   "To reach the diplomat, you must navigate through nine sectors (all crawling with hostiles by the "
                   "way) by using the naturally occurring JUMP POINTS. Our spies have provided INTEL pickups on the way"
                   " that will give you the disposition of the enemy forces in the next sector. If you don't pick up "
                   "the INTEL you'll be flying blind and probably die!\n\n"
                   "Your ship is equipped with a 3-tile cutting laser. End your turn within a distance of 3 to an enemy"
                   " to attack. It's pretty powerful against small ships, but be wary of extended engagements.\n\n"
                   "Good luck captain!\n\n"
                   "CONTROLS:\n"
                   "KEYPAD: Movement\n"
                   "g: pick up an item in your tile\n"
                   "r: view sector reports (DO THIS)\n"
                   "<: jump to the next sector (must be on the jump point)\n",
                   70)
            tutorial = False

        # TODO: Kind of messy way of structuring this!
        time = time_to_next_event(objects)
        for obj in objects:
            if obj.fighter and (obj.ai or obj == player):
                obj.fighter.pass_time(time)

        if player.fighter.time_until_turn == 0:
            check_level_up()
            player_action = handle_keys()
            if player_action == 'exit':
                break
            elif player_action != GAME_STATE_DIDNT_TAKE_TURN:
                player.fighter.end_turn()
        else:
            player_action = None

        if game_state == GAME_STATE_PLAYING and player_action != GAME_STATE_DIDNT_TAKE_TURN:
            for o in objects:
                if o.fighter and o.fighter.time_until_turn == 0 and o.ai:
                    o.ai.take_turn()
                    o.fighter.end_turn()


def main_menu():
    img = libtcod.image_load('star.png')

    while not libtcod.console_is_window_closed():
        # background image
        libtcod.image_blit_2x(img, 0, 0, 0)

        # title and credits
        libtcod.console_set_default_foreground(0, libtcod.white)
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2-4, libtcod.BKGND_DARKEN, libtcod.CENTER,
                                 'A Roguelike Where You Dodge Projectiles')
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2-3, libtcod.BKGND_DARKEN, libtcod.CENTER, 'by MoyTW')

        # menu + choice
        choice = menu('', ['New game', 'Quit'], 24)
        if choice == 0:
            new_game()
            play_game()
        elif choice == 1:
            break

# Set font
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

# Initialize windows/buffers
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'A Roguelike Where You Dodge Projectiles', False)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

# I don't want this to be real-time, so this line effectively does nothing!
libtcod.sys_set_fps(LIMIT_FPS)

libtcod.console_set_fullscreen(True)

main_menu()
