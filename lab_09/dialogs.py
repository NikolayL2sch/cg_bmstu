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
    msg.setText("Лабораторная работа №9.\nРазработал Миленко Николай ИУ7-45Б")
    msg.exec_()


def show_task():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Условие задачи")
    msg.setText(
        'Программа позволяет осуществлять ввод отсекателя, отсекаемого многоугольника и выполнять'
        ' отсечение многоугольника по границам отсекателя.\n')
    msg.exec_()


def show_instruction():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Возможности программы")
    msg.setText("Смена цвета регулярного отсекателя/отрезков.\nВыбор одного из предложенных цветов меняет цвет "
                "для всех БУДУЩИХ графических объектов этого типа."
                "\n\nВвод отсекателя-многоугольника осуществляется по точкам с помощью нажатия ЛКМ. "
                "Предварительно для ввода регулярного отсекателя необходимо нажать на "
                "кнопку с надписью 'Добавить выпуклый отсекатель'. \nПосле ввода отсекателя необходимо нажать на "
                "кнопку с надписью 'Закончить добавление отсекателя'."
                "\n\nВвод отсекаемого многоугольника осуществляется путем добавления вершин по клику ЛКМ в "
                "выбранном пользователем месте.\n\n"
                "Добавление ребер отсекаемого многоугольника, принадлежащих ребрам отсекателя осуществляется путем "
                "нажатия на одно из ребер в списке ребер (слева снизу). Далее следует кликнуть на сцене в точке, "
                "примерно принадлежащей желаемому ребру.")
    msg.exec_()
