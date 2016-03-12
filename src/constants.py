# Name constants
GAME_STATE_DIDNT_TAKE_TURN = 'gs-didnt-take-turn'
GAME_STATE_PLAYER_DEAD = 'gs-dead'
GAME_STATE_PLAYING = 'gs-playing'

ACTION_CANCELLED = 'cancelled'

SLOT_RIGHT_HAND = 'right hand'
SLOT_LEFT_HAND = 'left hand'

# Value constants
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 60

CAMERA_WIDTH = 80
CAMERA_HEIGHT = 43

FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 20

BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

INVENTORY_WIDTH = 50

HEAL_AMOUNT = 4
LIGHTNING_RANGE = 5
LIGHTNING_DAMAGE = 20
CONFUSE_NUM_TURNS = 10
CONFUSE_RANGE = 8
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 12

LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150
LEVEL_SCREEN_WIDTH = 40

CHARACTER_SCREEN_WIDTH = 30

MAP_WIDTH = 150
MAP_HEIGHT = 150

ROOM_MAX_SIZE = 40
ROOM_MIN_SIZE = 20
MAX_ZONE_GEN_ATTEMPTS = 100
MAX_ZONES = 9

TIME_IN_TURN = 100

SATELLITES_PER_LEVEL = [[30, 1], [25, 3], [20, 5]]

SCOUTS_PER_LEVEL = [[10, 1]]
GUNSHIPS_PER_LEVEL = [[10, 1], [30, 2]]
POINT_DEFENSE_DESTROYERS_PER_LEVEL = [[10, 2], [30, 3]]

SCOUT = 'scout'
GUNSHIP = 'gunship'
POINT_DEFENSE_DESTROYER = 'point defense destroyer'