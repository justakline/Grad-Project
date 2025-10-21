import random
import numpy as np
from mesa import Model
from .Highway import Highway
from .TrafficAgent import TrafficAgent


class TrafficModel(Model):
    """
    All spatial units are in millimeters; time in milliseconds.
    Agents spawn on lane CENTERS coming from Highway.lanes[*].start_position[0].
    """

    def __init__(self, n_agents: int, seed: int, dt: int, highway: Highway):
        super().__init__(seed=seed)
        self.highway = highway
        self.steps = 0
        self.dt = dt
        self.total_time = 0

        # Defaults for vehicle size in mm
        default_length_mm = 4500.0
        default_width_mm = 1700.0

        for i in range(n_agents):
            lane_intent = i % len(self.highway.lanes)
            lane = self.highway.lanes[lane_intent]

            # Spawn on lane center X
            start_position = self._find_clear_spawn(
                lane_idx=lane_intent,
                vehicle_length_mm=default_length_mm,
                tries=150
            )
            if start_position is None:
                # There are no more open spots so we can not add any more into the sim
                break
                # Fallback if no clear spot found after N tries
                # y_fallback = random.uniform(0.0, float(self.highway.y_max) / 3.0)
                # start_position = np.array([float(lane.start_position[0]), y_fallback], dtype=float)

            end_position = lane.end_position.copy()

            agent = TrafficAgent(
                model=self,
                position=start_position,
                goal=end_position,
                length=default_length_mm,
                width=default_width_mm,
                lane_intent=lane_intent,
            )

            # Place once in the space
            self.highway.place_agent(agent, tuple(agent.vehicle.position))


            self.agents.add(agent)

    def step(self):
        self.agents.do("step")
        self.steps += 1
        self.total_time +=self.dt

    def _find_clear_spawn(self, lane_idx: int, vehicle_length_mm: float, tries: int = 50):
        """
        Pick a start position on lane `lane_idx` with no nearby agents.
        Uses Mesa get_neighbors so we avoid overlaps at t=0.
        """
        lane = self.highway.lanes[lane_idx]
        x_center = float(lane.start_position[0])  # lane center X

        # At least one car length worth of spacing, with a small buffer
        spawn_radius_mm: float = float(vehicle_length_mm) * 1.2

        # Keep a small vertical margin so spawns are not right at the bounds
        top_margin = 500.0
        bottom_margin = 500.0
        y_min = top_margin
        y_max = float(self.highway.y_max) - bottom_margin

        for _ in range(tries):
            y = random.uniform(y_min, y_max)
            pos = np.array([x_center, y], dtype=float)
            if len(self.agents) == 0:
                return pos
            # Get the neighbors that are in the same lane
            neighbors:list = list(filter( lambda a: a.lane_intent == lane_idx,self.highway.get_neighbors(tuple(pos), spawn_radius_mm, False)))
            if  len(neighbors) ==0 :
                return pos

        return None  # could not find a clear spot
