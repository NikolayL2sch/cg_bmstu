from PyQt5.QtWidgets import QMessageBox


def show_war_win(war: str) -> None:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(war)
    msg.setWindowTitle("Предупреждение!")
    msg.exec_()


def show_err_win(err: str) -> None:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(err)
    msg.setWindowTitle("Ошибка!")
    msg.exec_()


def show_author():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Об авторе")
    msg.setText("Лабораторная работа №2.\nРазработал Миленко Николай ИУ7-45Б")
    msg.exec_()


def show_task():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Условие задачи")
    msg.setText("Построить фигуру, образованную пересечением окружности (x - a) ^ 2 + (y - b) ^ 2 = r ^ "
                "2 с гиперболой y = c / x.\n\nПостроить заштрихованную фигуру, затем ее переместить,"
                "промасштабировать, повернуть\n\n"
                "Вывести изображение в графическом режиме.\n\n19 Вариант.")
    msg.exec_()


def show_instruction():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Возможности программы")
    msg.setText("Перенос.\nПеренос фигуры осуществляется в соответствии с заданными dx, dy: переносом по OX и OY "
                "соответственно.\n\nМасштабирование осуществляется в соответствии с заданными kx, ky: коэффициентами "
                "масштабирования, а так же cx, cy - координатами центра масштабирования"
                "\nПо клику ПРАВОЙ кнопкой мыши на графике достаточно близко к удаляемой "
                "точке.\n\nМасштабирование окна при изменении его размеров происходит "
                "автоматически.\nРеализовано масштабирование графика с помощью колеса мыши. Шаг сетки меняется "
                "автоматически и указан в левом нижнем углу экрана.")
    msg.exec_()
