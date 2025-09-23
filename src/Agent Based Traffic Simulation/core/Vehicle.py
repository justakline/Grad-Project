import numpy as np


class Vehicle:

    def __init__(position:np.array, length:float, width: float ):
        self.position = position
        self.length = length
        self.width = width
        self.velocity = np.array([0,0])
        self.acceleration = np.array([0,0])

