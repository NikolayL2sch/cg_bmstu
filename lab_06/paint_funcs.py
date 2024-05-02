from typing import List

from class_point import Point
from point_funcs import add_symmetr_points


def paint_alg():
    pass


def brezenhem_circle(p: Point, radius: float) -> List[Point]:
    points = []
    x = 0
    y = radius
    d = 2 * (1 - radius)
    while x <= y:
        points.extend(add_symmetr_points(p, Point(x + p.x, y + p.y), True))
        d1 = 2 * d + 2 * y - 1
        if d1 < 0:
            x += 1
            d = d + 2 * x + 1
        else:
            x += 1
            y -= 1
            d = d + 2 * (x - y + 1)
    return points


def brezenhem_ellipse(p: Point, width: float, height: float) -> List[Point]:
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
                d += height * height * (2 * x + 1) + \
                    width * width * (1 - 2 * y)
        else:
            d2 = 2 * d + height * height * (2 - 2 * x)
            y -= 1
            if d2 < 0:
                x += 1
                d = d + height * height * \
                    (2 * x + 1) + width * width * (1 - 2 * y)
            else:
                d += width * width * (1 - 2 * y)
    return points
