from typing import List
from dialogs import show_err_win


def check_radius(radius: float) -> bool:
    if radius > 0:
        return True
    show_err_win("Значение радиуса должно быть больше 0!")
    return False


def params_to_float(*args: List[str]) -> List[float]:
    float_args = []
    if '' in args:
        show_err_win("Не введены все параметры для совершения этого действия")
        return float_args
    try:
        float_args = [float(arg) for arg in args]
    except ValueError:
        show_err_win("Введены некорректные символы")
    return float_args


def check_scale_koeff(scale_koeff: float) -> bool:
    if abs(scale_koeff) > 1e-13:
        return True
    show_err_win("Значение коэффициента не должно быть равно 0!")
    return False
