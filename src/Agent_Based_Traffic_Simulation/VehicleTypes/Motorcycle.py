import numpy as np
from .AbstractVehicle import AbstractVehicle


# One of the mos tpopular motorcyles in America is the 2025 Harley-Davidson Street Glide
# Using it's dimensions

class Motocycle(AbstractVehicle):
    def __init__(self, position: np.ndarray):
        super.__init__(position, 2410, 975)
        self.velocity = np.array([0.0, 0.0], dtype=float)  # mm/ms
        self.acceleration = np.array([0.0, 0.0], dtype=float)  # mm/ms^2
