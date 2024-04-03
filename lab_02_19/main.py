import sys
from math import cos, sin, pi, sqrt, cosh, sinh
from typing import List, Tuple

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QPen, QWheelEvent, QMouseEvent
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem

from dialogs import show_author, show_task, show_instruction
from input_checks import params_to_float, check_radius, check_scale_koeff
from class_point import Point
from matrix_methods import get_new_coords

intersection_points: List[Point] = []
grid_lines: List[QGraphicsLineItem] = []

scale: float = 1.0
step: int = int(scale) * 10
max_win_size: List[int] = [0, 0, 0]

a: float = 0.0
b: float = 0.0
c: float = 1000.0
R: float = 100

angle: float = 0

# для гиперболы базовые точки - центр, ее вершина и фокус во второй четверти.
hyperbole_points: List[Point] = [Point(0, 0), Point(sqrt(c), sqrt(c)), Point(sqrt(2 * c), sqrt(2 * c))]

# первая точка - центр эллипса, вторая - лежит на большой полуоси, третья - отстает от нее на угол pi/2
ellipse_points: List[Point] = [Point(a, b), Point(a + R, b), Point(a, b + R)]

init_points: List[List[Point]] = [hyperbole_points.copy(), ellipse_points.copy(), intersection_points.copy()]
is_pressed: bool = False
last_pos: bool = None


def ellipse_coords(n: int) -> Tuple[float, float]:
    current_x = ellipse_points[0].x + (ellipse_points[1].x - ellipse_points[0].x) * cos(n * 2 * pi / (100 * scale)) + (
            ellipse_points[2].x - ellipse_points[0].x) * sin(n * 2 * pi / (100 * scale))
    current_y = ellipse_points[0].y + (ellipse_points[1].y - ellipse_points[0].y) * cos(n * 2 * pi / (100 * scale)) + (
            ellipse_points[2].y - ellipse_points[0].y) * sin(n * 2 * pi / (100 * scale))
    return current_x, -current_y


def hyperbole_coords(n: int) -> Tuple[float, float]:
    a_h = sqrt(
        (hyperbole_points[1].x - hyperbole_points[0].x) ** 2 + (hyperbole_points[1].y - hyperbole_points[0].y) ** 2)
    c_h = sqrt(
        (hyperbole_points[2].x - hyperbole_points[0].x) ** 2 + (hyperbole_points[2].y - hyperbole_points[0].y) ** 2)
    b_h = sqrt(c_h * c_h - a_h * a_h)

    current_x = a_h * cosh(n / (100 * scale)) + hyperbole_points[0].x
    current_y = b_h * sinh(n / (100 * scale)) + hyperbole_points[0].y

    rotated_x = (hyperbole_points[0].x + (cos(pi / 4 + angle)) * (current_x - hyperbole_points[0].x) -
                 sin(pi / 4 + angle) * (current_y - hyperbole_points[0].y))
    rotated_y = (hyperbole_points[0].y + (sin(pi / 4 + angle)) * (current_x - hyperbole_points[0].x) +
                 cos(pi / 4 + angle) * (current_y - hyperbole_points[0].y))
    return rotated_x, -rotated_y


def is_inner_point(x: float, y: float) -> bool:
    is_between = (x - a) ** 2 + (y - b) ** 2 <= R * R and y >= c / x
    is_correct = (x > 0 and y > 0 and c > 0) or (x < 0 < y and c < 0)
    return is_between and is_correct


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        global init_points
        super(Ui, self).__init__()
        uic.loadUi("./lab_02_19/template.ui", self)

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.need_grid()
        self.draw_figure()
        self.draw_intersection()
        init_points[2] = intersection_points

        self.redBrush = QBrush(Qt.red)
        self.pen = QPen(Qt.red)

        # menu bar
        self.about_author.triggered.connect(show_author)
        self.about_task.triggered.connect(show_task)
        self.instruction.triggered.connect(show_instruction)

        # button actions
        self.move_action_button.clicked.connect(self.move_figure)
        self.scale_action_button.clicked.connect(self.scale_figure)
        self.rotate_action_button.clicked.connect(self.rotate_figure)
        self.draw_figure_action_button.clicked.connect(self.redraw_figure)
        self.reset_action_button.clicked.connect(self.reset_figure)

        self.graphicsView.setMouseTracking(True)

        self.graphicsView.mousePressEvent = self.mousePressEvent
        self.graphicsView.wheelEvent = self.wheel_event
        self.graphicsView.mouseReleaseEvent = self.mouseReleaseEvent
        self.graphicsView.mouseMoveEvent = self.mouseMoveEvent

        self.show()

    def wheel_event(self, event: QWheelEvent) -> None:
        global scale
        factor = 1.2

        if event.angleDelta().y() > 0:
            self.graphicsView.scale(factor, factor)
        else:
            self.graphicsView.scale(1.0 / factor, 1.0 / factor)

        scale = self.graphicsView.transform().m11()  # Получаем текущий масштаб по оси X (и Y)
        if self.need_grid():
            for grid_line in grid_lines:
                self.scene.removeItem(grid_line)
            self.add_grid()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        global is_pressed
        if event.button() == Qt.LeftButton:
            is_pressed = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        global last_pos
        if is_pressed:
            dx = event.pos().x() - last_pos.x()
            dy = event.pos().y() - last_pos.y()
            self.graphicsView.horizontalScrollBar().setValue(self.graphicsView.horizontalScrollBar().value() - dx)
            self.graphicsView.verticalScrollBar().setValue(self.graphicsView.verticalScrollBar().value() - dy)
            last_pos = event.pos()
            if self.need_grid():
                for grid_line in grid_lines:
                    grid_line.deleteLater()
                self.add_grid()
        scene_pos = self.graphicsView.mapToScene(event.pos())
        self.current_coords_label.setText(f'x :{scene_pos.x():.2f}, y :{-scene_pos.y():.2f}')

    def mousePressEvent(self, event: QMouseEvent) -> None:
        global last_pos, is_pressed
        if event.button() == Qt.LeftButton:
            is_pressed = True
            last_pos = event.pos()

    def get_move_params(self) -> float:
        dx_str = self.set_dx.text()
        dy_str = self.set_dy.text()

        params = params_to_float(dx_str, dy_str)

        if len(params) == 0:
            return
        dx, dy = params

        return dx, dy

    def reset_figure(self):
        global hyperbole_points, ellipse_points, intersection_points
        hyperbole_points = init_points[0]
        ellipse_points = init_points[1]
        intersection_points = []

        self.draw_figure()
        self.draw_intersection()

    def move_figure(self) -> None:
        global hyperbole_points, ellipse_points, intersection_points

        params = self.get_move_params()
        if params is None:
            return
        dx, dy = params

        move_matrix = [[1, 0, dx], [0, 1, dy], [0, 0, 1]]
        hyperbole_points = get_new_coords(move_matrix, hyperbole_points)
        ellipse_points = get_new_coords(move_matrix, ellipse_points)

        self.draw_figure()

    def draw_figure(self) -> None:
        global intersection_points, grid_lines
        self.scene.clear()
        grid_lines = []
        self.need_grid()
        self.add_grid()
        self.draw_ellipse()
        self.draw_hyperbole()

    def draw_intersection(self) -> None:
        min_diff, max_diff = None, None
        max_point, min_point = Point(0, 0), Point(0, 0)

        for point in intersection_points:
            line_diff = point.y - point.x
            if not min_diff or line_diff < min_diff:
                min_point = point
                min_diff = line_diff
            if not max_diff or line_diff > max_diff:
                max_point = point
                max_diff = line_diff
        k = (max_point.y - min_point.y) / (max_point.x - min_point.x)

        half_diff = max_point.y - k * max_point.x
        z1, z2 = [], []
        for point in intersection_points:
            if point.y - k * point.x < half_diff:
                z1.append(point)
            else:
                z2.append(point)

        z1.sort(key=lambda _: _.y - _.x)
        z2.sort(key=lambda _: _.y - _.x)
        cur_diff = min_diff
        while cur_diff < max_diff:
            i = 0
            while i < len(z1) - 1 and z1[i].y - z1[i].x < cur_diff:
                i += 1
            first_point = z1[i]
            i = 0
            while i < len(z2) - 1 and z2[i].y - z2[i].x < cur_diff:
                i += 1
            second_point = z2[i]
            line = QGraphicsLineItem(first_point.x, first_point.y, second_point.x, second_point.y)
            line.setPen(QPen(Qt.magenta))
            line.setZValue(1)
            self.scene.addItem(line)
            cur_diff += 10 / scale

    def draw_hyperbole(self) -> None:
        global intersection_points
        first_id = -max_win_size[0] / 6
        prev_x, prev_y = hyperbole_coords(first_id)
        if is_inner_point(prev_x, -prev_y):
            intersection_points.append(Point(prev_x, prev_y))
        i_step = 5 * int(scale)
        for i in range(int(first_id) + 1, int(-first_id), i_step):
            x, y = hyperbole_coords(i)
            if is_inner_point(x, -y):
                intersection_points.append(Point(x, y))
            line = QGraphicsLineItem(prev_x, prev_y, x, y)
            line.setPen(QPen(Qt.green))
            line.setZValue(1)
            self.scene.addItem(line)
            prev_x, prev_y = x, y

    def draw_ellipse(self) -> None:
        global intersection_points
        prev_x, prev_y = ellipse_coords(0)
        if is_inner_point(prev_x, -prev_y):
            intersection_points.append(Point(prev_x, prev_y))
        for i in range(1, 101 * int(scale)):
            x, y = ellipse_coords(i)
            if is_inner_point(x, -y):
                intersection_points.append(Point(x, y))
            line = QGraphicsLineItem(prev_x, prev_y, x, y)
            line.setPen(QPen(Qt.red))
            line.setZValue(1)
            self.scene.addItem(line)
            prev_x, prev_y = x, y

    def need_grid(self) -> bool:
        global max_win_size
        flag: bool = False
        max_size = self.graphicsView.maximumSize()
        max_width = int(max_size.width() * (1 / scale))
        max_height = int(max_size.height() * (1 / scale))
        grid_interval = int(50 * (1 / scale))
        grid_interval = round(grid_interval / 50) * 50
        if grid_interval != max_win_size[2]:
            max_win_size[2] = grid_interval
            flag = True
        if max_win_size[0] < max_width and max_win_size[1] < max_height:
            max_win_size[0] = max_width
            max_win_size[1] = max_height
            flag = True
        return flag

    def add_grid(self):
        global grid_lines, max_win_size
        max_width = max_win_size[0]
        max_height = max_win_size[1]
        grid_interval = max_win_size[2]
        if grid_interval == 0:
            grid_interval = 20
        self.current_grid_label.setText(f'Текущий шаг сетки: {grid_interval}')
        start_grid_width = - ((max_width // 2) + grid_interval - (max_width // 2) % grid_interval)
        start_grid_height = - ((max_height // 2) + grid_interval - (max_height // 2) % grid_interval)
        end_grid_width = (max_width // 2) - (max_width // 2) % grid_interval
        end_grid_height = (max_height // 2) - (max_width // 2) % grid_interval
        pen = QPen(Qt.darkGray)
        pen_width = 1 if int(1 / scale) == 0 else int(1 / scale)
        pen.setWidth(pen_width)
        for x in range(start_grid_width, end_grid_width, grid_interval):
            line = QGraphicsLineItem(x, start_grid_height, x, end_grid_height)
            line.setPen(pen)
            line.setZValue(0)
            grid_lines.append(line)
            self.scene.addItem(line)
        for y in range(start_grid_height, end_grid_height, grid_interval):
            line = QGraphicsLineItem(start_grid_width, y, end_grid_width, y)
            line.setPen(pen)
            line.setZValue(0)
            grid_lines.append(line)
            self.scene.addItem(line)

        axis_x = QGraphicsLineItem(-300 * (1 / scale), 0, 300 * (1 / scale), 0)
        axis_y = QGraphicsLineItem(0, -300 * (1 / scale), 0, 300 * (1 / scale))
        pen.setColor(Qt.white)
        grid_lines.append(axis_x)
        grid_lines.append(axis_y)
        axis_x.setPen(pen)
        axis_y.setPen(pen)
        axis_x.setZValue(0)
        axis_y.setZValue(0)
        self.scene.addItem(axis_x)
        self.scene.addItem(axis_y)

    def get_scale_params(self) -> float:
        kx_str = self.set_kx.text()
        ky_str = self.set_ky.text()
        cx_str = self.set_cx.text()
        cy_str = self.set_cy.text()

        params = params_to_float(kx_str, ky_str, cx_str, cy_str)

        if len(params) == 0:
            return
        kx, ky, cx, cy = params
        if not check_scale_koeff(kx) or not check_scale_koeff(ky):
            return
        return kx, ky, cx, cy

    def scale_figure(self) -> None:
        global hyperbole_points, ellipse_points, intersection_points
        params = self.get_scale_params()
        if params is None:
            return
        kx, ky, cx, cy = params

        move_matrix = [[1, 0, -cx], [0, 1, -cy], [0, 0, 1]]
        scale_matrix = [[kx, 0, 0], [0, ky, 0], [0, 0, 1]]
        move_matrix_back = [[1, 0, cx], [0, 1, cy], [0, 0, 1]]

        hyperbole_points = get_new_coords(move_matrix, hyperbole_points)
        ellipse_points = get_new_coords(move_matrix, ellipse_points)

        hyperbole_points = get_new_coords(scale_matrix, hyperbole_points)
        ellipse_points = get_new_coords(scale_matrix, ellipse_points)

        hyperbole_points = get_new_coords(move_matrix_back, hyperbole_points)
        ellipse_points = get_new_coords(move_matrix_back, ellipse_points)

        self.draw_figure()

    def rotate_figure(self):
        global hyperbole_points, ellipse_points, intersection_points, angle

        params = self.get_rotate_params()
        if params is None:
            return

        rx, ry, angle_p = params
        angle_p *= pi / 180
        angle += angle_p
        rotate_matrix = [[cos(angle), -sin(angle), 0], [sin(angle), cos(angle), 0], [0, 0, 1]]

        r_points = get_new_coords(rotate_matrix, [Point(point.x - rx, point.y - ry) for point in hyperbole_points])
        hyperbole_points = [Point(point.x + rx, point.y + ry) for point in r_points]

        r_points = get_new_coords(rotate_matrix, [Point(point.x - rx, point.y - ry) for point in ellipse_points])
        ellipse_points = [Point(point.x + rx, point.y + ry) for point in r_points]
        self.draw_figure()

    def get_rotate_params(self) -> Tuple[float, float, float]:
        rx_str = self.set_rx.text()
        ry_str = self.set_ry.text()
        angle_str = self.set_angle.text()

        params = params_to_float(rx_str, ry_str, angle_str)

        if len(params) == 0:
            return
        rx, ry, angle_p = params

        return rx, ry, angle_p

    def redraw_figure(self):
        global ellipse_points, hyperbole_points, intersection_points
        self.get_change_coeff()

        ellipse_points = [Point(a, b), Point(a + R, b), Point(a, b + R)]
        hyperbole_points = [Point(0, 0), Point(sqrt(c), sqrt(c)), Point(sqrt(2 * c), sqrt(2 * c))]

        self.draw_figure()

    def get_change_coeff(self):
        global a, b, c, R

        a_str = self.set_a.text()
        b_str = self.set_b.text()
        c_str = self.set_c.text()
        r_str = self.set_r.text()
        params = params_to_float(a_str, b_str, c_str, r_str)

        if params is None:
            return
        if not check_radius(params[3]):
            return

        a, b, c, R = params


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
