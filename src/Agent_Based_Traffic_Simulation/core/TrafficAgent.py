import random
from typing import TYPE_CHECKING, Type

import numpy as np

from .Personalities import DefensivePersonality
from .Personalities.AbstractPersonality import AbstractPersonality
from .Utils import to_unit, EPS
from mesa import Agent

# from Agent_Based_Traffic_Simulation.core.DriveStrategies import AbstractDriveStrategy
from . import TrafficModel
from .VehicleTypes import AbstractVehicle, SUV, Truck,  Motorcycle

if TYPE_CHECKING:
    from .DriveStrategies.AbstractDriveStrategy import AbstractDriveStrategy


class TrafficAgent(Agent):
    model: TrafficModel

    def __init__(self, model: TrafficModel, goal: np.ndarray, lane_intent: int, spawn_time, vehicle: AbstractVehicle, 
                 personality: AbstractPersonality = DefensivePersonality(), velocity = 0):
        super().__init__(model)
        dt = model.dt

        self.vehicle: AbstractVehicle = vehicle
        self.goal: np.ndarray = goal
        self.lane_intent = lane_intent
        self.current_lane = lane_intent
        self.spawn_time = spawn_time

        self.is_removed = False

        # --- Personality ---
        self.personality = personality
        self.personality.vehicle = self.vehicle # Give personality access to vehicle properties

        self.max_speed = personality.max_speed
        self.desired_speed = personality.desired_speed
        self.sensing_distance = personality.sensing_distance
        self.max_acceleration = personality.max_acceleration
        self.cruise_gain = personality.cruise_gain
        self.braking_comfortable = personality.braking_comfortable
        self.b_max = personality.b_max
        self.desired_time_headway = personality.desired_time_headway
        self.smallest_follow_distance = self.vehicle.length * self.personality.smallest_follow_distance_factor
        self.desired_gap = self.vehicle.length * self.personality.desired_gap_factor
        self.politeness_factor = personality.politeness_factor
        self.lane_change_threshold = personality.lane_change_threshold
        self.decision_time = personality.decision_time
     

        # strategies
        from .DriveStrategies.CruiseStrategy import CruiseStrategy
        from .LaneChangeStrategies.LaneStayStrategy import LaneStayStrategy

        self.previous_drive_strategy = CruiseStrategy()
        self.current_drive_strategy = CruiseStrategy()
        self.lane_change_strategy = LaneStayStrategy()

        # tracking
        self.lead = None
        self.direction = None
        self.gap_to_lead = None  # center-to-center, longitudinal mm

        # decision cadence
        self.internal_timer = self.decision_time
        self.initial_lane_x = self.vehicle.position[0]

        # small initial push along lane
        if(velocity == 0 ):
            self.vehicle.velocity = self.current_lane_vector() * self.desired_speed/10
        else:
            self.vehicle.velocity = self.current_lane_vector() * velocity



    # ---------- tick ----------
    def step(self) -> None:
        from .DriveStrategies.CruiseStrategy import CruiseStrategy
        from .DriveStrategies.AccelerateStrategy import AccelerateStrategy
        from .DriveStrategies.BrakeStrategy import BrakeStrategy
        dt = self.model.dt  # ms

 
     
    
        self.sense()
        self.action()
      
        # Make sure the vehicle does not go backwards, some boundary physics night allow that to happen
        if (np.linalg.norm(self.vehicle.velocity < 0)):
            self.vehicle.velocity[1] = max(0, self.vehicle.velocity[1])
        self.vehicle.position += self.vehicle.velocity * dt

        # Check for out of bounds and remove 
        if (self.check_outside_of_bounds()):
            self.remove_self() # This will now mark the agent for removal
            return
                
        if type(self.current_drive_strategy) is not type(self.previous_drive_strategy):
            self.internal_timer = -1
            
        self.model.highway.move_agent(self, tuple(self.vehicle.position))
        self.internal_timer += dt

    def sense(self) -> None:
        self.previous_drive_strategy = self.current_drive_strategy
        self.lead, self.gap_to_lead = self.find_lead_and_gap(self.sensing_distance)

    def action(self) -> None:
        self.choose_drive_strategy()
        self.do_drive_strategy()
        self.choose_lane_change_strategy()
        self.do_lane_change_strategy()
        longitudinal_accel_magnitude = self.current_drive_strategy.calculate_accel(self)
        self.vehicle.velocity[1] += longitudinal_accel_magnitude * self.model.dt

    def do_drive_strategy(self):
        self.current_drive_strategy.step(self)
    
    def do_lane_change_strategy(self):
        # This will set a lateral_velocity on the lane_change_strategy if a change is active
        self.lane_change_strategy.step(self)

        # --- Physics Update ---
        # 1. Get longitudinal acceleration from the driving strategy
        # 2. Update longitudinal velocity (y-component)
        # 3. Get lateral velocity from the lane change strategy 
        
        self.vehicle.velocity[0] = self.lane_change_strategy.lateral_velocity
        
    def choose_drive_strategy(self):
        from .DriveStrategies.CruiseStrategy import CruiseStrategy
        from .DriveStrategies.AccelerateStrategy import AccelerateStrategy
        from .DriveStrategies.BrakeStrategy import BrakeStrategy
        self.previous_drive_strategy = self.current_drive_strategy
        self.lead, self.gap_to_lead = self.find_lead_and_gap(self.sensing_distance)
        
        # If we do not have a person in front of us or we are in the first x ms of spawning
        if self.lead is None or self.gap_to_lead is None or self.spawn_time + self.model.initial_accelerate_time > self.model.total_time:
            self.assign_strategy(CruiseStrategy) 
            return

        v_now = np.linalg.norm(self.vehicle.velocity)
        v_lead = np.linalg.norm(self.lead.vehicle.velocity)
        closing_speed = v_now - v_lead # Positive if closing, negative if pulling away

        safe_dist = self.get_safe_following_distance()
        is_uncomfortable = self.is_uncomfortable_closing_speed(closing_speed, v_now)
        

        if self.gap_to_lead < safe_dist or is_uncomfortable:
            self.assign_strategy(BrakeStrategy)
        elif self.gap_to_lead < self.desired_gap:
            self.assign_strategy(CruiseStrategy)
        else:
            # Gap is generous, so accelerate towards desired speed
            self.assign_strategy(AccelerateStrategy)
        pass

    def choose_lane_change_strategy(self):
        pass
    
    def is_in_same_lane(self, other_agent: "TrafficAgent") -> bool:
        """
        Checks if another agent is at least partially within the boundaries of this agent's current lane.
        This is more robust than just checking lane indices, as it accounts for agents
        that are in the middle of a lane change.
        """
        lane = self.model.highway.lanes[self.current_lane]
        lane_width = lane.lane_width
        lane_center_x = lane.start_position[0]

        # Only count as same lane if their center is inside this lane
        return abs(other_agent.vehicle.position[0] - lane_center_x) < lane_width * 0.80

        # return other_agent_max_x > lane_min_x and other_agent_min_x < lane_max_x

    def check_outside_of_bounds(self) -> bool:
      

        if (
            self.vehicle.position[0] >= self.model.highway.x_max
            or self.vehicle.position[0] <= self.model.highway.x_min
            or self.vehicle.position[1] >= self.model.highway.y_max
            or self.vehicle.position[1] <= self.model.highway.y_min
        ):
            return True
        return False

    def remove_self(self):
        # Mark it for removal because if we remove it now, then other's could still have references to it
        self.is_removed = True

    def get_safe_following_distance(self):
        """
        Calculates safe following distance using the Intelligent Driver Model (IDM) approach.
        s*(v, dv) = s0 + max(0, v*T + (v*dv) / (2*sqrt(a*b)))
        """
        if self.lead is None:
            return 0.0

        v = np.linalg.norm(self.vehicle.velocity)
        v_lead = np.linalg.norm(self.lead.vehicle.velocity)
        delta_v = v - v_lead

        s_star = self.smallest_follow_distance + max(0.0, (v * self.desired_time_headway / 1000.0) + (v * delta_v) / (2 * np.sqrt(self.max_acceleration * self.braking_comfortable)))
        return s_star

    def assign_strategy(self, strategy_type: Type['AbstractDriveStrategy']):
        if not isinstance(self.current_drive_strategy, strategy_type):
            self.current_drive_strategy = strategy_type()
            
    def is_uncomfortable_closing_speed(self, closing_speed, velocity):
        if(velocity < 15):
            return closing_speed > 10
        if(velocity < 25):
            return closing_speed > 13
        if(velocity < 45):
            return closing_speed > 15
        if velocity < 65:
            return closing_speed > 20
        return closing_speed > 25

    def current_lane_vector(self) -> np.ndarray:
        lane = self.model.highway.lanes[self.lane_intent]
        d = lane.end_position - self.vehicle.position
        return to_unit(d)
    
    

    # def find_lead_and_gap(self, sense):
    def find_lead_and_gap(self, max_sense=200_000_000):
        if(len(self.model.agents) <= 1):
            return None, None
        # Poll candidates until we find one in front of us
        sense = 10_000 # Start at 10 meters in front of me
        candidates = []
        while len(candidates) == 0 and sense < max_sense:
            candidates = self.model.highway.get_neighbors(self.pos, sense, False)
            candidates = list(filter(
                lambda a: a.pos[1] > self.pos[1] and self.is_in_same_lane(a),
                candidates
            ))
            sense *= 2


        # Filter: same lane and further along
        candidates = sorted(candidates, key=lambda a: a.pos[1], reverse=False)

        if len(candidates) == 0:
            return None, None

        lead = candidates[0]
        gap = (lead.pos[1] - lead.vehicle.length / 2) - (self.pos[1] + self.vehicle.length / 2)
        return lead, gap

    def find_neighbors_in_lane(self, lane_idx):
        """Finds the immediate leader and follower in a given lane."""
        if(len(self.model.agents) <= 1):
            return None, None


        sense_dist = self.sensing_distance
        neighbors = self.model.highway.get_neighbors(self.pos, sense_dist, False) 
        
        # Filter for agents in the target lane
        target_lane = self.model.highway.lanes[lane_idx]
        lane_width = target_lane.lane_width
        lane_center_x = target_lane.start_position[0]
        lane_min_x = lane_center_x - lane_width / 2
        lane_max_x = lane_center_x + lane_width / 2

        # An agent is considered in the lane if any part of its body is inside the lane boundaries
        is_partly_in_lane = lambda a: (a.pos[0] - a.vehicle.width / 2) < lane_max_x and (a.pos[0] + a.vehicle.width / 2) > lane_min_x

        lane_neighbors = [a for a in neighbors if is_partly_in_lane(a)  ]
        
        # Agents in front of us
        leaders = sorted(
            [a for a in lane_neighbors if a.pos[1] > self.pos[1]],
            key=lambda a: a.pos[1]
        )
        
        # Agents behind us
        followers = sorted(
            [a for a in lane_neighbors if a.pos[1] < self.pos[1]],
            key=lambda a: a.pos[1],
            reverse=True
        )

        leader = leaders[0] if leaders else None
        follower = followers[0] if followers else None
        return leader, follower

    def get_scalar(self, vec: np.array) -> float:
        return np.linalg.norm(vec)

    def is_colliding_at_next_step(self, lateral_velocity: float, target_lane_x: float) -> bool:
        """
        Predicts if a collision will occur during a lane change maneuver.
        It simulates forward in time for the expected duration of the maneuver.
        """
        dt = self.model.dt


        # Calculate how many steps to look ahead based on the maneuver's dynamics.
        # Duration = Distance / Speed
        lateral_distance = abs(target_lane_x - self.pos[0])
        effective_lat_v = abs(lateral_velocity) if abs(lateral_velocity) > EPS else 1.0
        lane_change_duration_ms = lateral_distance / effective_lat_v
        number_of_steps = int(lane_change_duration_ms / dt)

        if number_of_steps <= 0:
            return False # No maneuver to predict

        # --- 1. Predict the full trajectory for the ego agent ---
        ego_trajectory = []
        ego_accel = self.current_drive_strategy.calculate_accel(self)
        ego_pos = self.vehicle.position.copy()
        ego_vel = self.vehicle.velocity.copy()
        ego_vel[0] = lateral_velocity 

        # Calculate my trajectory over the enxt couple of steps
        for _ in range(number_of_steps):
            ego_vel[1] += ego_accel * dt
            ego_pos += ego_vel * dt
            ego_trajectory.append(ego_pos.copy())

        my_half_width = self.vehicle.width / 2
        my_half_length = self.vehicle.length / 2

        # Check against nearby agents
        check_radius = self.vehicle.length * 15 # Check for collisions within 15 car lengths
        neighbors = self.model.highway.get_neighbors(self.pos, check_radius, False)

        # Check all the neighbors' trajectories for a collision
        for neighbor in neighbors:
            # Get all the neighbor's values 
            n_pos = neighbor.vehicle.position.copy()
            n_vel = neighbor.vehicle.velocity.copy()
            n_accel = neighbor.vehicle.acceleration.copy()
            n_half_width = neighbor.vehicle.width / 2
            n_half_length = neighbor.vehicle.length / 2

            # Simulate neighbor's trajectory and check against mine at each step -
            for i in range(number_of_steps):
                # Update neighbor's state for the next step
                n_vel += n_accel * dt
                n_pos += n_vel * dt

                # Check for collision at this future step
                ego_future_pos = ego_trajectory[i]
                dx = abs(ego_future_pos[0] - n_pos[0])
                dy = abs(ego_future_pos[1] - n_pos[1])
                
                #Did we collide
                if dx < (my_half_width + n_half_width) and dy < (my_half_length + n_half_length):
                    return True 
        # No collision
        return False 
