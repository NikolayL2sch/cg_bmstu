import sys

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QMouseEvent, QFont, QColor, QBrush, QWheelEvent
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem
from typing import List, Union, Tuple

from dialogs import show_war_win, show_err_win, show_author, show_task, show_instruction
from triangle_methods import find_min_angle
from class_point import Point

point_list: List[Point] = []
scene_point_list: List[QGraphicsEllipseItem] = []
grid_lines: List[QGraphicsLineItem] = []
point_scale: List[float] = []
triangle_lines: List[QGraphicsLineItem] = []
coords_desc: List[QGraphicsTextItem] = []

scale: float = 1.0
max_win_size: List[int] = [0, 0, 0]

dragging: bool = False
is_pressed: bool = False
last_pos: bool = None


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("./lab_01_31/template.ui", self)

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self.need_grid()
        self.add_grid()

        self.redBrush = QBrush(Qt.red)
        self.pen = QPen(Qt.red)

        self.add_point_button.clicked.connect(self.add_point)
        self.del_point_button.clicked.connect(self.del_point)
        self.solve_task_button.clicked.connect(self.draw_solution)

        self.about_author.triggered.connect(show_author)
        self.about_task.triggered.connect(show_task)
        self.instruction.triggered.connect(show_instruction)

        self.graphicsView.mousePressEvent = self.mousePressEvent
        self.graphicsView.wheelEvent = self.wheel_event
        self.graphicsView.mouseReleaseEvent = self.mouseReleaseEvent
        self.graphicsView.mouseMoveEvent = self.mouseMoveEvent

        self.show()

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

    def add_point(self) -> None:
        coords = self.get_coords_from_field()
        if coords is not None:
            self.draw_point(coords[0], -coords[1])

    def get_coords_from_field(self) -> Union[Tuple[float, float], None]:
        x_txt = self.set_x_field.text()
        y_txt = self.set_y_field.text()
        if x_txt == '' or y_txt == '':
            show_err_win("Не введены координаты точки.")
        else:
            try:
                x, y = float(x_txt), float(y_txt)
                self.clear_fields()
                return x, y
            except ValueError:
                show_err_win("Введены некорректные символы.")

    def add_point_by_click(self, event: QMouseEvent) -> None:
        pos = event.pos()
        scene_pos = self.graphicsView.mapToScene(pos)
        p_x, p_y = scene_pos.x(), scene_pos.y()
        self.draw_point(p_x, p_y)

    def clear_fields(self) -> None:
        self.set_y_field.setText('')
        self.set_x_field.setText('')

    def del_point(self) -> None:
        coords = self.get_coords_from_field()
        if coords is not None:
            del_point = Point(coords[0], coords[1])
            for i in range(len(point_list)):
                if point_list[i] == del_point:
                    self.scene.removeItem(scene_point_list[i])
                    self.scene.removeItem(coords_desc[i])
                    coords_desc.pop(i)
                    point_list.pop(i)
                    scene_point_list.pop(i)
                    point_scale.pop(i)
                    self.update_scroll_list()
                    break
            self.clear_fields()

    def update_scroll_list(self) -> None:
        self.scroll_list.clear()
        for i in range(len(point_list)):
            self.scroll_list.addItem(f'{i + 1}.({round(point_list[i].x, 2)}; {round(point_list[i].y, 2)})')

    def draw_point(self, p_x: float, p_y: float) -> None:
        new_point = Point(p_x, -p_y)
        for point in point_list:
            if point == new_point:
                show_war_win("Введенная точка уже существует.")
                break
        else:
            point_list.append(new_point)
            self.scroll_list.addItem(f'{len(point_list)}.({round(p_x, 2)}; {round(-p_y, 2)})')
            point_scale.append(1 / scale)
            point_coords_label = QGraphicsTextItem(f'x:({p_x:.2f}, y:{-p_y:.2f})')
            coords_desc.append(point_coords_label)

            point = QGraphicsEllipseItem(p_x, p_y, 5 * (1 / scale), 5 * (1 / scale))
            point.setBrush(self.redBrush)
            self.scene.addItem(point)

            point_coords_label.setPos(point.rect().center().x() + 10, point.rect().center().y())

            point_coords_label.setDefaultTextColor(QColor(255, 255, 255))
            font = QFont()
            font.setPointSize(8)
            point_coords_label.setFont(font)
            self.scene.addItem(point_coords_label)

            scene_point_list.append(point)

    def del_point_by_click(self, event: QMouseEvent) -> None:
        pos = event.pos()
        scene_pos = self.graphicsView.mapToScene(pos)
        min_diff = 100 * (1 / scale)
        if min_diff < 1:
            min_diff = 1
        del_point_id = -1
        for i in range(len(point_list)):
            if abs(scene_pos.x() - point_list[i].x) + abs(scene_pos.y() + point_list[i].y) < min_diff:
                min_diff = abs(scene_pos.x() - point_list[i].x) + abs(scene_pos.y() + point_list[i].y)
                del_point_id = i
        if min_diff > 10 * (1 / scale):
            show_err_win("Кажется, вы пытаетесь удалить несуществующую точку.\nПопробуйте кликнуть ближе к точке.")
        else:
            self.scene.removeItem(scene_point_list[del_point_id])
            point_list.pop(del_point_id)
            scene_point_list.pop(del_point_id)
            point_scale.pop(del_point_id)
            self.scene.removeItem(coords_desc[del_point_id])
            coords_desc.pop(del_point_id)
            self.update_scroll_list()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        global last_pos, is_pressed
        if event.button() == Qt.LeftButton:
            is_pressed = True
            last_pos = event.pos()
        elif event.button() == Qt.RightButton:
            self.del_point_by_click(event)

    def draw_solution(self) -> None:
        global triangle_lines
        if triangle_lines:
            for line in triangle_lines:
                self.scene.removeItem(line)

        result = find_min_angle(point_list)
        if result is None:
            return
        vertexes, v_p, v_m, min_angle = result

        if v_p is None or v_m is None or min_angle is None:
            return

        side_1 = QGraphicsLineItem(vertexes[0].x, -vertexes[0].y, vertexes[1].x, -vertexes[1].y)
        side_2 = QGraphicsLineItem(vertexes[1].x, -vertexes[1].y, vertexes[2].x, -vertexes[2].y)
        side_3 = QGraphicsLineItem(vertexes[2].x, -vertexes[2].y, vertexes[0].x, -vertexes[0].y)

        perpend = QGraphicsLineItem(vertexes[0].x, -vertexes[0].y, vertexes[0].x + v_p.x(), -vertexes[0].y - v_p.y())
        median = QGraphicsLineItem(vertexes[0].x, -vertexes[0].y, vertexes[0].x + v_m.x(), -vertexes[0].y - v_m.y())

        pen_sides = QPen(Qt.magenta)
        pen_median = QPen(Qt.green)
        pen_perpend = QPen(Qt.yellow)

        side_1.setPen(pen_sides)
        side_2.setPen(pen_sides)
        side_3.setPen(pen_sides)
        perpend.setPen(pen_perpend)
        median.setPen(pen_median)

        triangle_lines = [side_1, side_2, side_3, perpend, median]

        self.scene.addItem(side_1)
        self.scene.addItem(side_2)
        self.scene.addItem(side_3)
        self.scene.addItem(perpend)
        self.scene.addItem(median)
        show_war_win(f"Задача решена.\nМинимальный угол: {min_angle}°")

    def wheel_event(self, event: QWheelEvent) -> None:
        global scale
        factor = 1.2

        if event.angleDelta().y() > 0:
            self.graphicsView.scale(factor, factor)
        else:
            self.graphicsView.scale(1.0 / factor, 1.0 / factor)

        scale = self.graphicsView.transform().m11()  # Получаем текущий масштаб по оси X (и Y)
        for i in range(len(scene_point_list)):
            point = scene_point_list[i]
            point.setTransformOriginPoint(point.boundingRect().center())
            point.setScale(1 / (scale * point_scale[i]))
        if self.need_grid():
            for grid_line in grid_lines:
                self.scene.removeItem(grid_line)
            self.add_grid()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        global dragging, is_pressed
        if event.button() == Qt.LeftButton:
            if not dragging:
                self.add_point_by_click(event)
            dragging = False
            is_pressed = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        global last_pos, dragging
        if is_pressed:
            dragging = True
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
        self.current_coords_label.setText(f'x :{scene_pos.x():.2f}, y :{scene_pos.y():.2f}')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
