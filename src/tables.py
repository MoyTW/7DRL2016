import utils
from constants import *  # TODO: practices not so great maybe?

L0_ENCOUNTER = 0
L1_ENCOUNTER = 1
L2_ENCOUNTER = 2
L3_ENCOUNTER = 3
L4_ENCOUNTER = 4
L5_ENCOUNTER = 5
L6_ENCOUNTER = 6

EMPTY_ENCOUNTER = 'empty encounter'
SCOUT_ENCOUNTER = 'scout encounter'
SCOUT_PAIR_ENCOUNTER = 'scout pair encounter'
SCOUT_TRIO_ENCOUNTER = 'scout trio encounter'
FIGHTER_ENCOUNTER = 'fighter encounter'
FIGHTER_RECON_ENCOUNTER = 'fighter recon encounter'
FIGHTER_PAIR_ENCOUNTER = 'fighter pair encounter'
FIGHTER_FLIGHT_ENCOUNTER = 'fighter flight encounter'
GUNSHIP_ENCOUNTER = 'gunship encounter'
GUNSHIP_RECON_ENCOUNTER = 'gunship escorted encounter'
GUNSHIP_PAIR_ENCOUNTER = 'gunship pair encounter'
FRIGATE_ENCOUNTER = 'frigate encounter'
DESTROYER_ENCOUNTER = 'destroyer encounter'
CRUISER_ENCOUNTER = 'cruiser encounter'
CARRIER_ENCOUNTER = 'carrier encounter'
FRIGATE_PAIR_ENCOUNTER = 'frigate pair'
FRIGATE_GUNSHIP_ENCOUNTER = 'frigate gunship'
DESTROYER_FIGHTER_ENCOUNTER = 'destroyer fighter'
DESTROYER_FRIGATE_ENCOUNTER = 'destroyer frigate'
CRUISER_PAIR_ENCOUNTER = 'cruiser pair'
CRUISER_FIGHTER_ENCOUNTER = 'cruiser fighter'
CARRIER_SCREEN_ENCOUNTER = 'carrier screen'
CARRIER_DESTROYER_ENCOUNTER = 'carrier destroyer'
CARRIER_TASK_FORCE_ENCOUNTER = 'carrier task force'

PLACEHOLDER_ENCOUNTER = 'placeholder'

encounters_to_ship_lists = {
    EMPTY_ENCOUNTER: [],
    SCOUT_ENCOUNTER: [SCOUT],
    SCOUT_PAIR_ENCOUNTER: [SCOUT, SCOUT],
    SCOUT_TRIO_ENCOUNTER: [SCOUT, SCOUT, SCOUT],
    FIGHTER_ENCOUNTER: [FIGHTER],
    FIGHTER_RECON_ENCOUNTER: [FIGHTER, SCOUT, SCOUT],
    FIGHTER_PAIR_ENCOUNTER: [FIGHTER, FIGHTER],
    FIGHTER_FLIGHT_ENCOUNTER: [FIGHTER, FIGHTER, FIGHTER, FIGHTER],
    GUNSHIP_ENCOUNTER: [GUNSHIP],
    GUNSHIP_RECON_ENCOUNTER: [GUNSHIP, SCOUT, SCOUT],
    FRIGATE_ENCOUNTER: [FRIGATE],
    DESTROYER_ENCOUNTER: [DESTROYER],
    CRUISER_ENCOUNTER: [CRUISER],
    CARRIER_ENCOUNTER: [CARRIER],
    FRIGATE_PAIR_ENCOUNTER: [FRIGATE, FRIGATE],
    FRIGATE_GUNSHIP_ENCOUNTER: [FRIGATE, GUNSHIP, GUNSHIP],
    DESTROYER_FIGHTER_ENCOUNTER: [DESTROYER, FIGHTER, FIGHTER, FIGHTER, FIGHTER, FIGHTER, FIGHTER],
    DESTROYER_FRIGATE_ENCOUNTER: [DESTROYER, FRIGATE],
    CRUISER_PAIR_ENCOUNTER: [CRUISER, CRUISER],
    CRUISER_FIGHTER_ENCOUNTER: [CRUISER, FIGHTER, FIGHTER, FIGHTER, FIGHTER, FIGHTER, FIGHTER],
    CARRIER_SCREEN_ENCOUNTER: [CARRIER, SCOUT, SCOUT, SCOUT, GUNSHIP, GUNSHIP, GUNSHIP],
    CARRIER_DESTROYER_ENCOUNTER: [CARRIER, DESTROYER, GUNSHIP],
    CARRIER_TASK_FORCE_ENCOUNTER: [CARRIER, CRUISER, DESTROYER, DESTROYER, FRIGATE, FRIGATE, FRIGATE],
    PLACEHOLDER_ENCOUNTER: ['placeholder']
}

L0_ENCOUNTER_TABLE = {SCOUT_ENCOUNTER: 50,
                      SCOUT_PAIR_ENCOUNTER: 100,
                      SCOUT_TRIO_ENCOUNTER: 100,
                      FIGHTER_ENCOUNTER: 50}
L1_ENCOUNTER_TABLE = {FIGHTER_ENCOUNTER: 50,
                      FIGHTER_RECON_ENCOUNTER: 100,
                      FIGHTER_PAIR_ENCOUNTER: 100,
                      GUNSHIP_ENCOUNTER: 50}
L2_ENCOUNTER_TABLE = {GUNSHIP_ENCOUNTER: 50,
                      FIGHTER_FLIGHT_ENCOUNTER: 100,
                      GUNSHIP_RECON_ENCOUNTER: 100,
                      FRIGATE_ENCOUNTER: 50}
L3_ENCOUNTER_TABLE = {FRIGATE_ENCOUNTER: 50,
                      FRIGATE_PAIR_ENCOUNTER: 100,
                      FRIGATE_GUNSHIP_ENCOUNTER: 100,
                      DESTROYER_ENCOUNTER: 50}
L4_ENCOUNTER_TABLE = {DESTROYER_ENCOUNTER: 50,
                      DESTROYER_FIGHTER_ENCOUNTER: 100,
                      DESTROYER_FRIGATE_ENCOUNTER: 100,
                      CRUISER_ENCOUNTER: 50}
L5_ENCOUNTER_TABLE = {CRUISER_ENCOUNTER: 50,
                      CRUISER_PAIR_ENCOUNTER: 100,
                      CRUISER_FIGHTER_ENCOUNTER: 100,
                      CARRIER_ENCOUNTER: 50}
L6_ENCOUNTER_TABLE = {CARRIER_ENCOUNTER: 50,
                      CARRIER_SCREEN_ENCOUNTER: 100,
                      CARRIER_DESTROYER_ENCOUNTER: 100,
                      CARRIER_TASK_FORCE_ENCOUNTER: 50}

ENCOUNTERS_TO_ENCOUNTER_TABLES = {L0_ENCOUNTER: L0_ENCOUNTER_TABLE,
                                  L1_ENCOUNTER: L1_ENCOUNTER_TABLE,
                                  L2_ENCOUNTER: L2_ENCOUNTER_TABLE,
                                  L3_ENCOUNTER: L3_ENCOUNTER_TABLE,
                                  L4_ENCOUNTER: L4_ENCOUNTER_TABLE,
                                  L5_ENCOUNTER: L5_ENCOUNTER_TABLE,
                                  L6_ENCOUNTER: L6_ENCOUNTER_TABLE}

# This table is kind of silly in that there's a much better way to represent it! If you have time (you won't)
# Scouts
L0_ENCOUNTER_CHANCES = [[20, 1], [10, 2], [05, 3], [00, 4], [00, 5], [00, 6], [00, 7], [00, 8], [00, 9]]
# Fighters
L1_ENCOUNTER_CHANCES = [[10, 1], [20, 2], [10, 3], [05, 4], [00, 5], [00, 6], [00, 7], [00, 8], [00, 9]]
# Gunships
L2_ENCOUNTER_CHANCES = [[05, 1], [10, 2], [20, 3], [10, 4], [05, 5], [00, 6], [00, 7], [00, 8], [00, 9]]
# Frigates
L3_ENCOUNTER_CHANCES = [[00, 1], [05, 2], [10, 3], [20, 4], [10, 5], [05, 6], [00, 7], [00, 8], [00, 9]]
# Destroyers
L4_ENCOUNTER_CHANCES = [[00, 1], [00, 2], [05, 3], [10, 4], [20, 5], [10, 6], [05, 7], [00, 8], [00, 9]]
# Cruisers
L5_ENCOUNTER_CHANCES = [[00, 1], [00, 2], [00, 3], [05, 4], [10, 5], [20, 6], [10, 7], [05, 8], [00, 9]]
# DEATH
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
