# BrakeStrategy.py
import numpy as np

from .AbstractDriveStrategy import AbstractDriveStrategy

class BrakeStrategy(AbstractDriveStrategy):
    name = "brake"

    def step(self, traffic_agent):
        import numpy

        # Speeds (mm/ms)
        vehicle_speed = float(numpy.linalg.norm(traffic_agent.vehicle.velocity))
        leader_speed = float(numpy.linalg.norm(traffic_agent.lead.vehicle.velocity))
        closing_speed = vehicle_speed - leader_speed  # > 0 means we are faster



        # Distances and timing (mm, ms)
        gap_distance = float(traffic_agent.gap_to_lead)
        minimum_follow_distance = float(traffic_agent.smallest_follow_distance)
        hard_brake_distance_start = float(traffic_agent.hard_brake_distance_start)
        dt = float(traffic_agent.model.dt)

        # We are going slower than the car in front of us
        if(closing_speed <= 0):
            return
        
        if (gap_distance < minimum_follow_distance):
            traffic_agent.vehicle.velocity = np.array([0,0])

        

        # Apply along current motion
        # traffic_agent.vehicle.setAcceleration(new_acceleration)











        ############################################################################################





        # vehicle = traffic_agent.vehicle
        # v = vehicle.velocity
        # speed = float(np.linalg.norm(v))

        # # There is no one in front if me, so accelerate
        # if traffic_agent.gap_to_lead is None:
        #     traffic_agent.assign_strategy(AccelerateStrategy)
        #     return
        
        # # There is someone in front of me
        # gap = float(traffic_agent.gap_to_lead)

        # safe_min = float(traffic_agent.safe_follow_distance_minimum)


        # # Emergency brake if inside minimum distance: stop within remaining gap
        # if gap < traffic_agent.hard_brake_distance_start:
        #     if speed > 0.0:
        #         other_velocity = traffic_agent.lead.vehicle.velocity
        #         other_speed = float(np.linalg.norm(other_velocity))
        #         speed_variance = speed - other_speed


        #         a_mag = speed**2 / max(2.0 * max(gap, 1e-6), 1e-6)  # mm/ms^2
        #         vehicle.setAcceleration(-(a_mag * (v / speed)))
        #     else:
        #         vehicle.setAcceleration(np.array([0.0, 0.0], dtype=float))
        #     return

        # # Gentle brake toward time-headway target, with smooth recovery
        # desired_speed = max(0.0, (gap - safe_min) / th_ms)  # mm/ms

        # lane_dir = traffic_agent.lane_direction()
        # n = np.linalg.norm(lane_dir)
        # if n == 0.0:
        #     lane_dir = np.array([1.0, 0.0], dtype=float)
        # else:
        #     lane_dir = lane_dir / n

        # desired_v = lane_dir * desired_speed
        # dt = 1.0  # your agent uses dt = 1.0 ms in step()
        # a = (desired_v - v) / dt  # mm/ms^2

        # vehicle.setAcceleration(a)

