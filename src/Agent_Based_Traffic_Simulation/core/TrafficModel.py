import random

from mesa import Model
from .Highway import Highway
from .TrafficAgent import TrafficAgent
import numpy as np
class TrafficModel(Model):
    # All spacial units are in millimeters
    # All time units are in milliseconds
    def __init__(self, n_agents:int, dt:int, highway:Highway):
        # Call the parent constructor
        super().__init__()
        self.dt = dt # milliseconds

        self.highway: Highway = highway


        # Create all my vehicle agents
        # This is hard coded stuff for now to understand the mechanixs of a driving sim
        # Starting super basic
        for i in range(n_agents):

            lane_intent = random.randint(0, len(highway.lanes)-1)
            lane = highway.lanes[lane_intent]
            start_position, end_position = lane.start_position, lane.end_position
            # print(f"{start_position=}, {end_position=}")
            agent = TrafficAgent(self, start_position, end_position, 4500, 1700, lane_intent)
            highway.move_agent(agent, start_position)


    def step(self):
        self.agents.do("step")