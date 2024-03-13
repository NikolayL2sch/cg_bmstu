from typing import List
from dialogs import show_err_win


def check_radius(radius: float) -> bool:
    if radius > 0:
        return True
    return False


def params_to_float(*args: List[str]) -> List[float]:
    float_args = []
    if '' in args:
        show_err_win("Не введены все параметры для совершения этого действия")
    try:
        float_args = [float(arg) for arg in args]
    except ValueError:
        show_err_win("Введены некорректные символы")
    return float_args
