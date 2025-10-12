import random
from typing import TYPE_CHECKING, Type

import numpy as np
from mesa import Agent

from . import TrafficModel
from .Vehicle import Vehicle

if TYPE_CHECKING:
    from .DriveStrategies.DriveStrategy import DriveStrategy


class TrafficAgent(Agent):
    model: TrafficModel

    def __init__(self, model: TrafficModel, position: np.ndarray, goal: np.ndarray,
                 length: float, width: float, lane_intent: int):
        super().__init__(model)
        self.vehicle: Vehicle = Vehicle(position, length, width)
        self.goal: np.ndarray = goal
        self.lane_intent = lane_intent

        # dynamics and sensing (mm, ms)
        self.max_speed = random.uniform(50, 350)   # mm/ms
        self.sensing_distance = 5_000             # mm
        self.clearance_buffer = 200.0              # mm extra beyond nose-to-nose

        # control params
        self.a_max = 3.00         # mm/ms^2
        self.b_max = 4.004         # mm/ms^2
        self.time_headway = 1.2  # seconds (⚠ multiply speeds by 1000)
        self.safe_follow_distance_minimum = 500    # mm floor
        self.slow_brake_distance_start = 12_000 #12 meters distance we start to brake
        self.hard_brake_distance_start = 5_000 #5 meters distance we start to brake hard

        # strategies
        from .DriveStrategies.CruiseStrategy import CruiseStrategy
        self.previous_drive_strategy = CruiseStrategy()
        self.current_drive_strategy = CruiseStrategy()

        # lead tracking (updated every tick)
        self.lead = None
        self.direction = None
        self.gap_to_lead = None  # center-to-center, longitudinal mm

        # decision cadence
        self.decision_time = random.randint(10, 50)  # ms
        self.internal_timer = self.decision_time

        # small initial push along lane
        self.vehicle.changeAcceleration(self.lane_direction() * random.uniform(0.002, 0.008))
        # self.model.highway.move_agent(self, self.vehicle.position)

    # ---------- tick ----------
    def step(self) -> None:
        dt = 1.0  # ms
        # self.sense()

        # decide -> set acceleration
        self.action()

        # integrate a -> v
        self.vehicle.velocity = self.vehicle.velocity + self.vehicle.acceleration * dt
        self.vehicle.position += (self.vehicle.velocity * dt
)
        # bounds
        
        if(self.unique_id ==4):
            print(f"{self.pos[1]} --- max is {self.model.highway.y_max}")
        
        if (self.vehicle.position[0] >= self.model.highway.x_max or self.vehicle.position[0] <= self.model.highway.x_min
            or self.vehicle.position[1] >= self.model.highway.y_max or self.vehicle.position[1] <= self.model.highway.y_min):
            self.model.deregister_agent(self)
            return

        self.model.highway.move_agent(self, self.vehicle.position)
        self.internal_timer += 1

    # ---------- strategy selection ----------
    def action(self) -> None:
        from .DriveStrategies.CruiseStrategy import CruiseStrategy
        from .DriveStrategies.AccelerateStrategy import AccelerateStrategy
        from .DriveStrategies.BrakeStrategy import BrakeStrategy

        # remember last without deepcopy
        self.previous_drive_strategy = self.current_drive_strategy

        # lead & lane
        lead, gap = self.find_lead_and_gap(self.sensing_distance)
        self.lead, self.gap_to_lead = lead, gap

        velocity_scalar = float(np.linalg.norm(self.vehicle.velocity))

        # if no lead: accelerate to max then cruise
        if self.lead is None:
            # no leader: accelerate up to max, then cruise
            # print(f"{self.unique_id}")
            if(self.unique_id ==4):
                print("No lead")
            if velocity_scalar < self.max_speed:
                self.assign_strategy(AccelerateStrategy)
            else:
                # print("cruise")
                self.assign_strategy(CruiseStrategy)
        else:
            if(self.unique_id ==4):
                print("YES lead")
            # there IS a leader
            if self.gap_to_lead is not None and self.gap_to_lead < self.safe_follow_distance_minimum:
                # too close → brake
                self.assign_strategy(BrakeStrategy)
            else:
                # safe gap: speed back up if under max, else hold
                if velocity_scalar < self.max_speed:
                    self.assign_strategy(AccelerateStrategy)
                else:
                    # print("gap cruise")
                    self.assign_strategy(CruiseStrategy)

        # If we swithced stratefies then brake
        if type(self.current_drive_strategy) is not type(self.previous_drive_strategy):
            self.internal_timer = -1
            
        self.current_drive_strategy.step(self)
    # ---------- helpers ----------
    def assign_strategy(self, strategy_type: Type['DriveStrategy']):
        if not isinstance(self.current_drive_strategy, strategy_type):
            self.current_drive_strategy = strategy_type()
        return

    def lane_direction(self) -> np.ndarray:
        lane = self.model.highway.lanes[self.lane_intent]
        d = lane.end_position - lane.start_position
        return d / np.linalg.norm(d)

    def find_lead_and_gap(self, sense: float = 2000):
        lane = self.model.highway.lanes[self.lane_intent]

    


        candidates = self.model.highway.get_neighbors(self.pos, sense, False)
        # print(f"{candidates=}")
        
        # Get all of the agents in the same lane and and further along on the road and sort them
        candidates = filter(lambda a: a.pos[1] > self.pos[1] and a.lane_intent == self.lane_intent, candidates )
        candidates = sorted(candidates, key=lambda a: a.pos[1], reverse=False )
        
        if len(candidates) == 0:
            return None, None
        lead = candidates[0]
        gap = (lead.pos[1] -  lead.vehicle.length/2) - (self.pos[1] -  self.vehicle.length/2)
        

        return lead, gap