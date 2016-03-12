import math
import copy


class Path(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def current_position(self):
        return self.x, self.y

    def step(self):
        raise NotImplementedError('Override this!')

    def project(self, turns):
        mirror_path = copy.deepcopy(self)  # TODO: Kinda nasty, but DEADLINES!
        visited = []
        for _ in range(turns):
            mirror_path.step()
            visited.append((mirror_path.x, mirror_path.y))
        return visited


class LinePath(Path):
    """ Defines a line from (x0, y0) to (x1, y1). Will continue past (x1, y1). """
    def __init__(self, x0, y0, x1, y1):
        super(LinePath, self).__init__(x0, y0)
        self.x1 = x1
        self.y1 = y1

        # Special case: vertical line
        if x1 - x0 == 0:
            self.vertical = True
        else:
            self.vertical = False
            self.d_error = math.fabs(float(y1 - y0) / float(x1 - x0))

        self.error = 0.0

        if y1 - y0 > 0:
            y_err = 1
        else:
            y_err = -1
        self.y_err = y_err

        if x1 - x0 > 0:
            x_diff = 1
        else:
            x_diff = -1
        self.x_diff = x_diff

    def step(self):
        if self.vertical:
            self.y += self.y_err
            return self.x, self.y
        elif self.error >= 0.5:
            self.y += self.y_err
            self.error -= 1.0
            return self.x, self.y
        else:
            self.x += self.x_diff
            self.error += self.d_error
            return self.x, self.y


class ReversePath(Path):
    def __init__(self, x0, y0, x1, y1):
        super(ReversePath, self).__init__(x0, y0)
        self.straight_segment = LinePath(x0, y0, x1, y1)
        self.x1 = x1
        self.y1 = y1
        self.reverse_segment = LinePath(x1, y1, x0, y0)
        self.has_reversed = False

    def step(self):
        if not self.has_reversed:
            (self.x, self.y) = self.straight_segment.step()
            if self.x == self.x1 and self.y == self.y1:
                self.has_reversed = True
            return self.x, self.y
        else:
            (self.x, self.y) = self.reverse_segment.step()
            return self.x, self.y
