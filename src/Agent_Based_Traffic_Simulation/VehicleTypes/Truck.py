import numpy as np
from .AbstractVehicle import AbstractVehicle

# Ford f-150 XL is the most popular truck in america
# Using it's dimensions

class Truck:
    def __init__(self, position: np.ndarray):
        super.__init__(position, 5311, 2029)
        self.velocity = np.array([0.0, 0.0], dtype=float)  # mm/ms
        self.acceleration = np.array([0.0, 0.0], dtype=float)  # mm/ms^2
