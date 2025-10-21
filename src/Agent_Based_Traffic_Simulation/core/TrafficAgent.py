import random
from typing import TYPE_CHECKING, Type

import numpy as np
from .Utils import to_unit, EPS
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
        dt = model.dt

        self.vehicle: Vehicle = Vehicle(position, length, width)
        self.goal: np.ndarray = goal
        self.lane_intent = lane_intent

        # dynamics and sensing (mm, ms)
        self.max_speed = random.uniform(35, 45)  # mm/ms
        self.sensing_distance = random.uniform(60000, 120000)  # mm
        self.desired_speed = random.uniform(0.8, 0.95) * self.max_speed
        self.max_acceleration = random.uniform(0.0015, 0.003)  # mm/ms^2
        self.cruise_gain = random.uniform(0.0007, 0.0015)   # 1/ms
        self.braking_comfortable = random.uniform(0.002, 0.004)
        self.desired_time_headway = random.uniform(900, 1800)  # ms
        self.time_headway = 1.2  # seconds (⚠ multiply speeds by 1000)
        self.reaction_time_ms = int(self.time_headway * 1000)  # ms
        self.b_max = random.uniform(0.008, 0.012)  # mm/ms^2

        # control params
        self.acceleration_increase = 3.00  # mm/ms^2
        self.smallest_follow_distance = self.vehicle.length *0.3  # mm
        self.slow_brake_distance_start = 12000  # mm (12 meters)
        self.hard_brake_distance_start = 5000  # mm (5 meters)

        # strategies
        from .DriveStrategies.CruiseStrategy import CruiseStrategy
        self.previous_drive_strategy = CruiseStrategy()
        self.current_drive_strategy = CruiseStrategy()

        # tracking
        self.lead = None
        self.direction = None
        self.gap_to_lead = None  # center-to-center, longitudinal mm

        # decision cadence
        self.decision_time = random.randint(10, 50)  # ms
        self.internal_timer = self.decision_time

        # small initial push along lane
        self.vehicle.velocity = self.current_lane_vector() * self.desired_speed
        print(self.current_lane_vector())
        print(self.vehicle.velocity)
        # self.vehicle.changeAcceleration(self.current_lane_vector() * random.uniform(0.002, 0.008))

    # ---------- tick ----------
    def step(self) -> None:
        dt = self.model.dt  # ms

        # self.sense()
        # decide -> set acceleration
        self.action()
        
        # Hard cap of trying to not make them overlap
        if(self.gap_to_lead is not None and self.gap_to_lead < self.smallest_follow_distance):
            self.vehicle.velocity = self.lead.vehicle.velocity



        self.vehicle.velocity = self.vehicle.velocity + self.vehicle.acceleration * dt
        self.vehicle.position += self.vehicle.velocity * dt

        if (
            self.vehicle.position[0] >= self.model.highway.x_max
            or self.vehicle.position[0] <= self.model.highway.x_min
            or self.vehicle.position[1] >= self.model.highway.y_max
            or self.vehicle.position[1] <= self.model.highway.y_min
        ):
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

        self.previous_drive_strategy = self.current_drive_strategy

        self.lead, self.gap_to_lead = self.find_lead_and_gap(self.sensing_distance)
        current_speed = float(np.linalg.norm(self.vehicle.velocity))

        minimum_static_gap = float(self.smallest_follow_distance)
        time_headway_ms = float(self.desired_time_headway)  # use the sampled one
        desired_headway_gap_distance = minimum_static_gap + time_headway_ms * current_speed

        # add hysteresis buffer so you do not bounce into braking too early
        safe_gap_buffer_mm = max(2000.0, 0.10 * desired_headway_gap_distance)  # 10% or at least 2 m
        brake_threshold = desired_headway_gap_distance - safe_gap_buffer_mm

        if self.lead is None or self.gap_to_lead is None:
            # no leader: accelerate toward desired, then cruise
            if current_speed + EPS < self.desired_speed:
                self.assign_strategy(AccelerateStrategy)
            else:
                self.assign_strategy(CruiseStrategy)
        else:
            leader_speed = float(np.linalg.norm(self.lead.vehicle.velocity))
            closing_speed = current_speed - leader_speed

            # If gap is generous OR we are not closing, keep cruise
            if self.gap_to_lead > desired_headway_gap_distance:
                if(closing_speed >= 0.0):
                    self.assign_strategy(BrakeStrategy)
                # accelerate only if under desired, else cruise
                if current_speed + EPS < self.desired_speed:
                    self.assign_strategy(AccelerateStrategy)
                else:
                    self.assign_strategy(CruiseStrategy)
            else:
                # only brake if clearly inside threshold
                # self.assign_strategy(BrakeStrategy)
                if self.gap_to_lead < brake_threshold and closing_speed > 0.0:
                    self.assign_strategy(BrakeStrategy)
                else:
                    # mild follow-by-cruise behavior
                    self.assign_strategy(CruiseStrategy)

        if type(self.current_drive_strategy) is not type(self.previous_drive_strategy):
            self.internal_timer = -1

        self.current_drive_strategy.step(self)

    # ---------- helpers ----------
    def assign_strategy(self, strategy_type: Type['AbstractDriveStrategy']):
        if not isinstance(self.current_drive_strategy, strategy_type):
            self.current_drive_strategy = strategy_type()

    def current_lane_vector(self) -> np.ndarray:
        lane = self.model.highway.lanes[self.lane_intent]
        d = lane.end_position - self.vehicle.position
        return to_unit(d)

    def find_lead_and_gap(self, sense: float = 2000):
        lane = self.model.highway.lanes[self.lane_intent]
        candidates = self.model.highway.get_neighbors(self.pos, sense, False)

        # Filter: same lane and further along
        candidates = filter(
            lambda a: a.pos[1] > self.pos[1] and a.lane_intent == self.lane_intent,
            candidates
        )
        candidates = sorted(candidates, key=lambda a: a.pos[1], reverse=False)

        if len(candidates) == 0:
            return None, None

        lead = candidates[0]
        gap = (lead.pos[1] - lead.vehicle.length / 2) - (self.pos[1] + self.vehicle.length / 2)
        return lead, gap

    def get_scalar(self, vec: np.array) -> float:
        return np.linalg.norm(vec)
