import sys
from time import time

from typing import List

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsTextItem, QColorDialog, \
    QGraphicsRectItem
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QPen, QColor, QFont, QKeyEvent

from dialogs import show_author, show_task, show_instruction, show_war_win
from class_point import Point

grid_lines: List[QGraphicsLineItem] = []
max_win_size: List[int] = [0, 0, 0]
point_list: List[Point] = []
point_scale: List[float] = []
coords_desc: List[QGraphicsTextItem] = []
scene_point_list: List[QGraphicsEllipseItem] = []
segments: List[List[Point]] = []

scale: float = 1.0

is_pressed: bool = False
dragging: bool = False
enter_cutoff: bool = False
enter_vert_segment: bool = False
enter_hor_segment: bool = False

last_pos: QPoint = None
current_edge_color: QColor = QColor(255, 0, 0)
current_cutoff_color: QColor = QColor(0, 0, 255)

tmp_vert_segment: QGraphicsLineItem = None
tmp_hor_segment: QGraphicsLineItem = None


def change_segment_color() -> None:
    colour = QColorDialog.getColor(initial=current_cutoff_color)
    if colour.isValid():
        if colour.getRgb() != current_cutoff_color.getRgb():
            set_segment_color(QColor(colour))
        else:
            show_war_win("Цвет отсекателя и отрезков не могут совпадать.")


def set_segment_color(color: QColor) -> None:
    global current_edge_color
    current_edge_color = color


def set_cutoff_color(color: QColor) -> None:
    global current_cutoff_color
    current_cutoff_color = color


def change_cutoff_color() -> None:
    colour = QColorDialog.getColor(initial=current_cutoff_color)
    if colour.isValid():
        if colour.getRgb() != current_edge_color.getRgb():
            set_cutoff_color(QColor(colour))
        else:
            show_war_win("Цвет отсекателя и отрезков не могут совпадать.")


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("./lab_07_03/template.ui", self)  # временно в корне

        self.rect = []
        self.scene_rect = None

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self.need_grid()

        self.add_grid()

        # menu bar
        self.about_author.triggered.connect(show_author)
        self.about_task.triggered.connect(show_task)
        self.instruction.triggered.connect(show_instruction)

        self.clear_button.clicked.connect(self.clear_scene)

        self.graphicsView.setMouseTracking(True)

        # push buttons
        self.add_cutoff_button.clicked.connect(self.add_cutoff)
        self.change_cutoff_color_button.clicked.connect(change_cutoff_color)
        self.change_segment_color_button.clicked.connect(change_segment_color)
        self.add_segment_cutoff_button.clicked.connect(self.add_segment_cutoff)
        self.cutoff_button.clicked.connect(self.cutoff)

        # graphics view mouse events
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
        for i in range(len(scene_point_list)):
            point = scene_point_list[i]
            point.setTransformOriginPoint(point.boundingRect().center())
            point.setScale(1 / (scale * point_scale[i]))
        if self.need_grid():
            for grid_line in grid_lines:
                if grid_line in self.scene.items():
                    self.scene.removeItem(grid_line)
            self.add_grid()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        global is_pressed, dragging, enter_vert_segment, enter_hor_segment
        if event.button() == Qt.LeftButton:
            if not dragging and not enter_cutoff:
                self.add_point_by_click(event)
            enter_vert_segment = False
            enter_hor_segment = False
            dragging = False
            is_pressed = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        global last_pos, dragging
        if is_pressed:
            dragging = True
            last_scene_pos = self.graphicsView.mapToScene(last_pos)
            cur_scene_pos = self.graphicsView.mapToScene(event.pos())
            if enter_cutoff:
                for elem in self.scene.items():
                    if isinstance(elem, QGraphicsRectItem):
                        self.scene.removeItem(elem)
                        break
                tmp_rect = QGraphicsRectItem(last_scene_pos.x(), last_scene_pos.y(),
                                             cur_scene_pos.x() - last_scene_pos.x(),
                                             cur_scene_pos.y() - last_scene_pos.y())
                tmp_rect.setPen(current_cutoff_color)
                self.scene.addItem(tmp_rect)
                self.scene_rect = tmp_rect
                self.rect = [last_scene_pos.x(), last_scene_pos.y(), cur_scene_pos.x(), cur_scene_pos.y()]

            elif enter_vert_segment:
                global tmp_vert_segment
                if tmp_vert_segment:
                    self.scene.removeItem(tmp_vert_segment)
                tmp_vert_segment = QGraphicsLineItem(last_scene_pos.x(), last_scene_pos.y(),
                                                     cur_scene_pos.x(), last_scene_pos.y())
                tmp_vert_segment.setPen(current_edge_color)
                self.scene.addItem(tmp_vert_segment)
            elif enter_hor_segment:
                pass
            else:
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

    def keyPressEvent(self, event: QKeyEvent) -> None:
        global enter_vert_segment, enter_hor_segment
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Control and event.modifiers() & Qt.ControlModifier:
            enter_vert_segment = True
            enter_hor_segment = False
        elif event.key() == Qt.Key_Shift and event.modifiers() & Qt.ControlModifier:
            enter_hor_segment = True
            enter_vert_segment = False

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

    def change_color(self, color: QColor) -> None:
        global current_edge_color
        current_edge_color = color
        objects = self.scene.items()
        for obj in objects:
            if obj not in grid_lines and not isinstance(obj, QGraphicsTextItem):
                obj.setPen(current_edge_color)

    def clear_scene(self):
        for item in self.scene.items():
            if item not in grid_lines:
                self.scene.removeItem(item)
        point_list.clear()
        point_scale.clear()
        coords_desc.clear()
        scene_point_list.clear()
        self.scroll_list.clear()

    def add_point_by_click(self, event: QMouseEvent) -> None:
        pos = event.pos()
        scene_pos = self.graphicsView.mapToScene(pos)
        p_x, p_y = scene_pos.x(), scene_pos.y()
        self.draw_point(Point(p_x, -p_y))

    def draw_point(self, point: Point) -> None:
        for _ in point_list:
            if point == _:
                show_war_win("Введенная точка уже существует.")
                break
        else:
            point_list.append(point)
            self.scroll_list.addItem(
                f'{len(point_list)}.({round(point.x, 2)}; {round(point.y, 2)})')
            point_scale.append(1 / scale)
            scene_point = QGraphicsEllipseItem(
                point.x, -point.y, 5 * (1 / scale), 5 * (1 / scale))
            scene_point.setBrush(current_edge_color)
            self.scene.addItem(scene_point)
            self.add_point_label(scene_point, point)

            if len(point_list) % 2 == 1:
                segments.append([point_list[-1]])
            else:
                segments[-1].append(point_list[-1])
                self.draw_line(point_list[-2], point_list[-1])
            scene_point_list.append(scene_point)

    def add_point_label(self, scene_point: QGraphicsEllipseItem, point: Point) -> None:
        point_coords_label = QGraphicsTextItem(
            f'x:({point.x:.2f}, y:{point.y:.2f})')
        coords_desc.append(point_coords_label)
        point_coords_label.setPos(
            scene_point.rect().center().x() + 10, scene_point.rect().center().y())

        point_coords_label.setDefaultTextColor(QColor(255, 255, 255))
        font = QFont()
        font.setPointSize(8)
        point_coords_label.setFont(font)
        point_coords_label.setZValue(1)
        self.scene.addItem(point_coords_label)

    def draw_line(self, p1: Point, p2: Point) -> None:
        line = QGraphicsLineItem(p1.x, -p1.y, p2.x, -p2.y)
        line.setPen(current_edge_color)
        line.setZValue(1)
        self.scene.addItem(line)

    def update_scroll_list(self) -> None:
        self.scroll_list.clear()
        for i in range(len(point_list)):
            self.scroll_list.addItem(
                f'{i + 1}.({round(point_list[i].x, 2)}; {round(point_list[i].y, 2)})')

    def set_new_colour(self) -> None:
        colour = QColorDialog.getColor(initial=current_edge_color)
        if colour.isValid():
            self.change_color(QColor(colour))

    def add_cutoff(self) -> None:
        global enter_cutoff
        enter_cutoff = True if not enter_cutoff else False
        if enter_cutoff:
            self.add_cutoff_button.setText("Закончить добавление отсекателя")
        else:
            self.add_cutoff_button.setText("Добавить отсекатель")
        self.rect = []
        self.scene_rect = None

    def add_segment_cutoff(self) -> None:
        pass

    def cutoff(self) -> None:
        pass


if __name__ == '__main__':
    global test_i
    start_testing = time()
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()

    FUNC_TESTING = False
    if len(sys.argv) > 2:
        FUNC_TESTING = True
        test_i = int(sys.argv[1])
        num_points = int(sys.argv[2])
        for _ in range(num_points):
            window.add_point(
                Point(float(sys.argv[2 * _ + 3]), float(sys.argv[2 * _ + 4])))
        if sys.argv[-1] == 'true':
            window.set_delay_cb.setChecked(True)
        window.close_figure()
        window.paint_figures(func_testing=True)

    if FUNC_TESTING:
        screenshot = window.grab()
        screenshot.save(f'./results/test_{test_i}.png', 'png')
    else:
        sys.exit(app.exec_())
