import numpy as np
from .AbstractDriveStrategy import AbstractDriveStrategy

class AccelerateStrategy(AbstractDriveStrategy):
    name = 'accelerate'

    def step(self, traffic_agent):
        dt = traffic_agent.model.dt 
        v = traffic_agent.vehicle.velocity
        speed = float(np.linalg.norm(v))
        lane_dir = traffic_agent.current_lane_vector()

        # accelerate toward max_speed along the lane
        target_speed = min(traffic_agent.max_speed, speed + traffic_agent.acceleration_increase * dt)  
        desired_v = lane_dir * target_speed

        acceleration_increase = (desired_v - v) / dt  # mm/ms^2
        traffic_agent.vehicle.setAcceleration(acceleration_increase)
