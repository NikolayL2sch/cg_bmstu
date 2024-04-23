from math import sqrt, pi, cos, sin
from typing import List

from class_point import Point
from lab_04.point_funcs import add_symmetr_points


def ellipse_brezenhem(p: Point, width: float, height: float) -> List[Point]:
    x = 0
    y = height
    points = []

    d = height * height - width * width * (2 * height - 1)
    y_k = 0
    while y >= y_k:
        points.extend(add_symmetr_points(p, Point(x + p.x, y + p.y)))
        if d <= 0:
            d1 = 2 * d + width * width * (2 * y + 2)
            if d1 < 0:
                x += 1
                d = d + height * height * (2 * x + 1)
            else:
                x += 1
                y -= 1
                d += height * height * (2 * x + 1) + width * width * (1 - 2 * y)
        else:
            d2 = 2 * d + height * height * (2 - 2 * x)
            y -= 1
            if d2 < 0:
                x += 1
                d = d + height * height * (2 * x + 1) + width * width * (1 - 2 * y)
            else:
                d += width * width * (1 - 2 * y)
    return points


def ellipse_canonical(p: Point, width: float, height: float) -> List[Point]:
    points = []
    x = 0
    y = 0

    edge_x = round(width / sqrt(1 + height * height / (width * width)))

    while x <= edge_x:
        y = round(sqrt(width * width * height * height - x * x * height * height) / width)
        points.extend(add_symmetr_points(p, Point(x + p.x, y + p.y)))
        x += 1

    while y >= 0:
        x = round(sqrt(width * width * height * height - y * y * width * width) / height)
        points.extend(add_symmetr_points(p, Point(x + p.x, y + p.y)))
        y -= 1
    return points


def ellipse_param(p: Point, width: float, height: float) -> List[Point]:
    points = []
    step = 1 / max(width, height)
    angle = 0

    while angle <= pi / 2:
        x = round(width * cos(angle))
        y = round(height * sin(angle))
        angle += step
        points.extend(add_symmetr_points(p, Point(x + p.x, y + p.y)))
    return points


def ellipse_middle_point(p: Point, width: float, height: float) -> List[Point]:
    points = []
    x = 0
    y = height
    P1 = height * height - width * width * (height - 1 / 4)
    while 2 * height * height * x < 2 * width * width * y:
        points.extend(add_symmetr_points(p, Point(x + p.x, y + p.y)))
        if P1 < 0:
            x += 1
            P1 = P1 + 2 * height * height * x + height * height
        else:
            x += 1
            y -= 1
            P1 = P1 + 2 * height * height * x - 2 * width * width * y + height * height

    P2 = width * width - height * height * (width - 1 / 4)
    x = width
    y = 0
    while y <= height / sqrt(1 + width * width / (height * height)):
        points += add_symmetr_points(p, Point(x + p.x, y + p.y))
        if P2 < 0:
            y += 1
            P2 = P2 + 2 * width * width * y + width * width
        else:
            x -= 1
            y += 1
            P2 += width * width * (2 * y + 1) - 2 * height * height * x
    return points
