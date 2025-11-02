import numpy as np
from .AbstractDriveStrategy import AbstractDriveStrategy
from ..Utils import change_magnitude, EPS, to_unit

class BrakeStrategy(AbstractDriveStrategy):
    name = "brake"
    
   
class BrakeStrategy(AbstractDriveStrategy):
    name = "brake"

    def step(self, traffic_agent):
        """
        Implements braking behavior based on the Intelligent Driver Model (IDM).
        The acceleration is calculated to safely reduce speed and avoid collision.
        """
        lead = traffic_agent.lead
        if lead is None:
            # Should not happen if logic in TrafficAgent is correct, but as a fallback, stop braking.
            from .CruiseStrategy import CruiseStrategy
            traffic_agent.assign_strategy(CruiseStrategy)
            traffic_agent.current_drive_strategy.step(traffic_agent)
            return

        v_now = float(np.linalg.norm(traffic_agent.vehicle.velocity))
        v_lead = float(np.linalg.norm(lead.vehicle.velocity))
        delta_v = v_now - v_lead
        gap = traffic_agent.gap_to_lead

        # IDM parameters from agent
        a = traffic_agent.max_acceleration
        b = traffic_agent.braking_comfortable
        s0 = traffic_agent.smallest_follow_distance
        T = traffic_agent.desired_time_headway / 1000.0 # convert ms to s for formula, but speeds are mm/ms
        v0 = traffic_agent.desired_speed
        delta = 4.0 # Acceleration exponent, common default for IDM

        # IDM's desired gap calculation
        s_star = s0 + max(0.0, (v_now * T) + (v_now * delta_v) / (2 * np.sqrt(a * b)))

        # Full IDM acceleration formula
        # Includes free-road acceleration and interaction term for braking.
        free_road_term = a * (1 - (v_now / v0) ** delta if v0 > 0 else 1)
        interaction_term = -a * (s_star / max(gap, s0))**2
        a_cmd = free_road_term + interaction_term

        # Clip at max braking force and ensure we are decelerating
        a_cmd = float(np.clip(a_cmd, -traffic_agent.b_max, 0.0))
        # a_cmd = float(min(a_cmd, 0.0))
        # If we are inside the minimum safe distance, override and brake as hard as possible.
        if gap < s0:
            a_cmd = -traffic_agent.b_max
        else:
            # Otherwise, use the calculated acceleration, ensuring it's only for braking.
            a_cmd = float(np.clip(a_cmd, -traffic_agent.b_max, 0.0))

        # No backward roll when stopped
        if v_now < EPS and a_cmd < 0.0:
            a_cmd = 0.0



        # Apply along lane direction as a deceleration vector
        direction = to_unit(traffic_agent.vehicle.velocity) if np.linalg.norm(traffic_agent.vehicle.velocity) > EPS else np.array([0., 1.])
        new_accel = direction * a_cmd
        traffic_agent.vehicle.setAcceleration(new_accel)
