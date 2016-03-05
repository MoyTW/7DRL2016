import libtcodpy as libtcod

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

# Set font
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

# Set window
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'tutorial roguelike! whooo!', False)

# I don't want this to be real-time, so this line effectively does nothing!
libtcod.sys_set_fps(LIMIT_FPS)

# lol global
playerx = SCREEN_WIDTH/2
playery = SCREEN_HEIGHT/2


# uuuugh scoping
def handle_keys():
    global playerx, playery

    key = libtcod.console_wait_for_keypress(True)
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return True

    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        playery -= 1
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        playery += 1
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        playerx -= 1
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        playerx += 1

# Main loop (what is exit fn?)
while not libtcod.console_is_window_closed():
    # TODO: Is it necessary to set to run on each frame?
    libtcod.console_set_default_foreground(0, libtcod.white)
    libtcod.console_put_char(0, playerx, playery, '@', libtcod.BKGND_NONE)
    libtcod.console_flush()
    libtcod.console_put_char(0, playerx, playery, ' ', libtcod.BKGND_NONE)

    exit_status = handle_keys()
    if exit_status:
        break

