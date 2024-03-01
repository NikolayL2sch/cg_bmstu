from math import sqrt, acos, pi

from class_point import *

EPS = 1e-6


def side_len(p_1, p_2):
    return sqrt((p_2.x - p_1.x) * (p_2.x - p_1.x) + (p_2.y - p_1.y) * (p_2.y - p_1.y))


def is_triangle(side_1, side_2, side_3):
    if abs(side_1 + side_2 - side_3) < EPS or abs(side_2 + side_3 - side_1) < EPS or abs(
            side_1 + side_3 - side_2) < EPS:
        return False
    return True


def find_corner(p_1, p_2, p_3):
    p_p = find_intersection_altitude(p_1, p_2, p_3)
    p_m = find_intersection_median(p_2, p_3)

    am = side_len(p_1, p_p)
    an = side_len(p_1, p_m)
    mn = side_len(p_p, p_m)

    return p_p, p_m, count_corner(am, an, mn)


def count_corner(side_1, side_2, side_3):
    return acos((side_1 * side_1 + side_2 * side_2 - side_3 * side_3) / (2 * side_1 * side_2)) * (180 / pi)


def find_intersection_altitude(p_1, p_2, p_3):
    k_1 = (p_3.y - p_2.y) / (p_3.x - p_2.x)

    k_2 = -1 / k_1
    print(f'k_1, k_2: {k_1, k_2}')
    b_diff = p_3.y - p_1.y + k_2 * p_1.x - k_1 * p_3.x
    print('b_diff: ', b_diff)
    base_x = k_1 * b_diff / (1 + (k_1 ** 2))
    print(f'base_x: ', base_x)
    base_y = k_1 * (base_x - p_3.x) + p_3.y
    print(f'base_y: ', base_y)
    return Point(base_x, base_y)


def find_intersection_median(p_1, p_2):
    return Point((p_1.x + p_2.x) / 2, (p_1.y + p_2.y) / 2)
