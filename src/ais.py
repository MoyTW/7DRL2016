class ProjectileAI(object):
    def __init__(self, path, game_map, objects):
        self.path = path
        self.game_map = game_map
        self.objects = objects

    def take_turn(self):
        monster = self.owner

        (next_x, next_y) = self.path.step()
        blocked = monster.move_towards(next_x, next_y, self.game_map, self.objects)

        if blocked:
            for obj in self.objects:  # TODO: Ugh this is still gnarly
                if obj.x == next_x and obj.y == next_y and obj.fighter and obj != monster and not obj.is_projectile:
                    monster.fighter.attack(obj)
                    break
            monster.fighter.death_function(monster)