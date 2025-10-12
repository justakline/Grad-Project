import numpy as np
from .DriveStrategy import DriveStrategy

class AccelerateStrategy(DriveStrategy):
    name = 'accelerate'

    def step(self, traffic_agent):
        dt = 1.0  # ms, matches your agent step
        v = traffic_agent.vehicle.velocity
        speed = float(np.linalg.norm(v))
        lane_dir = traffic_agent.lane_direction()

        # accelerate toward max_speed along the lane
        target_speed = min(traffic_agent.max_speed, speed + traffic_agent.a_max * dt)  # all in mm/ms
        desired_v = lane_dir * target_speed
        a = (desired_v - v) / dt  # mm/ms^2

        traffic_agent.vehicle.setAcceleration(a)
