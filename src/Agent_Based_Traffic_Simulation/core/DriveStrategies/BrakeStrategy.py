# BrakeStrategy.py
import numpy as np
from .DriveStrategy import DriveStrategy
from .AccelerateStrategy import AccelerateStrategy

class BrakeStrategy(DriveStrategy):
    name = "brake"

    def step(self, traffic_agent):
        vehicle = traffic_agent.vehicle
        v = vehicle.velocity
        speed = float(np.linalg.norm(v))

        # No leader → switch back to accelerate
        if traffic_agent.gap_to_lead is None:
            traffic_agent.assign_strategy(AccelerateStrategy)
            return








        gap = float(traffic_agent.gap_to_lead)
        safe_min = float(traffic_agent.safe_follow_distance_minimum)
        th_ms = float(traffic_agent.time_headway) * 1000.0
        
        if th_ms <= 0.0:
            th_ms = 1e-6  # avoid div by zero

        # Emergency brake if inside minimum distance: stop within remaining gap
        if gap < safe_min:
            if speed > 0.0:
                a_mag = speed**2 / max(2.0 * max(gap, 1e-6), 1e-6)  # mm/ms^2
                vehicle.setAcceleration(-(a_mag * (v / speed)))
            else:
                vehicle.setAcceleration(np.array([0.0, 0.0], dtype=float))
            return

        # Gentle brake toward time-headway target, with smooth recovery
        desired_speed = max(0.0, (gap - safe_min) / th_ms)  # mm/ms

        lane_dir = traffic_agent.lane_direction()
        n = np.linalg.norm(lane_dir)
        if n == 0.0:
            lane_dir = np.array([1.0, 0.0], dtype=float)
        else:
            lane_dir = lane_dir / n

        desired_v = lane_dir * desired_speed
        dt = 1.0  # your agent uses dt = 1.0 ms in step()
        a = (desired_v - v) / dt  # mm/ms^2

        vehicle.setAcceleration(a)
