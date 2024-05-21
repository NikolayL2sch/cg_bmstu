import sys
from time import time

from typing import List, Tuple

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QColorDialog, QButtonGroup, QGraphicsSceneMouseEvent
from PyQt5.QtGui import QColor, QImage, QColorConstants, QPixmap

from dialogs import show_author, show_task, show_instruction, show_err_win, show_war_win
from class_point import Point
from input_checks import params_to_int
from paint_funcs import paint_alg
from point_funcs import del_lines_by_point
from brezenhem_algs import brezenhem_circle, brezenhem_ellipse, brezenhem_line

point_list: List[Point] = []
figures: List[List[Point]] = []
edges: List[List[List[Point]]] = []
limit_figures: List[List[Point]] = []

prev_figure_points: int = 0
current_figure_points: int = 0

last_pos: QPoint = None
current_edge_color: QColor = QColor(255, 0, 0)
current_paint_color: QColor = QColor(0, 0, 255)

seed_point: Point = None

is_pressed: bool = False


def delete_point_from_figures(del_point_id: int) -> None:
    k = del_point_id + 1
    for _ in range(len(figures)):
        if k - len(figures[_]) > 0:
            k -= len(figures[_])
        else:
            figures[_].pop(k - 1)


def delete_point_from_edges(del_point_id):
    if len(edges) > 1 and edges[del_point_id - 1]:
        for line in edges[del_point_id - 1]:
            if line in edges[del_point_id]:
                edges[del_point_id - 1].remove(line)
    if len(edges) > 1:
        if del_point_id + 1 < len(point_list):
            for line in edges[del_point_id + 1]:
                if line in edges[del_point_id]:
                    edges[del_point_id + 1].remove(line)
        elif figures and figures[0]:
            for line in edges[0]:
                if line in edges[del_point_id]:
                    edges[0].remove(line)


def set_paint_color(color: QColor) -> None:
    global current_paint_color
    current_paint_color = color


def change_paint_color():
    colour = QColorDialog.getColor(initial=current_paint_color)
    if colour.isValid():
        set_paint_color(QColor(colour))


def set_edge_color(color: QColor) -> None:
    global current_edge_color
    current_edge_color = color


def change_edge_color() -> None:
    colour = QColorDialog.getColor(initial=current_edge_color)
    if colour.isValid():
        set_edge_color(QColor(colour))


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("./template.ui", self)  # временно в корне

        self.scene = MyScene(self, 0, 0, 630.0, 900.0)
        self.graphicsView.setScene(self.scene)
        self.image = QImage(630, 900, QImage.Format_RGB32)
        self.image.fill(QColorConstants.White)

        # menu bar
        self.about_author.triggered.connect(show_author)
        self.about_task.triggered.connect(show_task)
        self.instruction.triggered.connect(show_instruction)

        self.clear_button.clicked.connect(self.clear_scene)

        # push buttons
        self.add_point_button.clicked.connect(self.add_point)
        self.remove_point_button.clicked.connect(self.remove_point)
        self.add_zt_button.clicked.connect(self.add_zt)
        self.add_figure_button.clicked.connect(self.add_figure)
        self.change_edge_button.clicked.connect(change_edge_color)
        self.change_color_button.clicked.connect(change_paint_color)
        self.close_figure_button.clicked.connect(self.close_figure)
        self.paint_figure_button.clicked.connect(self.paint_figures)

        self.figure_type_group = QButtonGroup()
        self.figure_type_group.addButton(self.set_circle_figure)
        self.figure_type_group.addButton(self.set_ellipse_figure)

        self.set_circle_figure.setChecked(True)
        self.set_circle_figure.toggled.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.page))
        self.set_ellipse_figure.toggled.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.page_2))
        self.stackedWidget.setCurrentWidget(self.page)

        self.graphicsView.setMouseTracking(True)
        self.redraw()
        self.show()

    def clear_scene(self):
        global prev_figure_points, current_figure_points
        self.image.fill(QColorConstants.White)
        self.redraw()
        point_list.clear()
        figures.clear()
        edges.clear()
        self.scroll_list.clear()
        prev_figure_points = 0
        current_figure_points = 0

    def add_point(self, point: Point = None) -> None:
        if not point:
            point = self.get_point_coords()
        if point is not None:
            self.draw_point(point)

    def get_point_coords(self) -> Point:
        x_txt = self.set_x.text()
        y_txt = self.set_y.text()
        params = params_to_int(x_txt, y_txt)
        if len(params) == 0:
            return
        x, y = params
        return Point(x, y)

    def add_point_by_click(self, event: QGraphicsSceneMouseEvent) -> None:
        scene_pos = event.scenePos()
        p_x, p_y = scene_pos.x(), scene_pos.y()
        self.draw_point(Point(int(p_x), int(p_y)))

    def redraw(self):
        self.scene.clear()
        self.scene.addPixmap(QPixmap.fromImage(self.image))

    def draw_point(self, point: Point) -> None:
        global current_figure_points
        for _ in point_list:
            if point == _:
                show_war_win("Введенная точка уже существует.")
                break
        else:
            point_list.append(point)
            self.scroll_list.addItem(
                f'{len(point_list)}.({point.x}; {point.y})')
            self.image.setPixel(point.x, point.y, current_edge_color.rgb())
            edges.append([])
            if len(point_list) > 1:
                self.draw_line(point_list[-2], point_list[-1])
            current_figure_points += 1
            self.redraw()

    def draw_line(self, p1: Point, p2: Point) -> None:
        line = brezenhem_line(p1, p2)
        for point in line:
            self.image.setPixel(point.x, point.y, current_edge_color.rgb())
        edges[-1].append(line)
        edges[-2].append(line)
        self.redraw()

    def remove_point(self):
        point = self.get_point_coords()
        if point is None:
            return

        for i in range(len(point_list)):
            if point_list[i] == point:
                del_lines_by_point(edges, i)
                if edges[i]:
                    for line in edges[i]:
                        for pixel in line:
                            self.image.setPixel(int(pixel.x), int(
                                pixel.y), QColor(Qt.white).rgb())
                edges.pop(i)
                if i == len(point_list) - 1 and len(point_list) > 2:
                    self.draw_line(point_list[i - 1], point_list[0])
                elif len(point_list) > 2:
                    self.draw_line(point_list[i - 1], point_list[i + 1])
                point_list.pop(i)
                self.update_scroll_list()
                self.redraw()
                break
        else:
            show_err_win("Введенной точки не существует.")
            return

        for i in range(len(figures)):
            for _ in range(len(figures[i])):
                if figures[i][_] == point:
                    figures[i].pop(_)
                    break

    def update_scroll_list(self) -> None:
        self.scroll_list.clear()
        for i in range(len(point_list)):
            self.scroll_list.addItem(
                f'{i + 1}.({round(point_list[i].x, 2)}; {round(point_list[i].y, 2)})')

    def close_figure(self):
        global prev_figure_points
        if len(point_list) < 2:
            show_err_win("Введено недостаточно точек для этого действия")
        else:
            self.draw_line(point_list[0], point_list[-1])
            figures.append(
                point_list[prev_figure_points:current_figure_points:])
            prev_figure_points = current_figure_points

    def del_point_by_click(self, event: QGraphicsSceneMouseEvent):
        scene_pos = event.scenePos()
        min_diff = 100
        del_point_id = -1
        for i in range(len(point_list)):
            if abs(scene_pos.x() - point_list[i].x) + abs(scene_pos.y() - point_list[i].y) < min_diff:
                min_diff = abs(
                    scene_pos.x() - point_list[i].x) + abs(scene_pos.y() - point_list[i].y)
                del_point_id = i
        if min_diff > 10:
            show_err_win(
                "Кажется, вы пытаетесь удалить несуществующую точку.\nПопробуйте кликнуть ближе к точке.")
            return
        delete_point_from_figures(del_point_id)
        delete_point_from_edges(del_point_id)
        if edges[del_point_id]:
            for line in edges[del_point_id]:
                for pixel in line:
                    self.image.setPixel(int(pixel.x), int(
                        pixel.y), QColor(Qt.white).rgb())
        edges.pop(del_point_id)
        if del_point_id == len(point_list) - 1 and len(point_list) > 2:
            self.draw_line(point_list[del_point_id - 1], point_list[0])
        elif len(point_list) > 2:
            self.draw_line(point_list[del_point_id - 1],
                           point_list[del_point_id + 1])
        point_list.pop(del_point_id)
        self.update_scroll_list()

    def paint_figures(self, func_testing=False):
        delay = False
        if self.set_delay_cb.isChecked():
            delay = True
        if len(figures) == 0:
            show_err_win("Ошибка. Фигура не замкнута")
            return
        if seed_point is None:
            show_err_win("Ошибка. Не задана затравочная точка.")
            return
        start = time()
        paint_alg(current_edge_color, current_paint_color,
                  seed_point, self, delay=delay)
        end = time()
        if not delay:
            if func_testing:
                with open('report-functesting-latest.txt', 'a+') as f:
                    f.write(f"Время выполнения алгоритма в тесте {test_i}: {(end - start) * 1000:.2f} мс.\n")
            else:
                show_war_win(f"Время выполнения алгоритма: {(end - start) * 1000:.2f} мс.")

    def add_zt(self, point: Point = None) -> None:
        global seed_point
        if not point:
            new_point = self.get_point_coords()
        else:
            new_point = point
        if new_point is not None:
            if seed_point is not None:
                for i in range(3):
                    self.image.setPixel(
                        int(seed_point.x + i), int(seed_point.y - i), QColor(Qt.white).rgb())
                    self.image.setPixel(
                        int(seed_point.x - i), int(seed_point.y + i), QColor(Qt.white).rgb())
                    self.image.setPixel(
                        int(seed_point.x + i), int(seed_point.y + i), QColor(Qt.white).rgb())
                    self.image.setPixel(
                        int(seed_point.x - i), int(seed_point.y - i), QColor(Qt.white).rgb())
            seed_point = new_point
            for i in range(3):
                self.image.setPixel(
                    int(seed_point.x + i), int(seed_point.y - i), QColor(Qt.magenta).rgb())
                self.image.setPixel(
                    int(seed_point.x - i), int(seed_point.y + i), QColor(Qt.magenta).rgb())
                self.image.setPixel(
                    int(seed_point.x + i), int(seed_point.y + i), QColor(Qt.magenta).rgb())
                self.image.setPixel(
                    int(seed_point.x - i), int(seed_point.y - i), QColor(Qt.magenta).rgb())
            self.current_seed_label.setText(
                f"x,y затравки: {seed_point.x}, {seed_point.y}")
            self.redraw()

    def add_figure(self, args):
        if self.set_circle_figure.isChecked():
            self.draw_circle(args)
        else:
            self.draw_ellipse(args)

    def draw_ellipse(self, coords=None) -> None:
        if not coords:
            coords = self.get_ellipse_params()
            if coords is None:
                return
        center, width, height = coords
        points = brezenhem_ellipse(center, width, height)
        limit_figures.append(points)
        for point in points:
            self.image.setPixel(int(point.x), int(
                point.y), current_edge_color.rgb())
        self.redraw()

    def get_ellipse_params(self) -> Tuple[Point, int, int]:
        xc_str = self.set_xc_ellipse.text()
        yc_str = self.set_yc_ellipse.text()
        width_str = self.set_ellipse_width.text()
        height_str = self.set_ellipse_height.text()
        params = params_to_int(xc_str, yc_str, width_str, height_str)
        if len(params) == 0:
            return
        xc, yc, width, height = params
        if width <= 0 or height <= 0:
            show_err_win("Значение высоты и ширины должно быть больше нуля!")
            return
        return Point(xc, yc), width, height

    def get_circle_params(self) -> Tuple[Point, int]:
        xc_str = self.set_xc_circle.text()
        yc_str = self.set_yc_circle.text()
        radius_str = self.set_r_circle.text()
        params = params_to_int(xc_str, yc_str, radius_str)
        if len(params) == 0:
            return
        xc, yc, radius = params
        if radius <= 0:
            show_err_win("Значение радиуса должно быть больше нуля!")
            return
        return Point(xc, yc), radius

    def draw_circle(self, coords=None):
        if not coords:
            coords = self.get_circle_params()
            if coords is None:
                return
        center, radius = coords
        points = brezenhem_circle(center, radius)
        limit_figures.append(points)
        for point in points:
            self.image.setPixel(int(point.x), int(point.y),
                                QColor(current_edge_color).rgb())
        self.redraw()

    def add_zt_point_by_click(self, event: QGraphicsSceneMouseEvent) -> None:
        global seed_point
        scene_pos = event.scenePos()
        p_x, p_y = scene_pos.x(), scene_pos.y()
        if seed_point is not None:
            for i in range(3):
                self.image.setPixel(
                    int(seed_point.x + i), int(seed_point.y - i), QColor(Qt.white).rgb())
                self.image.setPixel(
                    int(seed_point.x - i), int(seed_point.y + i), QColor(Qt.white).rgb())
                self.image.setPixel(
                    int(seed_point.x + i), int(seed_point.y + i), QColor(Qt.white).rgb())
                self.image.setPixel(
                    int(seed_point.x - i), int(seed_point.y - i), QColor(Qt.white).rgb())
        seed_point = Point(p_x, p_y)
        self.current_seed_label.setText(
            f"x,y затравки: {seed_point.x}, {seed_point.y}")
        for i in range(3):
            self.image.setPixel(int(seed_point.x + i),
                                int(seed_point.y - i), QColor(Qt.magenta).rgb())
            self.image.setPixel(int(seed_point.x - i),
                                int(seed_point.y + i), QColor(Qt.magenta).rgb())
            self.image.setPixel(int(seed_point.x + i),
                                int(seed_point.y + i), QColor(Qt.magenta).rgb())
            self.image.setPixel(int(seed_point.x - i),
                                int(seed_point.y - i), QColor(Qt.magenta).rgb())
        self.redraw()


class MyScene(QtWidgets.QGraphicsScene):
    def __init__(self, win: Ui, *args):
        super().__init__(*args)
        self.window = win

        self.last_x = None
        self.last_y = None

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        scene_pos = event.scenePos()
        window.current_coords_label.setText(
            f'x :{scene_pos.x():.2f}, y :{scene_pos.y():.2f}')

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        global last_pos, is_pressed
        if event.button() == Qt.LeftButton:
            is_pressed = True
            last_pos = event.pos()
            window.add_point_by_click(event)
        elif event.button() == Qt.RightButton:
            window.del_point_by_click(event)
        elif event.button() == Qt.MiddleButton:
            window.add_zt_point_by_click(event)


if __name__ == '__main__':
    global test_i
    start_testing = time()
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()

    FUNC_TESTING = False
    if len(sys.argv) > 2:
        FUNC_TESTING = True
        test_i = int(sys.argv[1])
        seed_x = int(sys.argv[2])
        seed_y = int(sys.argv[3])
        seed_point = Point(seed_x, seed_y)
        num_points = int(sys.argv[4])
        for _ in range(num_points):
            window.add_point(
                Point(int(sys.argv[2 * _ + 5]), int(sys.argv[2 * _ + 6])))
        if sys.argv[2 * num_points + 5] == 'true':
            window.set_delay_cb.setChecked(True)
        window.close_figure()
        if len(sys.argv) > 2 * num_points + 6:
            limit_figure_type = sys.argv[2 * num_points + 6]
            if limit_figure_type == 'circle':
                window.set_circle_figure.setChecked(True)
                data = [Point(int(sys.argv[2 * num_points + 7]), int(sys.argv[2 * num_points + 8])),
                        int(sys.argv[2 * num_points + 9])]
            else:
                window.set_ellipse_figure.setChecked(True)
                data = [Point(int(sys.argv[2 * num_points + 7]), int(sys.argv[2 * num_points + 8])),
                        int(sys.argv[2 * num_points + 9]), int(sys.argv[2 * num_points + 10])]

            window.add_figure(data)

        window.paint_figures(func_testing=True)

    if FUNC_TESTING:
        screenshot = window.grab()
        screenshot.save(f'./results/test_{test_i}.png', 'png')
    else:
        sys.exit(app.exec_())
