from math import sqrt


def draw_ellipse(scene, center: Point, width, height, color):
    focus = sqrt(width * width + height * height)
    # фокусное расстояние первого эллипса - большая полуось второго
    # рисуем первый эллипс

    x = 0
    y = height
    points = []

    d = height * height - width * width * (2 * height - 1)
    y_k = 0
    while x < width:
        points.extend(add_symmetr_points(x, y))  # добавляем симметричные 8 точек
        if d <= 0:
            d1 = 2 * d + width * width * (2 * y + 2)
            if d1 < 0:
                x += 1
                d = d + height * height * (2 * x + 1)
            else:
                x += 1
                y -= 1
                d += height * height * (2 * x + 1) + width * width * (1 - 2 * y)

