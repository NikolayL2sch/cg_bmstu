EPS = 1e-6  # для сравнения вещественных точек-координат


# класс точка
class Point:
    def __init__(self, *kargs):
        if kargs:
            self._x = kargs[0]
            self._y = kargs[1]
        else:
            self._x = 0
            self._y = 0

    def __eq__(self, other):
        if self.__class__.__name__ == other.__class__.__name__:
            return abs(self._x - other.x) < EPS and abs(self._y - other.y) < EPS
        return False

    x = property(float)
    y = property(float)

    @x.getter
    def x(self): return self._x

    @x.setter
    def x(self, value): self._x = value

    # нужен ли делитер?

    @x.deleter
    def x(self): self._x = 0

    @y.getter
    def y(self): return self._y

    @y.setter
    def y(self, value): self._y = value

    @y.deleter
    def y(self): self._y = 0
