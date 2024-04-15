from math import floor, fabs
from typing import List, Union, Tuple

from class_point import Point


def sign(n: Union[int, float]) -> int:
    if n == 0:
        return 0
    if n < 0:
        return -1
    return 1


def brezenhem_int(p1: Point, p2: Point, testing=False) -> Union[List[Point], int]:
    points = []
    steps = 0

    if abs(p1.x - p2.x) <= 1e-13 and abs(p1.y - p2.y) <= 1e-13:
        points.append(Point(p1.x, p1.y))
        return points

    dx = p2.x - p1.x
    dy = p2.y - p1.y
    sx = sign(dx)
    sy = sign(dy)

    dx = abs(dx)
    dy = abs(dy)

    if dy > dx:
        dx, dy = dy, dx
        swap = True
    else:
        swap = False

    f = 2 * dy - dx
    x = p1.x
    y = p1.y

    x_ = x
    y_ = y

    for i in range(1, int(dx + 1)):
        if not testing:
            points.append(Point(x, y))

        if f >= 0:
            if swap:
                x += sx
            else:
                y += sy
            f -= 2 * dx
        if f <= 0:
            if swap:
                y += sy
            else:
                x += sx
            f += 2 * dy

        if testing:
            if abs(x_ - x) > 1e-13 and abs(y_ - y) > 1e-13:
                steps += 1
            x_ = x
            y_ = y

    return points if not testing else steps


def brezenhem_float(p1: Point, p2: Point, testing=False) -> Union[List[Point], int]:
    points = []
    steps = 0

    if abs(p1.x - p2.x) <= 1e-13 and abs(p1.y - p2.y) <= 1e-13:
        points.append(Point(p1.x, p1.y))
        return points

    dx = p2.x - p1.x
    dy = p2.y - p1.y
    sx = sign(dx)
    sy = sign(dy)
    dx = abs(dx)
    dy = abs(dy)

    if dx <= 1e-13:
        m = 10e9
    else:
        m = dy / dx

    if m > 1:
        dx, dy = dy, dx
        m = 1 / m
        fl = True
    else:
        fl = False

    f = m - 0.5

    x = p1.x
    y = p1.y

    x_ = x
    y_ = y

    for i in range(int(dx + 1)):
        if not testing:
            points.append(Point(x, y))
        if f >= 0:
            if fl:
                x = x + sx
            else:
                y = y + sy
            f -= 1
        if f <= 0:
            if fl:
                y = y + sy
            else:
                x = x + sx
            f += m
        if testing:
            if abs(x_ - x) > 1e-13 and abs(y_ - y) > 1e-13:
                steps += 1
            x_ = x
            y_ = y
    return points if not testing else steps


def brezenhem_st(p1: Point, p2: Point, testing=False) -> Union[List[Tuple[Point, float]], int]:
    points = []
    steps = 0

    if abs(p1.x - p2.x) <= 1e-13 and abs(p1.y - p2.y) <= 1e-13:
        points.append((Point(p1.x, p1.y), 255))
        return points

    dx = p2.x - p1.x
    dy = p2.y - p1.y
    sx = sign(dx)
    sy = sign(dy)
    dx = abs(dx)
    dy = abs(dy)

    if dy > dx:
        dx, dy = dy, dx
        fl = True
    else:
        fl = False

    intensity = 1
    f = intensity / 2

    if abs(dx) < 1e-13:
        m = 10e9
    else:
        m = dy / dx

    x = p1.x
    y = p1.y

    x_ = x
    y_ = y

    for i in range(1, int(dx + 1)):
        if not testing:
            points.append((Point(x, y), 255 * f))

        if f < 1 - m:
            if fl:
                y += sy
            else:
                x += sx
            f += m
        else:
            x += sx
            y += sy
            f -= (1 - m)

        if testing:
            if abs(x_ - x) > 1e-13 and abs(y_ - y) > 1e-13:
                steps += 1
            x_ = x
            y_ = y

    return points if not testing else steps


def cda(p1: Point, p2: Point, testing=False) -> Union[List[Point], int]:
    points = []

    if abs(p1.x - p2.x) <= 1e-13 and abs(p1.y - p2.y) <= 1e-13:
        points.append(Point(p1.x, p1.y))
        return points

    dx = p2.x - p1.x
    dy = p2.y - p1.y

    if abs(dx) > abs(dy):
        L = abs(dx)
    else:
        L = abs(dy)

    dx /= L
    dy /= L

    x = p1.x
    y = p1.y

    x_ = x
    y_ = y

    steps = 0

    for _ in range(int(L)):
        if testing:
            x_ = x
            y_ = y
        x += dx
        y += dy
        if not testing:
            points.append(Point(round(x), round(y)))
        elif round(x_) != round(x) and round(y_) != round(y):
            steps += 1

    return points if not testing else steps


def vu(p1: Point, p2: Point, testing=False) -> Union[List[Tuple[Point, float]], int]:
    points = []

    count_steps = 0

    if abs(p1.x - p2.x) <= 1e-13 and abs(p1.y - p2.y) <= 1e-13:
        points.append((Point(p1.x, p1.y), 255))
        return points

    dx = p2.x - p1.x
    dy = p2.y - p1.y
    intensity = 1
    step = 1

    if abs(dy) >= abs(dx):
        if dy != 0:
            intensity = dx / dy

        tmp_intensity = intensity

        if p1.y > p2.y:
            tmp_intensity *= -1
            step *= -1

        end = round(p2.y) - 1 if dx > dy else round(p2.y) + 1

        for y in range(round(p1.y), end, step):
            d1 = p1.x - floor(p1.x)
            d2 = 1 - d1

            if not testing:
                points.append((Point(int(p1.x) + 1, y), round(fabs(d1) * 255)))
                points.append((Point(int(p1.x), y), round(fabs(d2) * 255)))
            elif y < round(p2.y) and int(p1.x) != int(p1.x + intensity):
                count_steps += 1

            p1.x += tmp_intensity
    else:
        if dx != 0:
            intensity = dy / dx

        tmp_intensity = intensity

        if p1.x > p2.x:
            tmp_intensity *= -1
            step *= -1

        end = round(p2.x) - 1 if dx < dy else round(p2.x) + 1

        for x in range(round(p1.x), end, step):
            d1 = p1.y - floor(p1.y)
            d2 = 1 - d1

            if not testing:
                points.append((Point(x, int(p1.y) + 1), round(fabs(d1) * 255)))
                points.append((Point(x, int(p1.y)), round(fabs(d2) * 100)))
            elif x < round(p2.x) and int(p1.y) != int(p1.y + intensity):
                count_steps += 1

            p1.y += tmp_intensity
    return points if not testing else count_steps
