import libtcodpy as libtcod


class ProjectileAI(object):
    def __init__(self, path, game_map, objects, message_fn):  # TODO: Kinda iffy
        self.path = path
        self.game_map = game_map
        self.objects = objects
        self.message_fn = message_fn

    def take_turn(self):
        monster = self.owner

        (next_x, next_y) = self.path.step()
        blocked = monster.move_towards(next_x, next_y, self.game_map, self.objects)

        if blocked:
            for obj in self.objects:  # TODO: Ugh this is still gnarly
                if obj.x == next_x and obj.y == next_y and obj.fighter and obj != monster and not obj.is_projectile:
                    damage = monster.fighter.attack(obj)
                    if damage > 0 and (obj.ai or obj.is_player) and obj.fighter.hp > 0:
                        self.message_fn('The ' + monster.name + ' hit the ' + obj.name + ' for ' + str(damage) +
                                        ' damage!', libtcod.orange)
                    break
            monster.fighter.death_function(monster)
