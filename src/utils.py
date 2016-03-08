import math


class LinePath(object):
    """ Defines a line from (x0, y0) to (x1, y1). Progresses along a line from 0 to 1 using the step function. """
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.d_error = math.fabs(float(y1 - y0) / float(x1 - x0))

        self.x = x0
        self.y = y0

        self.error = 0.0

        if y1 - y0 > 0:
            y_err = 1
        else:
            y_err = -1
        self.y_err = y_err

    def current_position(self):
        return self.x, self.y

    def step(self):
        if self.error >= 0.5:
            self.y += self.y_err
            self.error -= 1.0
            return self.x, self.y
        else:
            self.x += 1
            self.error += self.d_error
            return self.x, self.y
