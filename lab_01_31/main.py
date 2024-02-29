import sys

from PyQt5 import QtWidgets, QtGui
from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint, QRectF
from PyQt5.QtGui import QPainterPath, QPen, QBrush, QPainter, QImage, QPolygonF, QPolygon, QColor
from PyQt5.QtWidgets import QMessageBox, QGraphicsScene, QGraphicsView, QGraphicsPathItem, QGraphicsEllipseItem, \
    QGraphicsLineItem

from class_point import *

point_list = []


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("template.ui", self)

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self.add_grid()
        self.greenBrush = QBrush(Qt.green)
        self.redBrush = QBrush(Qt.red)
        self.blueBrush = QBrush(Qt.blue)

        self.pen = QPen(Qt.red)

        self.add_point_button.clicked.connect(self.add_point)
        self.about_author.triggered.connect(self.show_author)
        self.about_task.triggered.connect(self.show_task)
        self.del_point_button.clicked.connect(self.del_point)
        self.graphicsView.mousePressEvent = self.on_graphicsview_click
        self.show()

    def add_grid(self):
        max_size = self.graphicsView.maximumSize()
        max_width = max_size.width()
        max_height = max_size.height()

        grid_interval = 30
        start_grid_width = - ((max_width // 2) + grid_interval - (max_width // 2) % grid_interval)
        start_grid_height = - ((max_height // 2) + grid_interval - (max_height // 2) % grid_interval)
        end_grid_width = (max_width // 2) - (max_width // 2) % grid_interval
        end_grid_height = (max_height // 2) - (max_width // 2) % grid_interval
        pen = QPen(Qt.darkGray)

        for x in range(start_grid_width, end_grid_width, grid_interval):
            line = QGraphicsLineItem(x, start_grid_height, x, end_grid_height)
            line.setPen(pen)
            self.scene.addItem(line)
        for y in range(start_grid_height, end_grid_height, grid_interval):
            line = QGraphicsLineItem(start_grid_width, y, end_grid_width, y)
            line.setPen(pen)
            self.scene.addItem(line)

        axis_x = QGraphicsLineItem(-300, 0, 300, 0)
        axis_y = QGraphicsLineItem(0, -300, 0, 300)
        pen.setColor(Qt.white)
        axis_x.setPen(pen)
        axis_y.setPen(pen)
        self.scene.addItem(axis_x)
        self.scene.addItem(axis_y)

    def add_point(self):
        x_txt = self.set_x_field.text()
        y_txt = self.set_y_field.text()
        if x_txt == '' or y_txt == '':
            self.show_err_win("Не введены координаты точки.")
        else:
            try:
                x, y = float(x_txt), float(y_txt)
                new_point = Point(x, y)
                flag = False
                for point in point_list:
                    if point == new_point:
                        self.show_war_win("Введенная точка уже существует.")
                        break
                else:
                    if abs(x) > 700 or abs(y) > 420:
                        self.show_err_win("Точка за пределами сетки")
                    point_list.append(new_point)
                    self.scroll_list.addItem(f'{len(point_list)}.({round(x, 2)}; {round(y, 2)})')
                    self.draw_point(x, y)
                    self.clear_fields()
            except:
                self.show_err_win("Введены некорректные символы.")

    def add_point_by_click(self, event):
        pos = event.pos()
        scene_pos = self.graphicsView.mapToScene(pos)
        p_x, p_y = scene_pos.x(), scene_pos.y()
        point = QGraphicsEllipseItem(p_x, p_y, 4, 4)
        point.setBrush(self.redBrush)
        self.scene.addItem(point)
        point.setPos(p_x, p_y)
        point_list.append(Point(p_x, p_y))
        self.scroll_list.addItem(f'{len(point_list)}.({round(p_x, 2)}; {round(p_y, 2)})')

    def show_err_win(self, err):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(err)
        msg.setWindowTitle("Ошибка!")
        msg.exec_()

    def show_war_win(self, war):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(war)
        msg.setWindowTitle("Предупреждение!")
        msg.exec_()

    def clear_fields(self):
        self.set_y_field.setText('')
        self.set_x_field.setText('')

    def show_author(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Об авторе")
        msg.setText(f"Лабораторная работа №1.\nРазработал Миленко Николай ИУ7-45Б")
        msg.exec_()

    def del_point(self):
        pass

    def show_task(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Условие задачи")
        msg.setText(f"На плоскости дано множество точек.\n\nНайти такой треугольник с вершинами в этих точках, "
                    f"у которого угол, образованный высотой и медианой, исходящими из одной вершины, минимален.\n\n"
                    f"Вывести изображение в графическом режиме.\n\n31 Вариант.")
        msg.exec_()

    def draw_point(self, p_x, p_y):
        point = QGraphicsEllipseItem(p_x, p_y, 4, 4)
        point.setBrush(self.redBrush)
        point.setPos(p_x, p_y)
        self.scene.addItem(point)

    def del_point_by_click(self, event):
        pos = event.pos()
        scene_pos = self.graphicsView.mapToScene(pos)
        items = self.scene.items()
        print(items)
        for item in items:
            if isinstance(item, QGraphicsEllipseItem):
                print(item.scenePos().x())
                if abs(item.scenepos().x() - scene_pos.x()) <= 7 and abs(item.scenepos().y() - scene_pos.y()) <= 7:
                    print('here3')
                    self.scene.removeItem(item)
                    point_list.remove(Point(item.x(), item.y()))
                else:
                    print(item.x(), item.y())

    def on_graphicsview_click(self, event):
        if event.buttons() == Qt.LeftButton:
            self.add_point_by_click(event)
        elif event.buttons() == Qt.RightButton:
            self.del_point_by_click(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
