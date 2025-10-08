import math
import random

import mesa
import numpy as np
import copy

from mesa import Model, Agent
from mesa.space import ContinuousSpace

from . import TrafficModel
from .Vehicle import Vehicle


from typing import TYPE_CHECKING
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

        self.previous_drive_strategy = copy.deepcopy(self.current_drive_strategy)
        if (np.linalg.norm(self.vehicle.velocity) <  np.linalg.norm(self.max_speed)):
            if not isinstance(self.previous_drive_strategy, AccelerateStrategy):
                self.current_drive_strategy = AccelerateStrategy()
        else:
            if not isinstance(self.previous_drive_strategy, CruiseStrategy):
                self.current_drive_strategy = CruiseStrategy()

 
        self.current_drive_strategy.step(self)



        pass
