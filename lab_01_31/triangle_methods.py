from math import sqrt, acos, pi

from class_point import Point, EPS


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

    # print(f'Perpend x: {p_p.x}, y: {p_p.y}\nMedian x: {p_m.x}, y: {p_m.y}')
    am = side_len(p_1, p_p)
    an = side_len(p_1, p_m)
    mn = side_len(p_p, p_m)
    # print(am, an, mn)

    return p_p, p_m, count_corner(am, an, mn)


def count_corner(side_1, side_2, side_3):
    return acos((side_1 * side_1 + side_2 * side_2 - side_3 * side_3) / (2 * side_1 * side_2)) * (180 / pi)


def find_intersection_altitude(p_1, p_2, p_3):
    if abs(p_3.x - p_2.x) < EPS:
        k_1 = 0
    else:
        k_1 = (p_3.y - p_2.y) / (p_3.x - p_2.x)

    if k_1 == 0:
        k_2 = 0
        b_diff = p_3.y - p_1.y + k_2 * p_1.x - k_1 * p_3.x
        base_x = b_diff
        base_y = 0
    else:
        k_2 = -1 / k_1
        b_diff = p_3.y - p_1.y + k_2 * p_1.x - k_1 * p_3.x
        base_x = - k_1 * b_diff / (1 + (k_1 ** 2))
        base_y = k_1 * (base_x - p_3.x) + p_3.y

    # print(f'k_1, k_2: {k_1, k_2}')
    # print('b_diff: ', b_diff)
    # print(f'base_x: ', base_x)
    # print(f'base_y: ', base_y)
    return Point(base_x, base_y)


def find_intersection_median(p_1, p_2):
    return Point((p_1.x + p_2.x) / 2, (p_1.y + p_2.y) / 2)
