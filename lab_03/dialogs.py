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
    msg.setText("Лабораторная работа №3.\nРазработал Миленко Николай ИУ7-45Б")
    msg.exec_()


def show_task():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Условие задачи")
    msg.setText("Реализовать возможность построения отрезков методами: Брезенхема, Ву, ЦДА, построение пучка отрезков "
                "и сравнение времени и ступенчатости.")
    msg.exec_()


def show_instruction():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Возможности программы")
    msg.setText("Смена цвета отрезка.\nВыбор одного из предложенных цветов меняет цвет всех отрезков на графике.")
    msg.exec_()
