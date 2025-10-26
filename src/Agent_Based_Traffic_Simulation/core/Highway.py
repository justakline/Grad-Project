from mesa.space import ContinuousSpace
from .Lane import Lane
import numpy as np
from typing import List


class Highway(ContinuousSpace):


    def __init__(self, x_max: int, y_max: int, torus: bool, lane_count: int, lane_width: int):
        super().__init__(x_max, y_max, torus)

        self.x_max: int = int(x_max)
        self.y_max: int = int(y_max)
        self.lane_count: int = int(lane_count)
        self.lane_width: float = float(lane_width)
        self.is_torus = torus
        total_lane_w = self.lane_count * self.lane_width

        # If total lanes are wider than highway, clamp shoulder at 0 (still draw; caller should fix sizes)
        shoulder = max(0.0, (self.x_max - total_lane_w) / 2.0)

        # Precompute lane centers (mm)
        self.lane_centers: List[float] = [
            shoulder + (i + 0.5) * self.lane_width for i in range(self.lane_count)
        ]

        # Build Lane objects; x is the centerline
        self.lanes: List[Lane] = []
        for cx in self.lane_centers:
            lane = Lane(
                np.array([cx, 0.0], dtype=float),
                np.array([cx, float(self.y_max)], dtype=float),
                self.lane_width,
            )
            self.lanes.append(lane)

    # Methods for the front end
    def get_lane_centers(self) -> List[float]:
        return list(self.lane_centers)

    def get_lane_width(self) -> float:
        return float(self.lane_width)
