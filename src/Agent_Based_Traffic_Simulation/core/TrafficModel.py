import random
import numpy as np
from mesa import Model
from .Highway import Highway
from .TrafficAgent import TrafficAgent


class TrafficModel(Model):
    # All spatial units are in millimeters
    # All time units are in milliseconds
    def __init__(self, n_agents: int, seed: int, dt: int, highway: Highway):
        super().__init__(seed=seed)
        self.highway = highway
        self.steps = 0

        # Defaults for vehicle size in mm
        default_length_mm = 4500.0
        default_width_mm = 1700.0

        for i in range(n_agents):
            lane_intent = i % len(self.highway.lanes)
            lane = self.highway.lanes[lane_intent]

            # Find a clear spawn position along this lane
            start_position = self._find_clear_spawn(lane_intent, default_length_mm)
            if start_position is None:
                # Fallback if no clear spot found after N tries
                y_fallback = random.uniform(0.0, float(self.highway.y_max) / 3.0)
                start_position = np.array([float(lane.start_position[0]), y_fallback], dtype=float)

            end_position = lane.end_position.copy()

            agent = TrafficAgent(
                model=self,
                position=start_position,
                goal=end_position,
                length=default_length_mm,
                width=default_width_mm,
                lane_intent=lane_intent,
            )

            # Place exactly once here (ensure no place/move in TrafficAgent.__init__ if you prefer single-source)
            self.highway.place_agent(agent, tuple(agent.vehicle.position))

            # Give a small initial forward velocity to reduce clumping at t=0
            d = lane.end_position - lane.start_position
            d = d / np.linalg.norm(d)
            init_speed = random.uniform(0.1 * agent.max_speed, 0.4 * agent.max_speed)  # mm/ms
            agent.vehicle.velocity = d * init_speed

            self.agents.add(agent)

    def step(self):
        self.agents.do("step")

    def _find_clear_spawn(self, lane_idx: int, vehicle_length_mm: float, tries: int = 50):
        """Pick a start position on lane `lane_idx` with no nearby agents.
        Uses Mesa get_neighbors so we avoid overlaps at t=0."""
        lane = self.highway.lanes[lane_idx]
        x = float(lane.start_position[0])

        # at least one car length worth of spacing, with a small buffer
        spawn_radius_mm: float = float(vehicle_length_mm) * 1.2

        # keep a small vertical margin so spawns are not right at the bounds
        top_margin = 500.0
        bottom_margin = 500.0
        y_min = top_margin
        y_max = float(self.highway.y_max) - bottom_margin

        for _ in range(tries):
            y = random.uniform(y_min, y_max)
            pos = np.array([x, y], dtype=float)
            if(len(self.agents)== 0):
                return pos
            if not self.highway.get_neighbors(tuple(pos), spawn_radius_mm, False):
                return pos

        return None  # could not find a clear spot
