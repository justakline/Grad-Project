import math
import random

import mesa
import numpy as np
import copy

from mesa import Model, Agent
from mesa.space import ContinuousSpace

from . import TrafficModel
from .Vehicle import Vehicle


from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
    from .DriveStrategies.DriveStrategy import DriveStrategy
    from .DriveStrategies.CruiseStrategy import CruiseStrategy
    from .DriveStrategies.AccelerateStrategy import AccelerateStrategy

class TrafficAgent(Agent):
    model: TrafficModel
    def __init__(self, model:TrafficModel, position:np.array, goal: np.array, length: float, width:float, lane_intent:int):
        super().__init__(model)
        self.vehicle:Vehicle = Vehicle(position, length, width)
        self.goal:np.array = goal
        self.lane_intent = lane_intent
        self.max_speed = random.randint(18,250 ) #40  miles per hour in mm/ms as the lowest

        direction: np.array = np.subtract(model.highway.lanes[lane_intent].end_position,model.highway.lanes[lane_intent].start_position)
        acceleration = direction/np.linalg.norm(direction) * random.uniform(0.5,3)
        from .DriveStrategies.CruiseStrategy import CruiseStrategy
        self.previous_drive_strategy = CruiseStrategy()
        self.current_drive_strategy = CruiseStrategy()
        self.vehicle.changeAcceleration(acceleration)
        
        # How long it takes to make a decision in ms
        self.decision_time = random.randint(10, 50)
        # How long since the last decision
        self.internal_timer = self.decision_time

        self.model.highway.move_agent(self, self.vehicle.position)
        pass

    def step(self) -> None:
        # For right now they are only going to decide to get a working prototype down

        self.action()
     

        if(self.vehicle.position[0] >= self.model.highway.x_max or self.vehicle.position[0] <= self.model.highway.x_min
        or self.vehicle.position[1] >= self.model.highway.y_max or self.vehicle.position[1] <= self.model.highway.y_min ):
            self.remove()
            print("agent removed")
            # self.model.highway.remove_agent(self)
            return

        # Move the agent to its new location in the model
        self.model.highway.move_agent(self, self.vehicle.position)

        pass

    def sense(self) -> None:
        pass

    def decide(self) -> None:
        pass

    def action(self) -> None:
        from .DriveStrategies.CruiseStrategy import CruiseStrategy
        from .DriveStrategies.AccelerateStrategy import AccelerateStrategy
        from .DriveStrategies.BrakeStrategy import BrakeStrategy

        self.previous_drive_strategy = copy.deepcopy(self.current_drive_strategy)
        neighbors = self.model.highway.get_neighbors(tuple(self.vehicle.position), 2000, False)
        # print(neighbors, flush=True)
        
        # Do not change the strategy if it is not time for a decision
        if(self.internal_timer < self.decision_time):
            pass
        # Acclerate
        elif (np.linalg.norm(self.vehicle.velocity) <  np.linalg.norm(self.max_speed)):
            # self.assign_strategy(AccelerateStrategy)
            if not isinstance(self.previous_drive_strategy, AccelerateStrategy):
                self.current_drive_strategy = AccelerateStrategy()
        # Brake if there is a car getting close and i sped up to them
        elif(len(neighbors) >= 1 and np.linalg.norm(self.vehicle.velocity) >= np.linalg.norm(neighbors[0].vehicle.velocity) ):
            # self.assign_strategy(BrakeStrategy)
            self.current_drive_strategy = BrakeStrategy()
            pass
        else:
            # self.assign_strategy(CruiseStrategy)
        # Cruise if there is nothing else is met
            if not isinstance(self.previous_drive_strategy, CruiseStrategy):
                self.current_drive_strategy = CruiseStrategy()

 
        self.current_drive_strategy.step(self)

        # if there was a change in strategy, then you have to wait for a new decision
        if(type(self.current_drive_strategy) is not type(self.previous_drive_strategy) ):
            self.internal_timer = -1
        self.internal_timer += 1
        pass
    
    def get_distance_to_agent(self, other:'TrafficAgent') -> int:
        return self.model.highway.get_distance(self.vehicle.position, other.vehicle.position)

    # Assign a new strategy if it is not already assigned to be that strategy
    def assign_strategy(self, strategy_type: Type['DriveStrategy']):

        if not isinstance(self.previous_drive_strategy, strategy_type):
            self.current_drive_strategy = strategy_type()
        return 