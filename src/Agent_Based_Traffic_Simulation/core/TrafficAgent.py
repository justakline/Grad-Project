import random
from typing import TYPE_CHECKING, Type

import numpy as np


from .Utils import to_unit, EPS
from mesa import Agent

# from Agent_Based_Traffic_Simulation.core.DriveStrategies import AbstractDriveStrategy
from . import TrafficModel
from .Vehicle import Vehicle

if TYPE_CHECKING:
    from .DriveStrategies.AbstractDriveStrategy import AbstractDriveStrategy


class TrafficAgent(Agent):
    model: TrafficModel

    def __init__(self, model: TrafficModel, position: np.ndarray, goal: np.ndarray,
                 length: float, width: float, lane_intent: int, spawn_time, velocity = 0):
        super().__init__(model)
        dt = model.dt

        self.vehicle: Vehicle = Vehicle(position, length, width)
        self.goal: np.ndarray = goal
        self.lane_intent = lane_intent
        self.current_lane = lane_intent
        self.spawn_time = spawn_time

        # dynamics and sensing (mm, ms)
        self.max_speed = random.uniform(35, 45)  # mm/ms
        # NOTE: 1 mm/ms = 1 m/s. At 35 m/s, a car travels 70m in 2s. Sensing distance should be generous.
        self.sensing_distance = random.uniform(50_000, 100_000)  # mm (100-200 meters)
        self.emergency_sensing_distance = 2* self.sensing_distance  # mm (200-300 meters)
        self.desired_speed = random.uniform(0.75, 0.95) * self.max_speed

        # NOTE: 1 mm/ms^2 = 1000 m/s^2. Realistic car acceleration is 1-3 m/s^2.
        # So we need values in the range of 0.001 to 0.003.
        self.max_acceleration = random.uniform(0.0025, 0.004)  # mm/ms^2 (Represents 2.5-4 m/s^2)
        self.cruise_gain = random.uniform(0.0005, 0.0015)   # 1/ms
        self.braking_comfortable = random.uniform(0.003, 0.0045) # mm/ms^2 (Represents 2-4 m/s^2, a comfortable brake)
        self.desired_time_headway = random.uniform(1200, 2400)  # ms
        self.time_headway = 1.2  # seconds (⚠ multiply speeds by 1000)
        self.reaction_time_ms = int(self.time_headway * 1000)  # ms
        self.b_max = random.uniform(0.008, 0.010)  # mm/ms^2 (Represents 8-10 m/s^2, max emergency braking)
        self.desired_gap =  self.vehicle.length *random.uniform(2, 3.2)  # mm


        # control params
        # This value was 3.00, which is 3000 m/s^2. Assuming it's unused or a typo. Commenting out for safety.
        # self.acceleration_increase = 3.00  # mm/ms^2
        self.smallest_follow_distance = self.vehicle.length *random.uniform(1, 1.4)  # mm
        self.slow_brake_distance_start = 12000  # mm (12 meters)
        self.hard_brake_distance_start = 5000  # mm (5 meters)

        # Lane change parameters
        self.politeness_factor = random.uniform(0.02, 0.5) # 0 is egoistic, >1 is altruistic
        self.lane_change_threshold = random.uniform(0.00005, 0.0009) # Min acceleration gain to justify a change

        # strategies
        from .DriveStrategies.CruiseStrategy import CruiseStrategy
        from .DriveStrategies.LaneStay import LaneStay
        self.previous_drive_strategy = CruiseStrategy()
        self.current_drive_strategy = CruiseStrategy()
        self.lane_change_strategy = LaneStay()

        # tracking
        self.lead = None
        self.direction = None
        self.gap_to_lead = None  # center-to-center, longitudinal mm

        # decision cadence
        self.decision_time = random.randint(125, 250)  # ms
        self.internal_timer = self.decision_time
        self.initial_lane_x = self.vehicle.position[0]

        # small initial push along lane
        if(velocity == 0 ):
            self.vehicle.velocity = self.current_lane_vector() * self.desired_speed/10
        else:
            self.vehicle.velocity = self.current_lane_vector() * velocity

        # print(self.vehicle.velocity)
        # print("hretr")
        # self.vehicle.changeAcceleration(self.current_lane_vector() * random.uniform(0.002, 0.008))

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

        # Check for out of bounds and either remove or adjust
        if (self.check_outside_of_bounds()):
            # This is extra cleanup because if I only remove it, the follow vehicle still uses its end position, ie the finish line
            # As the follow position, and since there is no more changes to position, the follow vehicle would brake, this presents that
            if(not self.model.highway.is_torus):
                # print("removed")
                # self.pos = (self.model.highway.x_max *2, self.model.highway.y_max *2)
                self.remove_self()
                return
            self.vehicle.position[1] = 0
                
        if type(self.current_drive_strategy) is not type(self.previous_drive_strategy):
            self.internal_timer = -1
            
        self.model.highway.move_agent(self, tuple(self.vehicle.position))
        self.internal_timer += dt

    def sense(self) -> None:
        self.previous_drive_strategy = self.current_drive_strategy
        self.lead, self.gap_to_lead = self.find_lead_and_gap()

    def action(self) -> None:
        self.choose_drive_strategy()
        self.choose_lane_change_strategy()
        self.do_lane_change_strategy()
        longitudinal_accel_magnitude = self.current_drive_strategy.calculate_accel(self)
        self.vehicle.velocity[1] += longitudinal_accel_magnitude * self.model.dt

    
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
        self.lead, self.gap_to_lead = self.find_lead_and_gap()
        
        # If we do not have a person in front of us or we are in the first x ms of spawning
        if self.lead is None or self.gap_to_lead is None or self.spawn_time + self.model.initial_accelerate_time > self.model.total_time:
            self.assign_strategy(AccelerateStrategy) 
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
        if(self.model.highway.is_torus):
            self.vehicle.position[1] = 0
        else:
            # print("removed")
            # This is extra cleanup because if I only remove it, the follow vehicle still uses its end position, ie the finish line
            # As the follow position, and since there is no more changes to position, the follow vehicle would brake, this presents that
            self.pos = (self.model.highway.x_max *2, self.model.highway.y_max *2)
            self.remove()
            # self.model.highway.remove_agent(self)
    

            
    # ---------- helpers ----------
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
        if(velocity > 25):
            return closing_speed > 13
        if(velocity > 45):
            return closing_speed > 15
        if velocity > 65:
            return closing_speed > 20
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
                lambda a: a.pos[1] > self.pos[1] and a.current_lane == self.current_lane,
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


        sense_dist = 150_000 # 150m
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
