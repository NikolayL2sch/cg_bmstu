from class_point import Point


def get_code(point: Point, rect):
    code = [0, 0, 0, 0]
    if point.x < rect[0]:
        code[0] = 1
    elif point.x > rect[2]:
        code[1] = 1
    if point.y < rect[3]:
        code[2] = 1
    elif point.y > rect[1]:
        code[3] = 1

    return int(''.join(map(str, code)), 2)
