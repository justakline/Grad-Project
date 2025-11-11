import numpy as np
from .AbstractVehicle import AbstractVehicle
# Toyota Rav4 is the most popular SUV in America 
# Using the Toyota Rav4's dimensions
class SUV(AbstractVehicle):
    def __init__(self, position: np.ndarray):
        super().__init__(position, 4595, 1880)
        self.velocity = np.array([0.0, 0.0], dtype=float)  # mm/ms
        self.acceleration = np.array([0.0, 0.0], dtype=float)  # mm/ms^2
