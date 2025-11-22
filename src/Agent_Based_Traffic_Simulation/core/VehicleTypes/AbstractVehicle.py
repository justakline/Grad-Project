import numpy as np


class AbstractVehicle:
    def __init__(self, position: np.ndarray, length: float, width: float):
        self.position: np.ndarray = position
        self.length:float = length
        self.width:float = width
        self.velocity:np.array = np.array([0.0, 0.0], dtype=float)  # mm/ms
        self.acceleration:np.array = np.array([0.0, 0.0], dtype=float)  # mm/ms^2



    def setAcceleration(self, new_a: np.array):
        # absolute set, not incremental
        self.acceleration = np.array(new_a, dtype=float)
