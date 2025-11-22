import numpy as np
from .AbstractDriveStrategy import AbstractDriveStrategy
from ..Utils import to_unit, change_magnitude,  EPS

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..TrafficAgent import TrafficAgent

# The idea of cruising is trying to get back to your "desired cruising speed and stay there"
class CruiseStrategy(AbstractDriveStrategy):
    name:str = 'cruise'


    # def step(self, traffic_agent):
    #     traffic_agent.vehicle.setAcceleration(np.array([0,0]))

    def step(self, traffic_agent: "TrafficAgent"):
        a_cmd = self.calculate_accel(traffic_agent)
        direction = to_unit(traffic_agent.vehicle.velocity) if np.linalg.norm(traffic_agent.vehicle.velocity) > EPS else np.array([0., 1.])
        new_acceleration = direction * a_cmd
        traffic_agent.vehicle.setAcceleration(new_acceleration)
  

    def calculate_accel(self, traffic_agent) -> float:
        cruise_g = traffic_agent.cruise_gain
        desired_v = traffic_agent.desired_speed
        current_v = np.linalg.norm(traffic_agent.vehicle.velocity)

        # The acceleration/deceleration needed to get to my desired velocity
        acceleration_raw = cruise_g * (desired_v - current_v)

        max_accel = traffic_agent.max_acceleration

        # This logic is flawed, it should not be max()
        # It should be clipped between a min (like comfortable braking) and max accel.
        # For now, we will just clip it at max acceleration.
        acceleration_clipped = min(acceleration_raw, max_accel)

        # No backwards movement when at a standstill
        if acceleration_clipped <= 0 and current_v < EPS:
            acceleration_clipped = 0
        
        return acceleration_clipped
