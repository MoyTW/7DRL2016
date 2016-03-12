import libtcodpy as libtcod
from constants import *  # lol
import math


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


def from_dungeon_level(dungeon_level, table):
    """Given a table, return the value for the current dungeon level.
    :param _dungeon_level: The dungeon level to draw from the table for
    :param table: The table, formatted as a list of [value, level] pairs.
    :return: The value for the current dungeon level
    """
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0


# TODO: This is a dumb way of doing it
def calculate_circle(x, y, distance):
    xmin = x - distance
    xmax = x + distance
    ymin = y - distance
    ymax = y + distance

    tiles = []
    for _x in range(xmin, xmax + 1):
        for _y in range(ymin, ymax + 1):
            dx = _x - x
            dy = _y - y
            _distance = int(math.sqrt(dx ** 2 + dy ** 2))
            if distance == _distance:
                tiles.append([_x, _y])
    return tiles


def enemies_in_range(player, objects, max_range):
    enemies = []

    for obj in objects:
        if obj.fighter and obj.ai and not obj.is_projectile and not obj == player:
            dist = player.distance_to(obj)
            if dist <= max_range:
                enemies.append(obj)
    return enemies
