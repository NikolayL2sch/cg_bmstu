from math import sin, cos
from typing import Tuple, List, Callable


def equation_1(x: float) -> float:
    return sin(x) * cos(x)


def equation_2(x: float, z: float) -> float:
    return 6 * x + 2 * z - 12


def equation_3(x: float, y: float) -> float:
    return x ** 2 + y ** 2


def equation_4(x: float, z: float) -> float:
    return sin(x * z)


def equation_5(x: float, y: float) -> float:
    return (x * y) ** 2


def get_equations() -> Tuple[List[Callable[..., float]], List[str]]:
    equations = []
    equations.extend([equation_1, equation_2, equation_3, equation_4, equation_5])
    equations_str = ['sin(x) * cos(x)', '6x + 2z - 12', 'x^2 + y^2', 'sin(x * z)', '(xy) ^ 2']
    return equations, equations_str
