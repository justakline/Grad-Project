import numpy as np
from .AbstractDriveStrategy import AbstractDriveStrategy
from ..Utils import to_unit, change_magnitude,  e


# The idea of cruising is trying to get back to your "desired cruising speed and stay there"
class CruiseStrategy(AbstractDriveStrategy):
    name = 'cruise'
    def step(self, traffic_agent):

        dt = traffic_agent.model.dt
        cruise_g = traffic_agent.cruise_gain
        desired_v = traffic_agent.desired_speed
        current_v = np.linalg.norm(traffic_agent.vehicle.velocity)

        
        acceleration_raw = cruise_g *(desired_v - current_v )

        braking_comfortable = traffic_agent.braking_comfortable
        max_accel = traffic_agent.max_acceleration

        acceleration_clipped = np.clip(acceleration_raw, -1*braking_comfortable, max_accel)

        # No backwards movement when at a standstill
        if(acceleration_clipped <= 0 or current_v < e ):
            acceleration_clipped = 0

        direction = traffic_agent.current_lane_vector()
        new_acceleration = change_magnitude(direction, acceleration_clipped)
        traffic_agent.vehicle.setAcceleration(new_acceleration)
    

        # traffic_agent.vehicle.setAcceleration(np.array([0.0, 0.0]))
