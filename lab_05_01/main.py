import sys
from time import time

from typing import List, Tuple

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QButtonGroup, QGraphicsEllipseItem, QGraphicsRectItem
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QPen, QColor, QBrush
from matplotlib import pyplot

from dialogs import show_author, show_task, show_instruction, show_err_win
from class_point import Point
from input_checks import params_to_float, validate_circle_spektre_params

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
        uic.loadUi("./template.ui", self)  # временно в корне

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

        self.circle_rb.toggled.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.page_1))
        self.ellipse_rb.toggled.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.page_2))
        self.stackedWidget.setCurrentWidget(self.page_1)

        self.time_test_button.clicked.connect(self.time_test)
        self.draw_circle_button.clicked.connect(self.draw_circle)
        self.draw_spektr_button.clicked.connect(self.draw_circle_spectre)

        self.draw_ellipse_button.clicked.connect(self.draw_ellipse)
        self.draw_ellipse_spektre.clicked.connect(self.draw_ellipse_spectre)

        self.clear_button.clicked.connect(self.clear_scene)

        self.graphicsView.setMouseTracking(True)
        change_color_button
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
        r_max = 1500
        step = 100
        cnt_runs = 500
        algs = [ellipse_brezenhem, ellipse_canonical, ellipse_param, ellipse_middle_point] \
            if self.ellipse_rb.isChecked() else [circle_brezenhem, circle_canonical, circle_param, circle_middle_point]
        run_times = [[] for _ in range(4)]
        for k, alg in enumerate(algs):
            for i in range(1, r_max // step):
                sum_time = 0
                if self.ellipse_rb.isChecked():
                    for _ in range(cnt_runs):
                        start = time()
                        alg(Point(0, 0), step * i, step * i, True)
                        sum_time += time() - start
                else:
                    for _ in range(cnt_runs):
                        start = time()
                        alg(Point(0, 0), step * i, True)
                        sum_time += time() - start
                run_times[k].append(sum_time / cnt_runs)

        range_ = [i for i in range(step, r_max, step)]

        pyplot.figure(figsize=(13, 7))
        pyplot.rcParams['font.size'] = '14'

        pyplot.title(f"Сравнение времени построения {'эллипсов' if self.ellipse_rb.isChecked() else 'окружностей'}"
                     f" для различных алгоритмов")
        pyplot.plot(range_, run_times[0], label='Алгоритм Брезенхема')
        pyplot.plot(range_, run_times[1], label='Каноническое уравнение')
        pyplot.plot(range_, run_times[2], label='Параметрическое уравнение')
        pyplot.plot(range_, run_times[3], label='Алгоритм средней точки')
        pyplot.xticks([_ for _ in range(step, r_max + 1, step)])
        pyplot.legend()
        pyplot.xlabel("Радиус")
        pyplot.ylabel("Время")

        if not FUNC_TESTING:
            pyplot.show()
        else:
            pyplot.savefig(f'./results/time_test_{test_i}.png')

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

    def get_circle_spectre_params(self) -> Tuple[float]:
        unsetted = 0
        unsetted_id = -1

        r_start_str = self.set_r_start.text()
        r_end_str = self.set_r_end.text()
        cnt_str = self.set_circle_count.text()
        step_str = self.set_step.text()
        x_c = self.set_x.text()
        y_c = self.set_y.text()
        params = params_to_float(x_c, y_c)
        if len(params) == 0:
            return

        x_c, y_c = params

        values = [r_start_str, r_end_str, cnt_str, step_str]
        for _ in range(len(values)):
            if values[_] == '':
                unsetted += 1
                unsetted_id = _

        params = validate_circle_spektre_params(unsetted, unsetted_id, values)
        if params is None:
            return
        r_start, r_end, circle_count, step = params
        return r_start, r_end, circle_count, step, x_c, y_c

    def draw_circle_spectre(self, params: List[float] = False) -> None:
        if not params:
            params = self.get_circle_spectre_params()
            if params is None:
                return
        r_start, r_end, n, step, x_c, y_c = params
        points = []
        for i in range(int(n)):
            points.extend(self.get_circle_points(
                Point(x_c, y_c), r_start + i * step))

        for point in points:
            part = QGraphicsRectItem(point.x, -point.y, 1, 1)
            part.setZValue(1)
            part.setPen(current_line_color)
            self.scene.addItem(part)

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
            circle = QGraphicsEllipseItem(-r +
                                          center.x, r - center.y, 2 * r, - 2 * r)
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

    def get_ellipse_params(self) -> Tuple[Point, float, float]:
        x_c_str = self.set_ellipse_x.text()
        y_c_str = self.set_ellipse_y.text()
        width_str = self.set_ellipse_width.text()
        height_str = self.set_ellipse_height.text()

        params = params_to_float(x_c_str, y_c_str, width_str, height_str)
        if len(params) == 0:
            return

        x_c, y_c, width, height = params
        return Point(x_c, y_c), width, height

    def draw_ellipse(self, center: Point = None, width: float = None, height: float = None) -> None:
        if center is None or width is None or height is None:
            params = self.get_ellipse_params()
            if params is None:
                return
            center, width, height = params

        if width <= 0 or height <= 0:
            show_err_win("Радиусы эллипса должны быть больше 0")
            return

        ellipse_points = self.get_ellipse_points(center, width, height)
        if not ellipse_points:
            return
        for point in ellipse_points:
            part = QGraphicsRectItem(point.x, -point.y, 1, 1)
            part.setZValue(1)
            part.setPen(current_line_color)
            self.scene.addItem(part)

    def get_ellipse_points(self, center: Point, width: float, height: float) -> List[Point]:
        if self.brezenhem_rbutton.isChecked():
            return ellipse_brezenhem(center, width, height)
        elif self.canonical_rbutton.isChecked():
            return ellipse_canonical(center, width, height)
        elif self.param_rbutton.isChecked():
            return ellipse_param(center, width, height)
        elif self.middle_point_rbutton.isChecked():
            return ellipse_middle_point(center, width, height)
        elif self.bibl_alg_rbutton.isChecked():
            ellipse = QGraphicsEllipseItem(
                center.x - width, height - center.y, 2 * width, - 2 * height)
            ellipse.setPen(current_line_color)
            ellipse.setZValue(1)
            self.scene.addItem(ellipse)
            return []

    def get_ellipse_spectre_params(self) -> Tuple[float, str]:
        width_str = self.set_spektr_width.text()
        height_str = self.set_spektr_height.text()
        step_x_str = self.set_ellipse_step_x.text()
        step_y_str = self.set_ellipse_step_y.text()
        cnt = self.set_ellipse_count.text()
        x_c = self.set_ellipse_x.text()
        y_c = self.set_ellipse_y.text()
        params = params_to_float(x_c, y_c, width_str, height_str, cnt)
        if len(params) == 0:
            return
        x_c, y_c, width, height, cnt = params
        if abs(cnt - int(cnt)) > 1e-13 or cnt <= 0 or width <= 0 or height <= 0:
            show_err_win("Введены некорректные параметры эллипса")
            return

        unsetted = 0
        unsetted_id = -1
        steps = [step_x_str, step_y_str]
        for _ in range(2):
            try:
                steps[_] = float(steps[_])
            except ValueError:
                unsetted += 1
                unsetted_id = _

        if unsetted != 1:
            return

        if steps[unsetted_id - 1] <= 0:
            return

        return x_c, y_c, width, height, cnt, steps[0], steps[1], unsetted_id

    def draw_ellipse_spectre(self, params: List[float] = False) -> None:
        if not params:
            params = self.get_ellipse_spectre_params()
            if params is None:
                return
        x_c, y_c, width, height, cnt, step_x, step_y, unsetted_ind = params
        points = []
        coeff = width / height

        for i in range(int(cnt)):
            if unsetted_ind == 1:
                width += step_x
                height = round(width / coeff)
            else:
                height += step_y
                width = round(height * coeff)
            points.extend(self.get_ellipse_points(
                Point(x_c, y_c), width, height))
        for point in points:
            part = QGraphicsRectItem(point.x, -point.y, 1, 1)
            part.setZValue(1)
            part.setPen(current_line_color)
            self.scene.addItem(part)


if __name__ == '__main__':
    global test_i
    start_testing = time()
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()

    FUNC_TESTING = False
    if len(sys.argv) > 2:
        FUNC_TESTING = True
        test_i = int(sys.argv[1])
        algs_choice = {'br': window.brezenhem_rbutton, 'can': window.canonical_rbutton, 'param': window.param_rbutton,
                       'mp': window.middle_point_rbutton}
        if sys.argv[2] == 'circle':
            window.circle_rb.setChecked(True)
            if sys.argv[3] == 'time_test':
                window.time_test()
            else:
                xc = float(sys.argv[3])
                yc = float(sys.argv[4])
                radius = float(sys.argv[5])
                algs_choice[sys.argv[6]].setChecked(True)
                window.draw_circle(Point(xc, yc), radius)
        elif sys.argv[2] == 'ellipse':
            window.ellipse_rb.setChecked(True)
            if sys.argv[3] == 'time_test':
                window.time_test()
            else:
                xc = float(sys.argv[3])
                yc = float(sys.argv[4])
                width_ = float(sys.argv[5])
                height_ = float(sys.argv[6])
                algs_choice[sys.argv[7]].setChecked(True)
                window.draw_ellipse(Point(xc, yc), width_, height_)
        elif sys.argv[2] == 'circle_spectre':
            window.circle_rb.setChecked(True)
            xc = float(sys.argv[3])
            yc = float(sys.argv[4])
            r_start_ = float(sys.argv[5])
            r_end_ = float(sys.argv[6])
            circle_cnt_ = int(sys.argv[7])
            step_ = float(sys.argv[8])
            algs_choice[sys.argv[9]].setChecked(True)
            window.draw_circle_spectre(
                [r_start_, r_end_, circle_cnt_, step_, xc, yc])
        elif sys.argv[2] == 'ellipse_spectre':
            xc = float(sys.argv[3])
            yc = float(sys.argv[4])
            width_ = float(sys.argv[5])
            height_ = float(sys.argv[6])
            try:
                step_x_ = float(sys.argv[7])
                unsetted_i = 1
                step_y_ = ''
            except ValueError:
                step_x_ = ''
                unsetted_i = 0
                step_y_ = float(sys.argv[8])
            ellipse_cnt_ = int(sys.argv[9])
            algs_choice[sys.argv[10]].setChecked(True)
            window.draw_ellipse_spectre(
                [xc, yc, width_, height_, ellipse_cnt_, step_x_, step_y_, unsetted_i])

    if FUNC_TESTING:
        screenshot = window.grab()
        screenshot.save(f'./results/test_{test_i}.png', 'png')
        time_elapsed = (time() - start_testing) * 1000
        with open('report-functesting-latest.txt', 'a+') as f:
            f.write(f'{test_i}. Time elapsed: {time_elapsed:.3f} mc.\n')
    else:
        sys.exit(app.exec_())
