import sys
from typing import List

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QPen, QColor, QWheelEvent, QMouseEvent
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem

from dialogs import show_author, show_task, show_instruction
from input_checks import params_to_float
from class_point import Point
from matrix_methods import get_new_coords
from figure_methods import fill_point_lists

hyperbole_points: List[Point] = []
circle_points: List[Point] = []
intersection_points: List[Point] = []
grid_lines: List[QGraphicsLineItem] = []

scale: float = 1.0
step: int = int(scale) * 10
max_win_size: List[int] = [0, 0, 0]
a: float = 0.0
b: float = 0.0
c: float = 100.0
R: float = 50

is_pressed: bool = False
last_pos: bool = None


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("./lab_02_19/template.ui", self)

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.need_grid()
        self.add_grid()
        self.draw_figure()

        self.redBrush = QBrush(Qt.red)
        self.pen = QPen(Qt.red)

        # menu bar
        self.about_author.triggered.connect(show_author)
        self.about_task.triggered.connect(show_task)
        self.instruction.triggered.connect(show_instruction)

        self.move_action_button.clicked.connect(self.move_figure)
        self.scale_action_button.clicked.connect(self.scale_figure)

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
                    self.scene.removeItem(grid_line)
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

    def move_figure(self) -> None:
        global hyperbole_points, circle_points, intersection_points

        dx, dy = self.get_move_params()

        move_matrix = [[1, 0, dx], [0, 1, dy], [0, 0, 1]]

        hyperbole_points = get_new_coords(move_matrix, hyperbole_points)
        circle_points = get_new_coords(move_matrix, circle_points)
        intersection_points = get_new_coords(move_matrix, intersection_points)
        self.draw_figure()

    def draw_figure(self) -> None:
        global circle_points, hyperbole_points, intersection_points
        circle_points, hyperbole_points, intersection_points = fill_point_lists(a, b, c, R, max_win_size)
        print(len(hyperbole_points))

        self.draw_parts(hyperbole_points, Qt.green)
        self.draw_parts(circle_points, Qt.red)
        self.draw_lines(intersection_points)

    def draw_parts(self, points: List[Point], color: QColor) -> None:
        for i in range(len(points) - 1):
            line_item = QGraphicsLineItem(points[i].x, -points[i].y, points[i + 1].x, -points[i + 1].y)
            line_item.setPen(QPen(color))
            self.scene.addItem(line_item)

    def draw_lines(self, points: List[Point]) -> None:
        pass

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
            grid_lines.append(line)
            self.scene.addItem(line)
        for y in range(start_grid_height, end_grid_height, grid_interval):
            line = QGraphicsLineItem(start_grid_width, y, end_grid_width, y)
            line.setPen(pen)
            grid_lines.append(line)
            self.scene.addItem(line)

        axis_x = QGraphicsLineItem(-300 * (1 / scale), 0, 300 * (1 / scale), 0)
        axis_y = QGraphicsLineItem(0, -300 * (1 / scale), 0, 300 * (1 / scale))
        pen.setColor(Qt.white)
        grid_lines.append(axis_x)
        grid_lines.append(axis_y)
        axis_x.setPen(pen)
        axis_y.setPen(pen)
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

        return kx, ky, cx, cy

    def scale_figure(self) -> None:
        global hyperbole_points, circle_points, intersection_points

        kx, ky, cx, cy = self.get_scale_params()
        # print(kx, ky, cx, cy)

        move_matrix = [[1, 0, -cx], [0, 1, -cy], [0, 0, 1]]
        scale_matrix = [[kx, 0, 0], [0, ky, 0], [0, 0, 1]]
        move_matrix_back = [[1, 0, cx], [0, 1, cy], [0, 0, 1]]

        hyperbole_points = get_new_coords(move_matrix, hyperbole_points)
        circle_points = get_new_coords(move_matrix, circle_points)
        intersection_points = get_new_coords(move_matrix, intersection_points)

        hyperbole_points = get_new_coords(scale_matrix, hyperbole_points)
        circle_points = get_new_coords(scale_matrix, circle_points)
        intersection_points = get_new_coords(scale_matrix, intersection_points)

        hyperbole_points = get_new_coords(move_matrix_back, hyperbole_points)
        circle_points = get_new_coords(move_matrix_back, circle_points)
        intersection_points = get_new_coords(move_matrix_back, intersection_points)
        self.draw_figure()

    def get_new_coeff(self):
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
