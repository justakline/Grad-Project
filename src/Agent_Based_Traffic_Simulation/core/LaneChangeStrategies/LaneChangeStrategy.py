import numpy as np
from .AbstractLaneChange import AbstractLaneChange
from ..Utils import to_unit

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..TrafficAgent import TrafficAgent

class LaneChangeStrategy(AbstractLaneChange):
    """
    Executes the physical lane change over a set duration.
    """
    def __init__(self, target_lane_x: float, duration: float = 2000.0, is_emergency_return: bool = False): # Default 2 second lane change
        self.target_x = target_lane_x
        self.duration = duration
        self.timer = 0.0
        self.lateral_velocity = 0.0
        self.is_emergency_return = is_emergency_return

    def step(self, traffic_agent: "TrafficAgent"):
        dt = traffic_agent.model.dt
        self.timer += dt

        if self.timer >= self.duration:
            # Finalize lane change
            traffic_agent.vehicle.position[0] = self.target_x
            traffic_agent.current_lane = traffic_agent.lane_intent
            
            from .LaneStayStrategy import LaneStayStrategy
            self.lateral_velocity = 0.0
            traffic_agent.lane_change_strategy = LaneStayStrategy()
            return

        longitudinal_velocity = traffic_agent.vehicle.velocity[1]
        min_speed_for_lane_change = 5.0 # mm/ms (18 km/h or 11 mph)

        # If agent is moving too slowly, pause the lane change to prevent spinning.
        if abs(longitudinal_velocity) < min_speed_for_lane_change:
            self.lateral_velocity = 0.0
            # We also pause the timer so the lane change can resume when speed picks up.
            self.timer -= dt
            return

        # Calculate the required lateral velocity to reach the target_x in the remaining time
        remaining_time = self.duration - self.timer
        required_lateral_velocity = 0.0
        if remaining_time > 0:
            # This is velocity per millisecond, which is what we need
            required_lateral_velocity = (self.target_x - traffic_agent.vehicle.position[0]) / remaining_time

        # Limit the lateral velocity to achieve a max angle of 30 degrees.
        # tan(30 deg) = lateral_v / longitudinal_v  =>  lateral_v = longitudinal_v * tan(45)
        max_lateral_velocity = abs(longitudinal_velocity) * np.tan(np.deg2rad(45))
        potential_lateral_v = np.clip(required_lateral_velocity, -max_lateral_velocity, max_lateral_velocity)

        # --- CONTINUOUS DYNAMIC SAFETY CHECK ---
        # Before committing to the lateral movement, check if it will cause a collision.
        # An emergency return maneuver cannot be interrupted.
        if not self.is_emergency_return and traffic_agent.is_colliding_at_next_step(potential_lateral_v, self.target_x):
            # EMERGENCY ABORT: A collision is imminent. Change back to the original lane.
            # The new target is the initial X position, and this is now an emergency return.
            traffic_agent.lane_change_strategy = LaneChangeStrategy(traffic_agent.initial_lane_x, self.duration, is_emergency_return=True)
            traffic_agent.lane_intent = traffic_agent.current_lane
            return
        
        self.lateral_velocity = potential_lateral_v