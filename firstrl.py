import libtcodpy as libtcod

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

# ================================================== MAP SECTION =================================================
MAP_WIDTH = 80
MAP_HEIGHT = 45

# Why are these not defined as constants? Are they going to be put into a color lookup dict later on?
color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 100)


class Tile(object):
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        # That's...basically shadowing. Reassignment! Hiss! Boo!
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight


def make_game_map():
    # OH GOD! WHAT IS SCOPE EVEN
    global game_map

    game_map = [[Tile(False)
                 for _ in range(MAP_HEIGHT)]
                for _ in range(MAP_WIDTH)]

    game_map[30][22].blocked = True
    game_map[30][22].block_sight = True
    game_map[50][22].blocked = True
    game_map[50][22].block_sight = True


# Object is using 'con' as the buffer, which is unbound! Does that...work?
class Object(object):
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx, dy):
        # SCOPING DEAR OH GOD WHY FIX THIS AFTER THE TUTORIAL
        if not game_map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy

    # TODO: Have draw take the buffer to draw to as a parameter!
    def draw(self):
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    # TODO: Have clear take the buffer to draw to as a parameter!
    def clear(self):
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)


# Set font
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

# Initialize windows/buffers
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'tutorial roguelike! whooo!', False)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

# I don't want this to be real-time, so this line effectively does nothing!
libtcod.sys_set_fps(LIMIT_FPS)

# Initialize Object objects
# TODO: Rename Object lol
player = Object(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, '@', libtcod.white)
npc = Object(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 'N', libtcod.blue)
objects = [npc, player]


# uuuugh scoping
def handle_keys():
    key = libtcod.console_wait_for_keypress(True)
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return True

    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        player.move(0, -1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        player.move(0, 1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        player.move(-1, 0)
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        player.move(1, 0)


def render_all():
    for o in objects:
        o.draw()

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = game_map[x][y].block_sight
            if wall:
                libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
            else:
                libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)

    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


def clear_objects():
    for o in objects:
        o.clear()

# =================================================== MAIN LOOP ==================================================

# Init before main loop
make_game_map()

# Main loop (what is exit fn?)
while not libtcod.console_is_window_closed():
    libtcod.console_set_default_foreground(0, libtcod.white)

    render_all()
    libtcod.console_flush()
    clear_objects()

    exit_status = handle_keys()
    if exit_status:
        break
