from math import sqrt, pi, cos, sin
from typing import List

from class_point import Point
from point_funcs import add_symmetr_points


def circle_brezenhem(p: Point, radius: float, time_testing=False) -> List[Point]:
    points = []
    x = 0
    y = radius
    d = 2 * (1 - radius)
    while x <= y:
        if not time_testing:
            points.extend(add_symmetr_points(p, Point(x + p.x, y + p.y), True))
        d1 = 2 * d + 2 * y - 1
        if d1 < 0:
            x += 1
            d = d + 2 * x + 1
        else:
            x += 1
            y -= 1
            d = d + 2 * (x - y + 1)
    if not time_testing:
        return points


def circle_canonical(p: Point, radius: float, time_testing=False) -> List[Point]:
    points = []
    x = 0
    arc_end = round(radius / sqrt(2))  # идем до половины дуги
    while x <= arc_end:
        y = sqrt(radius * radius - x ** 2)
        if not time_testing:
            points.extend(add_symmetr_points(
                p, Point(x + p.x, y + p.y), is_circle=True))
        x += 1
    if not time_testing:
        return points


def circle_param(p: Point, radius: float, time_testing=False) -> List[Point]:
    t = 1 / radius
    points = []
    angle = 0

    while angle <= pi / 4:
        x = round(radius * cos(angle))
        y = round(radius * sin(angle))
        angle += t
        if not time_testing:
            points.extend(add_symmetr_points(
                p, Point(x + p.x, y + p.y), is_circle=True))

    if not time_testing:
        return points


def circle_middle_point(p: Point, radius: float, time_testing=False) -> List[Point]:
    x = 0
    y = radius
    points = []

    k = 5 / 4 - radius  # параметр принятия решений
    if not time_testing:
        points = add_symmetr_points(p, Point(x + p.x, y + p.y), is_circle=True)

    while x < y:
        x += 1
        if k < 0:
            k = k + 2 * x + 1
        else:
            y -= 1
            k = k + 2 * x + 1 - 2 * y
        if not time_testing:
            points.extend(add_symmetr_points(
                p, Point(x + p.x, y + p.y), is_circle=True))
    if not time_testing:
        return points
