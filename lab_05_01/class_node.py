from dataclasses import dataclass


@dataclass(order=True)
class Node:
    x: float
    dx: float
    dy: int
