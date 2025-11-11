import numpy as np
from .AbstractVehicle import AbstractVehicle

# Ford f-350 LARIAT is chosen as the standard truck
# Using it's dimensions

class Truck(AbstractVehicle):
    def __init__(self, position: np.ndarray):
        super().__init__(position, 5887, 2690)
        self.velocity = np.array([0.0, 0.0], dtype=float)  # mm/ms
        self.acceleration = np.array([0.0, 0.0], dtype=float)  # mm/ms^2
