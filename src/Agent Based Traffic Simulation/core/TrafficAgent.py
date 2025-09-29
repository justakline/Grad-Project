import math
import random

import mesa
import numpy as np

from mesa import Model, Agent
from mesa.space import ContinuousSpace

import TrafficModel
from Vehicle import Vehicle

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

        print(f"direction is to {direction}")
        print(f"acceleration set to {acceleration}")
        self.vehicle.changeAcceleration(acceleration)

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


        if (np.linalg.norm(self.vehicle.velocity) <  np.linalg.norm(self.max_speed)):
            print(f" {np.linalg.norm(self.vehicle.acceleration)=}")
            self.vehicle.changeVelocity(self.vehicle.acceleration)
        print(f"Before: {self.vehicle.position=}")
        self.vehicle.changePosition(self.vehicle.velocity)
        print(f"After: {self.vehicle.position=}\n\n")


        pass
