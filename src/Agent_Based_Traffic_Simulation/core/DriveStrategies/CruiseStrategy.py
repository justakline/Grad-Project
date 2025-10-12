# CruiseStrategy.py
import numpy as np
from .DriveStrategy import DriveStrategy

class CruiseStrategy(DriveStrategy):
    name = "cruise"

    def step(self, traffic_agent):
        vehicle = traffic_agent.vehicle
        v = vehicle.velocity  # mm/ms
        lane_dir = traffic_agent.lane_direction()
        n = np.linalg.norm(lane_dir)
        lane_dir = lane_dir / n if n > 0 else np.array([1.0, 0.0], dtype=float)

        target_speed = float(traffic_agent.max_speed)          # mm/ms
        desired_v = lane_dir * target_speed                    # vector target

        # Smooth tracking so it accelerates back up after braking
        tau_ms = 500.0  # response time in ms, adjust 300-800 as you like
        a = (desired_v - v) / tau_ms                           # mm/ms^2

        # tiny nudge if completely stopped to overcome numeric deadzone
        if np.linalg.norm(v) < 1e-6:
            a += 0.001 * lane_dir

        vehicle.setAcceleration(a)
