from math import pi, cos, sin
from typing import Union, List, Tuple

from PyQt5 import Qt

from class_point import Point


def fill_point_lists(a: float, b: float, c: float, R: float, max_win_size: List[float]) -> List[Point]:
    circle_points = []
    hyperbole_points = []

    # A + cos(degrees) * R = x
    # B + sin(degrees) * R = y
    degrees = 0
    while degrees <= 2 * pi:
        circle_points.append(Point(a + cos(degrees) * R, b + sin(degrees) * R))
        degrees += 1 / R  # scale?

    # y = C / x - гипербола
    x = max_win_size[0] // 2
    print(x)
    while x > 0:
        if x != 0:
            hyperbole_points.append(Point(x, c / x))
            x -= 1  # scale?

    intersection_points = find_strokes(a, b, c, R, hyperbole_points, circle_points)
    # for point in intersection_points:
    #    print(point.x, point.y)
    return circle_points, hyperbole_points, intersection_points


def find_strokes(a: float, b: float, c: float, R: float, hyperbole_points: List[Point], circle_points: List[Point]) -> List[Point]:
    strokes = []

    for point in hyperbole_points + circle_points:
        if (point.x - a) ** 2 + (point.y - b) ** 2 <= R * R:
            if point.y >= c and (point.x > 0 and point.y > 0 and c > 0) or (point.x < 0 < point.y and c < 0):
                strokes.append(point)
    return strokes
