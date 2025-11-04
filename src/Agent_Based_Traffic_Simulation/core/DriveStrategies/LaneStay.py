
import numpy as np
from ..Highway import Highway
from ..TrafficAgent import TrafficAgent
from ..DriveStrategies.AbstractLaneChange import AbstractLaneChange
from ..DriveStrategies.LaneChangeStrategy import LaneChangeStrategy

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..TrafficAgent import TrafficAgent

class LaneStay(AbstractLaneChange):
    """
    Default lateral strategy. Agent stays in its lane while checking
    for opportunities to change lanes based on the MOBIL model.
    """
    
    def __init__(self): # Default 2 second lane change

        self.lateral_velocity = 0.0

        
    def step(self, traffic_agent: "TrafficAgent"):
        # Only check for lane changes on the agent's decision tick
        if traffic_agent.internal_timer < traffic_agent.decision_time:
            return

        # COMMITMENT: If a lane change is already in progress, do not evaluate a new one.
        # This prevents "wiggling" back and forth.
        if isinstance(traffic_agent.lane_change_strategy, LaneChangeStrategy):
            return

        # --- 1. Evaluate Incentive to Change Lanes ---
        current_accel = traffic_agent.current_drive_strategy.calculate_accel(traffic_agent)
        
        best_gain = -np.inf
        best_target_lane = -1
        
        gains = {}

        # Check left and right lanes
        for lane_offset in [-1, 1]:
            target_lane_idx = traffic_agent.current_lane + lane_offset
            if not (0 <= target_lane_idx < len(traffic_agent.model.highway.lanes)):
                continue

            # --- 2. Find new neighbors in the target lane ---
            new_leader, new_follower = traffic_agent.find_neighbors_in_lane(target_lane_idx)
            
            # --- 3. Check Safety Criterion ---
            # Is it safe for the new follower?
            if new_follower is not None:
                # Calculate the acceleration the new follower would need if we changed lanes
                accel_new_follower = self.get_follower_accel(traffic_agent, new_follower)
                
                # SAFETY CRITERION: If the new follower would have to brake harder than their
                # comfortable braking limit, the lane change is unsafe.
                if accel_new_follower is not None and (accel_new_follower < -new_follower.braking_comfortable or not self.is_trajectory_safe(traffic_agent, new_follower)):
                    continue # Unsafe, check next lane

            # --- 4. Check Incentive Criterion ---
            # What is my acceleration if I change?
            accel_after_change = self.get_potential_accel(traffic_agent, new_leader)

            # Incentive formula from MOBIL model
            # a_c' - a_c > p * (a_n - a_n') + a_thr
            # My gain > politeness * follower's loss + threshold
            my_gain = accel_after_change - current_accel
            
            follower_loss = 0.0
            if new_follower is not None:
                # Follower's current acceleration in their own lane
                accel_new_follower_current = new_follower.current_drive_strategy.calculate_accel(new_follower)
                follower_loss = accel_new_follower_current - accel_new_follower

            incentive = my_gain - (traffic_agent.politeness_factor * follower_loss)
            


            if incentive > traffic_agent.lane_change_threshold and my_gain > best_gain:
                best_gain = my_gain
                best_target_lane = target_lane_idx
                
            # Left lane gets incentive due to it being a passing lane
            my_gain  = my_gain * 1.2 if lane_offset == -1 else my_gain
            gains[target_lane_idx] = my_gain

        # --- 5. Execute Lane Change if beneficial ---
        if best_target_lane != -1:
            best_target_lane = max(gains, key=gains.get)
            print(best_target_lane)
            target_lane_x = traffic_agent.model.highway.lanes[best_target_lane].start_position[0]
            traffic_agent.lane_intent = best_target_lane
            traffic_agent.initial_lane_x = traffic_agent.vehicle.position[0]
            traffic_agent.lane_change_strategy = LaneChangeStrategy(target_lane_x)

    def get_follower_accel(self, ego_agent: "TrafficAgent", follower: "TrafficAgent") -> float:
        """
        Calculates the acceleration 'follower' would have if 'ego_agent' becomes its new leader.
        """
        # Temporarily set the ego agent as the follower's leader to calculate acceleration
        original_leader = follower.lead
        original_gap = follower.gap_to_lead
        
        follower.lead = ego_agent
        # Use longitudinal gap, not euclidean distance, for safety calculations
        follower.gap_to_lead = (ego_agent.pos[1] - ego_agent.vehicle.length / 2) - (follower.pos[1] + follower.vehicle.length / 2)
        
        # Use the follower's current strategy to calculate potential acceleration
        potential_accel = follower.current_drive_strategy.calculate_accel(follower)
        
        # Restore original leader
        follower.lead = original_leader
        follower.gap_to_lead = original_gap
        
        return potential_accel

    def get_potential_accel(self, ego_agent: "TrafficAgent", potential_leader: "TrafficAgent") -> float:
        """
        Calculates the acceleration 'ego_agent' would have with a new potential leader.
        """
        original_leader = ego_agent.lead
        original_gap = ego_agent.gap_to_lead

        ego_agent.lead = potential_leader
        if potential_leader:
            # Use longitudinal gap, not euclidean distance
            ego_agent.gap_to_lead = (potential_leader.pos[1] - potential_leader.vehicle.length / 2) - (ego_agent.pos[1] + ego_agent.vehicle.length / 2)
        else:
            ego_agent.gap_to_lead = None

        potential_accel = ego_agent.current_drive_strategy.calculate_accel(ego_agent)

        # Restore original state
        ego_agent.lead = original_leader
        ego_agent.gap_to_lead = original_gap

        return potential_accel

    def is_trajectory_safe(self, ego_agent: "TrafficAgent", follower: "TrafficAgent") -> bool:
        """
        Predicts if the ego_agent's lane change trajectory will collide with the follower's.
        Returns True if safe, False if a collision is predicted.
        """
        if follower is None:
            return True

        # --- Simulation Parameters ---
        duration = 2000.0  # Must match the duration in LaneChangeStrategy
        dt = ego_agent.model.dt
        time_steps = int(duration / dt)
        target_lane_x = ego_agent.model.highway.lanes[ego_agent.lane_intent].start_position[0]

        # --- Get Predicted Accelerations ---
        # Find the new leader in the target lane to correctly predict ego's acceleration
        new_leader, _ = ego_agent.find_neighbors_in_lane(ego_agent.lane_intent)
        ego_accel = self.get_potential_accel(ego_agent, new_leader)
        follower_accel = self.get_follower_accel(ego_agent, follower) # Follower's accel if we cut in

        # --- Initial States for Simulation ---
        ego_pos = ego_agent.vehicle.position.copy()
        ego_vel = ego_agent.vehicle.velocity.copy()
        follower_pos = follower.vehicle.position.copy()
        follower_vel = follower.vehicle.velocity.copy()

        for i in range(time_steps):
            # --- Predict Ego Agent's Movement ---
            # Calculate lateral velocity for this step
            remaining_time = duration - (i * dt)
            lateral_vel_x = (target_lane_x - ego_pos[0]) / remaining_time if remaining_time > 0 else 0
            ego_vel[0] = lateral_vel_x
            # Update longitudinal velocity and position
            ego_vel[1] += ego_accel * dt
            ego_pos += ego_vel * dt
            
            # --- Predict Follower's Movement ---
            # Follower only moves longitudinally
            follower_vel[1] += follower_accel * dt
            follower_pos[1] += follower_vel[1] * dt

            # --- Check for Bounding Box Overlap at this time step ---
            dx = abs(ego_pos[0] - follower_pos[0])
            dy = abs(ego_pos[1] - follower_pos[1])
            if dx < (ego_agent.vehicle.width / 2 + follower.vehicle.width / 2) and \
               dy < (ego_agent.vehicle.length / 2 + follower.vehicle.length / 2):
                return False # Collision predicted

        return True # Trajectory is safe