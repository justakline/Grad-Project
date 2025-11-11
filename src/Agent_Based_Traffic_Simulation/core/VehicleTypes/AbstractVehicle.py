import numpy as np


class AbstractVehicle:
    def __init__(self, position: np.ndarray, length: float, width: float):
        self.position = position
        self.length = length
        self.width = width
        self.velocity = np.array([0.0, 0.0], dtype=float)  # mm/ms
        self.acceleration = np.array([0.0, 0.0], dtype=float)  # mm/ms^2
        
    def changeAcceleration(self, change_amount: np.array):
        self.acceleration = np.add(self.acceleration, change_amount)

    def changeVelocity(self, change_amount: np.array):
        self.velocity = np.add(self.velocity, change_amount)
        self.velocity = self.velocity if self.get_scaler(self.velocity) >= 0 else np.array([0.0, 0.0])

    def changePosition(self, change_amount: np.array):
        self.position = np.add(self.position, change_amount)

    def get_scaler(self, vector: np.array):
        return np.linalg.norm(vector)
    def setAcceleration(self, new_a: np.array):
        # absolute set, not incremental
        self.acceleration = np.array(new_a, dtype=float)
