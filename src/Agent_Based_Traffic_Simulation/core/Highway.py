
from mesa.space import ContinuousSpace
from .Lane import Lane
import numpy as np


class Highway(ContinuousSpace):

    def __init__(self,x_max:int, y_max:int, torus:bool, lane_count: int, lane_width:int):
        super().__init__(x_max, y_max, torus)
        self.lanes: list[Lane] = []
        for i in range(lane_count):
            lane = Lane(np.array([lane_width*(i+1),0]), np.array([lane_width*(i+1),y_max]), lane_width)
            self.lanes.append(lane)
