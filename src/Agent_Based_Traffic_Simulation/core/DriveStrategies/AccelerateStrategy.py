import numpy as np
from ..Utils import to_unit, change_magnitude, EPS
from .AbstractDriveStrategy import AbstractDriveStrategy


class AccelerateStrategy(AbstractDriveStrategy):
    name = "accelerate"

    def step(self, traffic_agent):
        dt = traffic_agent.model.dt
        direction = traffic_agent.vehicle.velocity
        current_speed = float(np.linalg.norm(traffic_agent.vehicle.velocity))
        desired_speed = float(traffic_agent.desired_speed)

        # reuse the same gain profile as cruise, but never decelerate
        cruise_gain = float(traffic_agent.cruise_gain)
        acceleration_raw = cruise_gain * (desired_speed - current_speed)
        acceleration_raw = max(0.0, acceleration_raw)  # only accelerate

        max_accel = float(traffic_agent.max_acceleration)

        # final accel bounded to [0, max_accel]
        acceleration_clipped = np.clip(acceleration_raw, 0.0, max_accel)

        # if nearly stopped, do not allow tiny negative due to numerics
        if acceleration_clipped <= 0.0 and current_speed < EPS:
            acceleration_clipped = 0.0

        new_acceleration = change_magnitude(direction, acceleration_clipped)
        traffic_agent.vehicle.setAcceleration(new_acceleration)
