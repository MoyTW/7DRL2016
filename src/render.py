import libtcodpy as libtcod
from constants import *  # TODO: Bad programmer!
import utils

color_dark_wall = libtcod.Color(120, 120, 160)
color_light_wall = libtcod.Color(200, 200, 220)
color_dark_ground = libtcod.Color(0, 0, 50)
color_light_ground = libtcod.Color(25, 25, 50)
color_danger = libtcod.orange


def get_names_under_mouse(fov_map, camera_x, camera_y, mouse, objects):
    (x, y) = (camera_x + mouse.cx, camera_y + mouse.cy)

    names = [obj.name for obj in objects
             if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]
    names_str = ', '.join(names)
    return names_str.capitalize()


def move_camera(target_x, target_y, camera_x, camera_y):
    # new camera coordinates (top-left corner of the screen relative to the map)
    x = target_x - CAMERA_WIDTH / 2
    y = target_y - CAMERA_HEIGHT / 2

    # make sure the camera doesn't see outside the map
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    if x > MAP_WIDTH - CAMERA_WIDTH - 1:
        x = MAP_WIDTH - CAMERA_WIDTH - 1
    if y > MAP_HEIGHT - CAMERA_HEIGHT - 1:
        y = MAP_HEIGHT - CAMERA_HEIGHT - 1

    recompute = (x != camera_x or y != camera_y)

    return x, y, recompute


def to_camera_coordinates(x, y, camera_x, camera_y):
    # convert coordinates on the map to coordinates on the screen
    (x, y) = (x - camera_x, y - camera_y)

    if x < 0 or y < 0 or x >= CAMERA_WIDTH or y >= CAMERA_HEIGHT:
        return None, None  # if it's outside the view, return nothing
    else:
        return x, y


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    # render background
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    # render bar
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    # text
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                             name + ': ' + str(value) + '/' + str(maximum))


def color_square(color, con, fov_map, game_map, x, y, camera_x, camera_y, flag=libtcod.BKGND_SET):
    # Don't try to color squares off the map
    if x >= MAP_WIDTH or y >= MAP_HEIGHT:
        return False

    visible = libtcod.map_is_in_fov(fov_map, x, y)
    wall = game_map[x][y].block_sight
    if visible and not wall:
        libtcod.console_set_char_background(con, x - camera_x, y - camera_y, color, flag)
        return True
    return False


def draw_paths(con, fov_map, game_map, camera_x, camera_y, projectiles, timeframe):
    for projectile in projectiles:
        path = projectile.ai.path
        continue_draw = True

        moves_in_timeframe = int(timeframe / projectile.fighter.speed)

        for (x, y) in path.project(moves_in_timeframe):
            if continue_draw:
                continue_draw = color_square(color_danger, con, fov_map, game_map, x, y, camera_x, camera_y)
                if game_map[x][y].blocked:
                    continue_draw = False


def draw_rangefinder(con, fov_map, game_map, player, camera_x, camera_y):
    tiles = utils.calculate_circle(player.x, player.y, 3)
    for tile in tiles:
        color_square(libtcod.lightest_blue, con, fov_map, game_map, tile[0], tile[1], camera_x, camera_y,
                     libtcod.BKGND_ALPHA(.1))


def highlight_movers(con, fov_map, game_map, camera_x, camera_y, objects, timeframe):
    for obj in objects:
        if obj.ai and not hasattr(obj.ai, 'path') and obj.fighter:
            if obj.fighter.time_until_turn < timeframe:
                color_square(libtcod.lightest_green, con, fov_map, game_map, obj.x, obj.y, camera_x, camera_y)


def render_all(fov_recompute, player, objects, projectiles, fov_map, game_map, con, panel, game_msgs, dungeon_level,
               mouse, camera_x, camera_y, timeframe, non_interactive_objects):  # TODO: Silly

    (camera_x, camera_y, recompute) = move_camera(player.x, player.y, camera_x, camera_y)
    fov_recompute = fov_recompute or recompute

    for non_interactive_object in non_interactive_objects:
        non_interactive_object.draw(con, fov_map, game_map, camera_x, camera_y)
    for projectile in projectiles:
        projectile.draw(con, fov_map, game_map, camera_x, camera_y)
    for o in objects:
        if o != player:
            o.draw(con, fov_map, game_map, camera_x, camera_y)
    player.draw(con, fov_map, game_map, camera_x, camera_y)

    if fov_recompute:
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
        libtcod.console_clear(con)

    for y in range(CAMERA_HEIGHT):
        for x in range(CAMERA_WIDTH):
            (map_x, map_y) = (camera_x + x, camera_y + y)
            visible = libtcod.map_is_in_fov(fov_map, map_x, map_y)
            wall = game_map[map_x][map_y].block_sight
            if not visible:
                if game_map[map_x][map_y].explored:
                    if wall:
                        libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
            else:
                if wall:
                    libtcod.console_set_char_background(con, x, y, color_light_wall, libtcod.BKGND_SET)
                else:
                    libtcod.console_set_char_background(con, x, y, color_light_ground, libtcod.BKGND_SET)
                game_map[map_x][map_y].explored = True

    draw_rangefinder(con, fov_map, game_map, player, camera_x, camera_y)
    draw_paths(con, fov_map, game_map, camera_x, camera_y, projectiles, timeframe)
    highlight_movers(con, fov_map, game_map, camera_x, camera_y, objects, timeframe)

    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    # ----- rendering GUI -----
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    # print messages
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    # print bars
    render_bar(panel, 1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp, libtcod.light_red,
               libtcod.darker_red)
    libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Sector: ' + str(dungeon_level))
    libtcod.console_print_ex(panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT,
                             'Position: (' + str(player.x) + ',' + str(player.y) + ')')

    # print mouselook
    libtcod.console_set_default_foreground(panel, libtcod.light_grey)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
                             get_names_under_mouse(fov_map=fov_map, camera_x=camera_x, camera_y=camera_y, mouse=mouse,
                                                   objects=objects))

    # blit GUI
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

    return camera_x, camera_y, fov_recompute


class Renderer(object):
    def __init__(self, fov_map, fov_recompute=True, camera_x=0, camera_y=0):
        self.fov_map = fov_map
        self.fov_recompute = fov_recompute
        self.camera_x = camera_x
        self.camera_y = camera_y

    def force_recompute(self):
        self.fov_recompute = True

    def render_all(self, player, objects, projectiles, game_map, con, panel, game_msgs, dungeon_level, mouse,
                   non_interactive_objects):
        (camera_x, camera_y, fov_recompute) = render_all(fov_recompute=self.fov_recompute, player=player,
                                                         objects=objects, fov_map=self.fov_map, game_map=game_map,
                                                         con=con, panel=panel, game_msgs=game_msgs,
                                                         dungeon_level=dungeon_level, mouse=mouse,
                                                         camera_x=self.camera_x, camera_y=self.camera_y,
                                                         timeframe=player.fighter.speed, projectiles=projectiles,
                                                         non_interactive_objects=non_interactive_objects)
        self.camera_x = camera_x
        self.camera_y = camera_y
        self.fov_recompute = fov_recompute

    def clear_objects(self, con, objects):
        for obj in objects:
            obj.clear(con, self.camera_x, self.camera_y)