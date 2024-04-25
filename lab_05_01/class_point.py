EPS = 1e-6  # для сравнения вещественных точек-координат


# класс точка
class Point:
    def __init__(self, *args) -> object:
        if args:
            self._x = args[0]
            self._y = args[1]
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
    def x(self) -> float: return self._x

    @x.setter
    def x(self, value): self._x = value

    @x.deleter
    def x(self): self._x = 0

    @y.getter
    def y(self) -> float: return self._y

    @y.setter
    def y(self, value): self._y = value

    @y.deleter
    def y(self): self._y = 0
