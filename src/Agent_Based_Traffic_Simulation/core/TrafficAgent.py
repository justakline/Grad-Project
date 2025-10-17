import random
from typing import TYPE_CHECKING, Type

import numpy as np
from mesa import Agent

# from Agent_Based_Traffic_Simulation.core.DriveStrategies import AbstractDriveStrategy

from . import TrafficModel
from .Vehicle import Vehicle

if TYPE_CHECKING:
    from .DriveStrategies.AbstractDriveStrategy import AbstractDriveStrategy


class TrafficAgent(Agent):
    model: TrafficModel

    def __init__(self, model: TrafficModel, position: np.ndarray, goal: np.ndarray,
                 length: float, width: float, lane_intent: int):
        super().__init__(model)
        self.vehicle: Vehicle = Vehicle(position, length, width)
        self.goal: np.ndarray = goal
        self.lane_intent = lane_intent

        # dynamics and sensing (mm, ms)
        self.max_speed = random.uniform(200, 350)   # mm/ms
        self.sensing_distance = random.uniform(5000, 15000)            # mm 12_000 mm

        # control params
        self.acceleration_increase = 3.00         # mm/ms^2
        self.b_max = 4.004         # mm/ms^2
        self.time_headway = 1.2  # seconds (⚠ multiply speeds by 1000)
        self.smallest_follow_distance = 10_00    # mm floor
        self.slow_brake_distance_start = 12_000 #12 meters distance we start to brake
        self.hard_brake_distance_start = 5_000  #5 meters distance we start to brake hard

        # strategies
        from .DriveStrategies.CruiseStrategy import CruiseStrategy
        self.previous_drive_strategy = CruiseStrategy()
        self.current_drive_strategy = CruiseStrategy()

        # Tracking the car that is in front of them
        self.lead = None
        self.direction = None
        self.gap_to_lead = None  # center-to-center, longitudinal mm

        # decision cadence
        self.decision_time = random.randint(10, 50)  # ms
        self.internal_timer = self.decision_time

        # small initial push along lane
        self.vehicle.changeAcceleration(self.current_lane_vector() * random.uniform(0.002, 0.008))

    # ---------- tick ----------
    def step(self) -> None:
        dt = 1.0  # ms
        # self.sense()

        # decide -> set acceleration
        self.action()

        self.vehicle.velocity = self.vehicle.velocity + self.vehicle.acceleration * dt



        self.vehicle.position += (self.vehicle.velocity * dt)
    
        # if(self.unique_id ==4):
        #     print(f"{self.pos[1]} --- max is {self.model.highway.y_max}")
        
        # Out of bounds of the highwa
        # if(self.unique_id == 4):
        #     print(f"{self.vehicle.position[1]=} {self.model.highway.y_max=}")

        if (self.vehicle.position[0] >= self.model.highway.x_max or self.vehicle.position[0] <= self.model.highway.x_min
            or self.vehicle.position[1] >= self.model.highway.y_max or self.vehicle.position[1] <= self.model.highway.y_min):
            # self.model.deregister_agent(self)
            
            print("removed")
            self.remove()
            return

        self.model.highway.move_agent(self, self.vehicle.position)
        self.internal_timer += 1

    # ---------- strategy selection ----------
    def action(self) -> None:
        from .DriveStrategies.CruiseStrategy import CruiseStrategy
        from .DriveStrategies.AccelerateStrategy import AccelerateStrategy
        from .DriveStrategies.BrakeStrategy import BrakeStrategy

        # remember last
        self.previous_drive_strategy = self.current_drive_strategy
        self.lead, self.gap_to_lead = self.find_lead_and_gap(self.sensing_distance)

        velocity_scalar = float(np.linalg.norm(self.vehicle.velocity))

        # if no lead: accelerate to max then cruise
        if self.lead is None:
            # no leader: accelerate up to max, then cruise
            # print(f"{self.unique_id}")
            # if(self.unique_id ==4):
            #     print("No lead")
            if velocity_scalar < self.max_speed:
                if(self.unique_id == 4):
                    print(f"{velocity_scalar} {self.max_speed=}")
                self.assign_strategy(AccelerateStrategy)
            else:
                # print("cruise")
                self.assign_strategy(CruiseStrategy)
        else:
            # there IS a leader
            # if(self.unique_id ==4):
            #     print("YES lead")

            # If the car in front of us is faster or the same speed then just stay the same speed
            if(np.linalg.norm(self.lead.vehicle.velocity) >= np.linalg.norm(self.vehicle.velocity) ):
                self.assign_strategy(CruiseStrategy)

            elif self.gap_to_lead is not None:
                # too close → brake
                self.assign_strategy(BrakeStrategy)
            # else:
            #     # safe gap: speed back up if under max, else hold
            #     if velocity_scalar < self.max_speed:
            #         self.assign_strategy(AccelerateStrategy)
            #     else:
            #         # print("gap cruise")
            #         self.assign_strategy(CruiseStrategy)

        # If we switched strategies, then reset the timer so we have to wait to make another decision
        if type(self.current_drive_strategy) is not type(self.previous_drive_strategy):
            self.internal_timer = -1
            
        self.current_drive_strategy.step(self)
    # ---------- helpers ----------
    def assign_strategy(self, strategy_type: Type['AbstractDriveStrategy']): # type: ignore
        if not isinstance(self.current_drive_strategy, strategy_type):
            self.current_drive_strategy = strategy_type()
        return

    def current_lane_vector(self) -> np.ndarray:
        lane = self.model.highway.lanes[self.lane_intent]
        # d = lane.end_position - lane.start_position
        d = lane.end_position - self.vehicle.position
        return d / np.linalg.norm(d)

    def find_lead_and_gap(self, sense: float = 2000):
        lane = self.model.highway.lanes[self.lane_intent]

    


        candidates = self.model.highway.get_neighbors(self.pos, sense, False)
        
        # Get all of the agents in the same lane and and further along on the road and sort them
        candidates = filter(lambda a: a.pos[1] > self.pos[1] and a.lane_intent == self.lane_intent, candidates )
        candidates = sorted(candidates, key=lambda a: a.pos[1], reverse=False )
        
        if(self.unique_id ==4):
            can = list(map(lambda a : a.unique_id,candidates))
        if len(candidates) == 0:
            return None, None
        lead = candidates[0]

        gap = (lead.pos[1] -  lead.vehicle.length/2) - (self.pos[1] +  self.vehicle.length/2)
        

        return lead, gap
    
    def get_scalar(self, vec: np.array) -> float:
        return np.linalg.norm(vec)