import time

from PyQt5.QtCore import QEventLoop
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow

from class_point import Point


def paint_alg(edge_color: QColor, fill_color: QColor, seed_point: Point, win: QMainWindow, delay=False):
    stack = [seed_point]
    while stack:
        # Извлечь затравочный пиксель из стека
        seed_pixel = stack.pop()

        win.image.setPixel(int(seed_pixel.x), int(
            seed_pixel.y), fill_color.rgb())

        x = seed_pixel.x + 1
        y = seed_pixel.y

        pixel_color = win.image.pixelColor(int(x), int(y)).rgb()
        while pixel_color != fill_color.rgb() and pixel_color != edge_color.rgb():
            win.image.setPixel(int(x), int(y), fill_color.rgb())
            x += 1
            pixel_color = win.image.pixelColor(int(x), int(y)).rgb()

        xr = x - 1
        x = seed_pixel.x - 1
        pixel_color = win.image.pixelColor(int(x), int(y)).rgb()

        while pixel_color != fill_color.rgb() and pixel_color != edge_color.rgb() and x > 0:
            win.image.setPixel(int(x), int(y), fill_color.rgb())
            x -= 1
            pixel_color = win.image.pixelColor(int(x), int(y)).rgb()

        xl = x + 1
        sign = [1, -1]
        for i in sign:
            x = xl
            y = seed_pixel.y + i
            while x <= xr:
                flag = False
                pixel_color = win.image.pixelColor(int(x), int(y)).rgb()
                while pixel_color != fill_color.rgb() and pixel_color != edge_color.rgb() and x <= xr:
                    flag = True
                    x += 1
                    pixel_color = win.image.pixelColor(int(x), int(y)).rgb()

                if flag:
                    if x == xr and pixel_color != fill_color.rgb() and pixel_color != edge_color.rgb():
                        stack.append(Point(x, y))
                    else:
                        stack.append(Point(x - 1, y))
                x_in = x
                pixel_color = win.image.pixelColor(int(x), int(y)).rgb()
                while x < xr and (pixel_color == fill_color.rgb() or pixel_color == edge_color.rgb()):
                    x += 1
                    pixel_color = win.image.pixelColor(int(x), int(y)).rgb()
                if x == x_in:
                    x += 1
        if delay:
            win.scene.clear()
            win.scene.addPixmap(QPixmap.fromImage(win.image))
            QApplication.processEvents(QEventLoop.AllEvents, 1)
            time.sleep(0.01)
    win.scene.clear()
    win.scene.addPixmap(QPixmap.fromImage(win.image))
