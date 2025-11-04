import random
import numpy as np
from ..Utils import to_unit, change_magnitude, EPS
from .AbstractDriveStrategy import AbstractDriveStrategy


class AccelerateStrategy(AbstractDriveStrategy):
    name = "accelerate"

    def step(self, traffic_agent):
        a_cmd = self.calculate_accel(traffic_agent)
        #Variabilitiy

        direction = to_unit(traffic_agent.vehicle.velocity) if np.linalg.norm(traffic_agent.vehicle.velocity) > EPS else np.array([0., 1.])
        new_acceleration = direction * a_cmd
        traffic_agent.vehicle.setAcceleration(new_acceleration)
        


    def calculate_accel(self, traffic_agent) -> float:
        """Calculates the desired acceleration without applying it."""
        current_speed = float(np.linalg.norm(traffic_agent.vehicle.velocity))
        desired_speed = float(traffic_agent.desired_speed)

        # reuse the same gain profile as cruise, but never decelerate
        cruise_gain = float(traffic_agent.cruise_gain)
        acceleration_raw = cruise_gain * (desired_speed - current_speed)


        max_accel = float(traffic_agent.max_acceleration)

        # final accel bounded to [0, max_accel]
        acceleration_clipped = np.clip(acceleration_raw, 0.0, max_accel)
        # No backwards movement when at a standstill
        if current_speed < EPS and acceleration_clipped < 0:
            acceleration_clipped = 0.0
        

        return float(acceleration_clipped)
