import sys
from time import time

from typing import List, Tuple

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QButtonGroup, QGraphicsEllipseItem, QGraphicsRectItem
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QPen, QColor, QBrush

from dialogs import show_author, show_task, show_instruction, show_err_win
from class_point import Point
from input_checks import params_to_float
from circle_algs import circle_brezenhem, circle_canonical, circle_param, circle_middle_point

grid_lines: List[QGraphicsLineItem] = []
max_win_size: List[int] = [0, 0, 0]

scale: float = 1.0
num_tests: int = 50

is_pressed: bool = False

last_pos: QPoint = None
current_line_color: QColor = QColor(255, 0, 0)


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("./lab_04/template.ui", self)  # временно в корне

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.need_grid()
        self.add_grid()

        # menu bar
        self.about_author.triggered.connect(show_author)
        self.about_task.triggered.connect(show_task)
        self.instruction.triggered.connect(show_instruction)

        # add button group so that other will stay unchecked
        self.figure_color_group = QButtonGroup()
        self.bg_color_group = QButtonGroup()
        self.alg_group = QButtonGroup()

        self.figure_color_group.addButton(self.blue_figure_rbutton)
        self.figure_color_group.addButton(self.red_figure_rbutton)
        self.figure_color_group.addButton(self.green_figure_rbutton)
        self.figure_color_group.addButton(self.aqua_figure_rbutton)
        self.figure_color_group.addButton(self.purple_figure_rbutton)
        self.figure_color_group.addButton(self.yellow_figure_rbutton)

        self.bg_color_group.addButton(self.blue_bg_rbutton)
        self.bg_color_group.addButton(self.red_bg_rbutton)
        self.bg_color_group.addButton(self.green_bg_rbutton)
        self.bg_color_group.addButton(self.aqua_bg_rbutton)
        self.bg_color_group.addButton(self.purple_bg_rbutton)
        self.bg_color_group.addButton(self.gray_bg_rbutton)

        self.alg_group.addButton(self.brezenhem_rbutton)
        self.alg_group.addButton(self.canonical_rbutton)
        self.alg_group.addButton(self.param_rbutton)
        self.alg_group.addButton(self.middle_point_rbutton)
        self.alg_group.addButton(self.bibl_alg_rbutton)

        # !!! radio buttons setChecked (setup default config)
        self.circle_rb.setChecked(True)
        self.red_figure_rbutton.setChecked(True)
        self.gray_bg_rbutton.setChecked(True)
        self.bibl_alg_rbutton.setChecked(True)

        # figure color radio buttons
        self.blue_figure_rbutton.clicked.connect(
            lambda: self.set_figure_color(Qt.blue))
        self.red_figure_rbutton.clicked.connect(
            lambda: self.set_figure_color(Qt.red))
        self.green_figure_rbutton.clicked.connect(
            lambda: self.set_figure_color(Qt.darkGreen))
        self.aqua_figure_rbutton.clicked.connect(
            lambda: self.set_figure_color(Qt.darkCyan))
        self.purple_figure_rbutton.clicked.connect(
            lambda: self.set_figure_color(Qt.darkMagenta))
        self.yellow_figure_rbutton.clicked.connect(
            lambda: self.set_figure_color(Qt.darkYellow))

        # background color radio buttons
        self.blue_bg_rbutton.clicked.connect(
            lambda: self.set_bg_color(Qt.blue))
        self.red_bg_rbutton.clicked.connect(lambda: self.set_bg_color(Qt.red))
        self.green_bg_rbutton.clicked.connect(
            lambda: self.set_bg_color(Qt.darkGreen))
        self.aqua_bg_rbutton.clicked.connect(
            lambda: self.set_bg_color(Qt.darkCyan))
        self.purple_bg_rbutton.clicked.connect(
            lambda: self.set_bg_color(Qt.darkMagenta))
        self.gray_bg_rbutton.clicked.connect(
            lambda: self.set_bg_color(QColor(56, 56, 56)))

        self.circle_rb.toggled.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_1))
        self.ellipse_rb.toggled.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_2))
        self.stackedWidget.setCurrentWidget(self.page_1)

        self.time_test_button.clicked.connect(self.time_test)
        self.draw_circle_button.clicked.connect(self.draw_circle)
        self.draw_spektr_button.clicked.connect(self.draw_circle_spectre)
        self.clear_button.clicked.connect(self.clear_scene)

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

        # Получаем текущий масштаб по оси X (и Y)
        scale = self.graphicsView.transform().m11()
        if self.need_grid():
            for grid_line in grid_lines:
                if grid_line in self.scene.items():
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
            self.graphicsView.horizontalScrollBar().setValue(
                self.graphicsView.horizontalScrollBar().value() - dx)
            self.graphicsView.verticalScrollBar().setValue(
                self.graphicsView.verticalScrollBar().value() - dy)
            last_pos = event.pos()
            if self.need_grid():
                for grid_line in grid_lines:
                    if grid_line in self.scene.items():
                        self.scene.removeItem(grid_line)
                self.add_grid()
        scene_pos = self.graphicsView.mapToScene(event.pos())
        self.current_coords_label.setText(
            f'x :{scene_pos.x():.2f}, y :{-scene_pos.y():.2f}')

    def mousePressEvent(self, event: QMouseEvent) -> None:
        global last_pos, is_pressed
        if event.button() == Qt.LeftButton:
            is_pressed = True
            last_pos = event.pos()

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

    def add_grid(self) -> None:
        global grid_lines, max_win_size
        max_width = max_win_size[0]
        max_height = max_win_size[1]
        grid_interval = max_win_size[2]
        if grid_interval == 0:
            grid_interval = 20
        self.current_grid_label.setText(f'Текущий шаг сетки: {grid_interval}')
        start_grid_width = - ((max_width // 2) +
                              grid_interval - (max_width // 2) % grid_interval)
        start_grid_height = - \
            ((max_height // 2) + grid_interval - (max_height // 2) % grid_interval)
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

    def set_figure_color(self, color: QColor) -> None:
        global current_line_color
        current_line_color = color
        objects = self.scene.items()
        for obj in objects:
            if obj not in grid_lines:
                obj.setPen(current_line_color)

    def set_bg_color(self, color: QColor) -> None:
        background_brush = QBrush(color)
        self.graphicsView.setBackgroundBrush(background_brush)

    def clear_scene(self):
        for item in self.scene.items():
            if item not in grid_lines:
                self.scene.removeItem(item)

    def time_test(self):
        pass

    def draw_circle(self, center: Point = None, r: float = None):
        if center is None or r is None:
            params = self.get_circle_params()
            if params is None:
                return
            center, r = params

        if r <= 0.0:
            show_err_win("Радиус должен быть положительным числом")
            return

        circle_points = self.get_circle_points(center, r)
        if not circle_points:
            return
        for point in circle_points:
            part = QGraphicsRectItem(point.x, -point.y, 1, 1)
            part.setZValue(1)
            part.setPen(current_line_color)
            self.scene.addItem(part)

    def draw_circle_spectre(self):
        pass

    def get_circle_points(self, center: Point, r: float) -> List[Point]:
        if self.brezenhem_rbutton.isChecked():
            return circle_brezenhem(center, r)
        elif self.canonical_rbutton.isChecked():
            return circle_canonical(center, r)
        elif self.param_rbutton.isChecked():
            return circle_param(center, r)
        elif self.middle_point_rbutton.isChecked():
            return circle_middle_point(center, r)
        elif self.bibl_alg_rbutton.isChecked():
            circle = QGraphicsEllipseItem(-r + center.x, r - center.y, 2 * r, - 2 * r)
            circle.setPen(current_line_color)
            circle.setZValue(1)
            self.scene.addItem(circle)
            return []

    def get_circle_params(self) -> Tuple[Point, float]:
        x_c_str = self.set_x.text()
        y_c_str = self.set_y.text()
        r_str = self.set_r.text()
        params = params_to_float(x_c_str, y_c_str, r_str)

        if len(params) == 0:
            return

        x_c, y_c, r = params
        return Point(x_c, y_c), r


if __name__ == '__main__':
    global test_i
    start_testing = time()
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()

    FUNC_TESTING = False
    if len(sys.argv) > 7:
        FUNC_TESTING = True
        test_i = int(sys.argv[1])
        if sys.argv[7] == 'br_int':
            window.brezenhem_int_rbutton.setChecked(True)
        elif sys.argv[7] == 'br_float':
            window.brezenhem_float_rbutton.setChecked(True)
        elif sys.argv[7] == 'cda':
            window.cda_alg_rbutton.setChecked(True)
        elif sys.argv[7] == 'vu':
            window.vu_alg_rbutton.setChecked(True)
        elif sys.argv[7] == 'bibl':
            window.bibl_alg_rbutton.setChecked(True)
        elif sys.argv[7] == 'br_st':
            window.brezenhem_st_rbutton.setChecked(True)

        if sys.argv[2] == 'segment':
            x_1 = float(sys.argv[3])
            y_1 = float(sys.argv[4])
            x_2 = float(sys.argv[5])
            y_2 = float(sys.argv[6])

            window.draw_segment(Point(x_1, y_1), Point(x_2, y_2))

        elif sys.argv[2] == 'spectre':
            xc_ = float(sys.argv[3])
            yc_ = float(sys.argv[4])
            angle_ = float(sys.argv[5])
            length_ = float(sys.argv[6])

            if sys.argv[7] == 'time_test':
                window.time_test(xc_, yc_, angle_, length_)
            else:
                window.draw_spectre(Point(xc_, yc_), angle_, length_)

    if FUNC_TESTING:
        screenshot = window.grab()
        screenshot.save(f'./results/test_{test_i}.png', 'png')
        time_elapsed = (time() - start_testing) * 1000
        with open('report-functesting-latest.txt', 'a+') as f:
            f.write(f'{test_i}. Time elapsed: {time_elapsed:.2f} mc.\n')
    else:
        sys.exit(app.exec_())
