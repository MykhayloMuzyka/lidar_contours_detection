import numpy as np


class P:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"({self.x},{self.y})"


class var:
    def __init__(self, alias):
        self.alias = alias

    def __repr__(self):
        return self.alias

    def __str__(self):
        return self.__repr__()


def is_var(v):
    return isinstance(v, var)


class L:
    def __init__(self, y, k, x, b):
        self.y = y
        self.k = k
        self.x = x
        self.b = b

    def __repr__(self):
        return f"{self.y} = {self.k} * {self.x} + {self.b}"

    def is_horizontal(self):
        return is_var(self.y) and not is_var(self.x)

    def is_vertical(self):
        return is_var(self.x) and not is_var(self.y)

    def get_y(self, x):
        if self.is_horizontal():
            raise self.x
        elif self.is_vertical():
            raise ValueError()
        return self.k * x + self.b

    def get_x(self, y):
        if self.is_horizontal():
            raise ValueError()
        elif self.is_vertical():
            return self.y
        return (1 / self.k) * (y - self.b)

    @classmethod
    def from_p(cls, p1, p2):
        if p2.x == p1.x:
            return cls(p1.x, 1, var('x'), 0)
        elif p2.y == p1.y:
            return cls(var('y'), 1, p1.y, 0)
        k = (p2.y - p1.y) / (p2.x - p1.x)
        b = p1.y - k * p1.x
        return cls(var('y'), k, var('x'), b)

    def intersects(self, line):
        if (
                (self.is_horizontal() and line.is_horizontal())
                or (self.is_vertical() and line.is_vertical())
                or (self.k == line.k)
        ):
            return False

        if self.is_horizontal():
            y_int = self.x
            if line.is_vertical():
                x_int = line.y
            else:
                x_int = (line.b - y_int) / line.k
        elif self.is_vertical():
            x_int = self.y
            if line.is_horizontal():
                y_int = line.x
            else:
                y_int = line.k * x_int + line.b
        else:
            if line.is_vertical():
                x_int = line.y
                y_int = self.k * x_int + self.b
            elif line.is_horizontal():
                y_int = line.x
                x_int = (self.b - y_int) / self.k
            else:
                x_int = (line.b - self.b) / (self.k - line.k)
                y_int = self.k * x_int + self.b

        return P(abs(x_int), abs(y_int))


def distance(p1, p2):
    return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)


if __name__ == '__main__':
    p1, p2 = P(3, 5), P(0, 4)
    p3, p4 = P(0, 1), P(5, 7)

    l1 = L.from_p(p1, p2)
    l2 = L.from_p(p3, p4)

    print(l1)
    print(l2)

    print(l1.intersects(l2))
    print(l2.intersects(l1))
