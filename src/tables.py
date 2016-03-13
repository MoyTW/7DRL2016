import utils
from constants import *  # TODO: practices not so great maybe?

L0_ENCOUNTER = 0
L1_ENCOUNTER = 1
L2_ENCOUNTER = 2
L3_ENCOUNTER = 3
L4_ENCOUNTER = 4
L5_ENCOUNTER = 5
L6_ENCOUNTER = 6
L7_ENCOUNTER = 7

EMPTY_ENCOUNTER = 'none'
SCOUT_ENCOUNTER = 'single scout'
SCOUT_PAIR_ENCOUNTER = 'scout pair'
SCOUT_TRIO_ENCOUNTER = 'scout element'
FIGHTER_ENCOUNTER = 'single fighter'
FIGHTER_RECON_ENCOUNTER = 'recon flight'
FIGHTER_PAIR_ENCOUNTER = 'fighter element'
FIGHTER_FLIGHT_ENCOUNTER = 'fighter flight'
GUNSHIP_ENCOUNTER = 'single gunship'
GUNSHIP_RECON_ENCOUNTER = 'gunship and escorts'
GUNSHIP_PAIR_ENCOUNTER = 'gunship element'
FRIGATE_ENCOUNTER = 'single frigate'
DESTROYER_ENCOUNTER = 'single destroyer'
CRUISER_ENCOUNTER = 'single cruiser'
CARRIER_ENCOUNTER = 'single carrier'
FRIGATE_PAIR_ENCOUNTER = 'pair of frigates'
FRIGATE_GUNSHIP_ENCOUNTER = 'frigate and gunship'
DESTROYER_FIGHTER_ENCOUNTER = 'destroyer and escorts'
DESTROYER_FRIGATE_ENCOUNTER = 'destroyer and frigate'
CRUISER_PAIR_ENCOUNTER = 'cruiser pair'
CRUISER_FIGHTER_ENCOUNTER = 'cruiser and escorts'
CARRIER_SCREEN_ENCOUNTER = 'carrier and screening force'
CARRIER_DESTROYER_ENCOUNTER = 'carrier and destroyer'
CARRIER_TASK_FORCE_ENCOUNTER = 'carrier task force'
FAST_RESPONSE_FLEET_ENCOUNTER = 'fast response fleet'
HEAVY_STRIKE_FORCE_ENCOUNTER = 'heavy strike force'
EVER_VICTORIOUS_FLEET_ENCOUNTER = 'Ever Victorious Fleet'

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
    FAST_RESPONSE_FLEET_ENCOUNTER: [DESTROYER, DESTROYER, DESTROYER, DESTROYER, DESTROYER, DESTROYER, FRIGATE, FRIGATE, GUNSHIP,
                                    GUNSHIP, GUNSHIP, GUNSHIP, GUNSHIP, GUNSHIP, GUNSHIP, GUNSHIP, GUNSHIP, GUNSHIP,
                                    GUNSHIP, GUNSHIP],
    HEAVY_STRIKE_FORCE_ENCOUNTER: [CRUISER, CRUISER, CRUISER, CRUISER, CARRIER, CARRIER, DESTROYER, DESTROYER],
    EVER_VICTORIOUS_FLEET_ENCOUNTER: [CRUISER, CRUISER, CRUISER, CRUISER, CARRIER, CARRIER, DESTROYER, DESTROYER,
                                      CARRIER, CRUISER, FRIGATE, FRIGATE, FRIGATE, FRIGATE, FRIGATE],

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
L7_ENCOUNTER_TABLE = {CARRIER_TASK_FORCE_ENCOUNTER: 50,
                      FAST_RESPONSE_FLEET_ENCOUNTER: 100,
                      HEAVY_STRIKE_FORCE_ENCOUNTER: 100,
                      EVER_VICTORIOUS_FLEET_ENCOUNTER: 50}

ENCOUNTERS_TO_ENCOUNTER_TABLES = {L0_ENCOUNTER: L0_ENCOUNTER_TABLE,
                                  L1_ENCOUNTER: L1_ENCOUNTER_TABLE,
                                  L2_ENCOUNTER: L2_ENCOUNTER_TABLE,
                                  L3_ENCOUNTER: L3_ENCOUNTER_TABLE,
                                  L4_ENCOUNTER: L4_ENCOUNTER_TABLE,
                                  L5_ENCOUNTER: L5_ENCOUNTER_TABLE,
                                  L6_ENCOUNTER: L6_ENCOUNTER_TABLE,
                                  L7_ENCOUNTER: L7_ENCOUNTER_TABLE}

# This table is kind of silly in that there's a much better way to represent it! If you have time (you won't)
# Scouts
L0_ENCOUNTER_CHANCES = [[20, 1], [10, 2], [00, 3], [00, 4], [00, 5], [00, 6], [00, 7], [00, 8], [00, 9]]
# Fighters
L1_ENCOUNTER_CHANCES = [[10, 1], [20, 2], [10, 3], [00, 4], [00, 5], [00, 6], [00, 7], [00, 8], [00, 9]]
# Gunships
L2_ENCOUNTER_CHANCES = [[00, 1], [10, 2], [20, 3], [10, 4], [00, 5], [00, 6], [00, 7], [00, 8], [00, 9]]
# Frigates
L3_ENCOUNTER_CHANCES = [[00, 1], [00, 2], [10, 3], [20, 4], [10, 5], [00, 6], [00, 7], [00, 8], [00, 9]]
# Destroyers
L4_ENCOUNTER_CHANCES = [[00, 1], [00, 2], [00, 3], [10, 4], [20, 5], [10, 6], [00, 7], [00, 8], [00, 9]]
# Cruisers
L5_ENCOUNTER_CHANCES = [[00, 1], [00, 2], [00, 3], [00, 4], [10, 5], [20, 6], [10, 7], [00, 8], [00, 9]]
# Carriers
L6_ENCOUNTER_CHANCES = [[00, 1], [00, 2], [00, 3], [00, 4], [00, 5], [10, 6], [20, 7], [10, 8], [00, 9]]
# DEATH
L7_ENCOUNTER_CHANCES = [[00, 1], [00, 2], [00, 3], [00, 4], [00, 5], [00, 6], [00, 7], [00, 8], [01, 9]]


def choose_encounter_for_level(level):
    table = {L0_ENCOUNTER: utils.from_dungeon_level(level, L0_ENCOUNTER_CHANCES),
             L1_ENCOUNTER: utils.from_dungeon_level(level, L1_ENCOUNTER_CHANCES),
             L2_ENCOUNTER: utils.from_dungeon_level(level, L2_ENCOUNTER_CHANCES),
             L3_ENCOUNTER: utils.from_dungeon_level(level, L3_ENCOUNTER_CHANCES),
             L4_ENCOUNTER: utils.from_dungeon_level(level, L4_ENCOUNTER_CHANCES),
             L5_ENCOUNTER: utils.from_dungeon_level(level, L5_ENCOUNTER_CHANCES),
             L6_ENCOUNTER: utils.from_dungeon_level(level, L6_ENCOUNTER_CHANCES),
             L7_ENCOUNTER: utils.from_dungeon_level(level, L7_ENCOUNTER_CHANCES)}
    encounter_level = utils.random_choice(table)
    encounter_table = ENCOUNTERS_TO_ENCOUNTER_TABLES[encounter_level]
    return utils.random_choice(encounter_table)
