import utils
from constants import *  # TODO: practices not so great maybe?

L0_ENCOUNTER = 0
L1_ENCOUNTER = 1
L2_ENCOUNTER = 2
L3_ENCOUNTER = 3
L4_ENCOUNTER = 4
L5_ENCOUNTER = 5
L6_ENCOUNTER = 6

SCOUT_ENCOUNTER = 'scout encounter'
SCOUT_PAIR_ENCOUNTER = 'scout pair encounter'
GUNSHIP_ENCOUNTER = 'gunship encounter'
SCOUT_TRIO_ENCOUNTER = 'scout trio encounter'

PLACEHOLDER_ENCOUNTER = 'placeholder'

encounters_to_ship_lists = {
    SCOUT_ENCOUNTER: [SCOUT],
    SCOUT_PAIR_ENCOUNTER: [SCOUT, SCOUT],
    SCOUT_TRIO_ENCOUNTER: [SCOUT, SCOUT, SCOUT],
    GUNSHIP_ENCOUNTER: [GUNSHIP],
    PLACEHOLDER_ENCOUNTER: ['placeholder']
}

L0_ENCOUNTER_TABLE = {SCOUT_ENCOUNTER: 50,
                      SCOUT_PAIR_ENCOUNTER: 100,
                      SCOUT_TRIO_ENCOUNTER: 50,
                      GUNSHIP_ENCOUNTER: 50}
L1_ENCOUNTER_TABLE = {PLACEHOLDER_ENCOUNTER: 50}
L2_ENCOUNTER_TABLE = {PLACEHOLDER_ENCOUNTER: 50}
L3_ENCOUNTER_TABLE = {PLACEHOLDER_ENCOUNTER: 50}
L4_ENCOUNTER_TABLE = {PLACEHOLDER_ENCOUNTER: 50}
L5_ENCOUNTER_TABLE = {PLACEHOLDER_ENCOUNTER: 50}
L6_ENCOUNTER_TABLE = {PLACEHOLDER_ENCOUNTER: 50}

ENCOUNTERS_TO_ENCOUNTER_TABLES = {L0_ENCOUNTER: L0_ENCOUNTER_TABLE,
                                  L1_ENCOUNTER: L1_ENCOUNTER_TABLE,
                                  L2_ENCOUNTER: L2_ENCOUNTER_TABLE,
                                  L3_ENCOUNTER: L3_ENCOUNTER_TABLE,
                                  L4_ENCOUNTER: L4_ENCOUNTER_TABLE,
                                  L5_ENCOUNTER: L5_ENCOUNTER_TABLE,
                                  L6_ENCOUNTER: L6_ENCOUNTER_TABLE}

# This table is kind of silly in that there's a much better way to represent it! If you have time (you won't)
# Scouting parties, fighter patrols, or gunships
L0_ENCOUNTER_CHANCES = [[20, 1], [10, 2], [05, 3], [00, 4], [00, 5], [00, 6], [00, 7], [00, 8], [00, 9]]
# Gunships, grouped gunships, or corvettes
L1_ENCOUNTER_CHANCES = [[10, 1], [20, 2], [10, 3], [05, 4], [00, 5], [00, 6], [00, 7], [00, 8], [00, 9]]
# Corvettes, frigates, or recon in force parties
L2_ENCOUNTER_CHANCES = [[05, 1], [10, 2], [20, 3], [10, 4], [05, 5], [00, 6], [00, 7], [00, 8], [00, 9]]
# Destroyers, corvette groups, or frigates
L3_ENCOUNTER_CHANCES = [[00, 1], [05, 2], [10, 3], [20, 4], [10, 5], [05, 6], [00, 7], [00, 8], [00, 9]]
# Escorted frigates, destroyers, and cruisers
L4_ENCOUNTER_CHANCES = [[00, 1], [00, 2], [05, 3], [10, 4], [20, 5], [10, 6], [05, 7], [00, 8], [00, 9]]
# Escorted minor battle groups
L5_ENCOUNTER_CHANCES = [[00, 1], [00, 2], [00, 3], [05, 4], [10, 5], [20, 6], [10, 7], [05, 8], [00, 9]]
# Full battle groups with a range of ships
L6_ENCOUNTER_CHANCES = [[00, 1], [00, 2], [00, 3], [00, 4], [05, 5], [10, 6], [20, 7], [10, 8], [05, 9]]


def choose_encounter_for_level(level):
    table = {L0_ENCOUNTER: utils.from_dungeon_level(level, L0_ENCOUNTER_CHANCES),
             L1_ENCOUNTER: utils.from_dungeon_level(level, L1_ENCOUNTER_CHANCES),
             L2_ENCOUNTER: utils.from_dungeon_level(level, L2_ENCOUNTER_CHANCES),
             L3_ENCOUNTER: utils.from_dungeon_level(level, L3_ENCOUNTER_CHANCES),
             L4_ENCOUNTER: utils.from_dungeon_level(level, L4_ENCOUNTER_CHANCES),
             L5_ENCOUNTER: utils.from_dungeon_level(level, L5_ENCOUNTER_CHANCES),
             L6_ENCOUNTER: utils.from_dungeon_level(level, L6_ENCOUNTER_CHANCES)}
    encounter_level = utils.random_choice(table)
    encounter_table = ENCOUNTERS_TO_ENCOUNTER_TABLES[encounter_level]
    encounter = utils.random_choice(encounter_table)
    return encounters_to_ship_lists[encounter]
