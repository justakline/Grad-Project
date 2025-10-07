import numpy as np


class Vehicle:

    position: np.array
    velocity: np.array
    acceleration: np.array
    length:float
    width:float

    def __init__(self, position:np.array, length:float, width: float ):
        self.position = position
        self.length = length
        self.width = width
        self.velocity = np.array([0,0])
        self.acceleration = np.array([0,0])

