import numpy as np


class Vehicle:
    # Distance will use floats because mm/ms does not have enough precision... 2mi/hour = 1mm/s
    def __init__(self, position: np.array, length: float, width: float):
        self.position: np.array = position
        self.length: float = length
        self.width: float = width
        self.velocity: np.array = np.array([0, 0], dtype=float)
        self.acceleration: np.array = np.array([0, 0], dtype=float)

    def changeAcceleration(self, change_amount: np.array):
        self.acceleration = np.add(self.acceleration, change_amount)

    def changeVelocity(self, change_amount: np.array):
        self.velocity = np.add(self.velocity, change_amount)
        self.velocity = self.velocity if self.get_scaler(self.velocity) >= 0 else np.array([0.0, 0.0])

    def changePosition(self, change_amount: np.array):
        self.position = np.add(self.position, change_amount)

    def get_scaler(self, vector: np.array):
        return np.linalg.norm(vector)

    def setAcceleration(self, new_a):
        # absolute set, not incremental
        self.acceleration = np.array(new_a, dtype=float)
