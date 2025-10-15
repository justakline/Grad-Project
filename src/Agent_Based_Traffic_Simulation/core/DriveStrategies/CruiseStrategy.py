import numpy as np
from .AbstractDriveStrategy import AbstractDriveStrategy

class CruiseStrategy(AbstractDriveStrategy):
    name = 'cruise'
    def step(self, traffic_agent):
        # hold speed; zero acceleration
        traffic_agent.vehicle.setAcceleration(np.array([0.0, 0.0]))
