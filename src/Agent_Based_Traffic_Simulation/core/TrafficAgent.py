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
        self.sensing_distance = random.uniform(15000, 25000)  # mm
        self.emergency_sensing_distance = random.uniform(45000, 70000)  # mm
        self.desired_speed = random.uniform(0.75, 0.95) * self.max_speed
        self.max_acceleration = random.uniform(0.0010, 0.0025)  # mm/ms^2
        self.cruise_gain = random.uniform(0.0005, 0.0015)   # 1/ms
        self.braking_comfortable = random.uniform(0.006, 0.015)
        self.desired_time_headway = random.uniform(1200, 2400)  # ms
        self.time_headway = 1.2  # seconds (⚠ multiply speeds by 1000)
        self.reaction_time_ms = int(self.time_headway * 1000)  # ms
        self.b_max = random.uniform(0.015, 0.025)  # mm/ms^2
        self.desired_gap =  self.vehicle.length *random.uniform(2, 3.2)  # mm


        # control params
        self.acceleration_increase = 3.00  # mm/ms^2
        self.smallest_follow_distance = self.vehicle.length *random.uniform(1, 1.4)  # mm
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
        self.decision_time = random.randint(125, 250)  # ms
        self.internal_timer = self.decision_time

        # small initial push along lane
        self.vehicle.velocity = self.current_lane_vector() * self.desired_speed
        print(self.current_lane_vector())
        print(self.vehicle.velocity)
        # self.vehicle.changeAcceleration(self.current_lane_vector() * random.uniform(0.002, 0.008))

    # ---------- tick ----------
    def step(self) -> None:
        dt = self.model.dt  # ms
        from .DriveStrategies.BrakeStrategy import BrakeStrategy

        # self.sense()
        # decide -> set acceleration
        self.action()
        
        if(self.gap_to_lead is not None and self.gap_to_lead < self.smallest_follow_distance):
            self.vehicle.velocity = self.lead.vehicle.velocity * 0.9



        self.vehicle.velocity = self.vehicle.velocity + self.vehicle.acceleration * dt

        if (np.linalg.norm(self.vehicle.velocity < 0)):
            self.vehicle.velocity = np.array([0,1])
        self.vehicle.position += self.vehicle.velocity * dt

        if (

            self.vehicle.position[0] >= self.model.highway.x_max
            or self.vehicle.position[0] <= self.model.highway.x_min
            or self.vehicle.position[1] >= self.model.highway.y_max
            or self.vehicle.position[1] <= self.model.highway.y_min
        ):
            if(self.model.highway.is_torus):
                self.vehicle.position[1] = 0
            else:
                print("removed")
                self.remove()
                return

        self.model.highway.move_agent(self, self.vehicle.position)
        self.internal_timer += dt

    # ---------- strategy selection ----------
    def action(self) -> None:
        from .DriveStrategies.CruiseStrategy import CruiseStrategy
        from .DriveStrategies.AccelerateStrategy import AccelerateStrategy
        from .DriveStrategies.BrakeStrategy import BrakeStrategy

        # Have a commitment to one strategy, but if we are too close to
        # The car in front of us then react
        if(self.internal_timer < self.decision_time):
            if(self.lead and self.gap_to_lead < self.smallest_follow_distance):
                self.assign_strategy(BrakeStrategy)
            self.current_drive_strategy.step(self)
            return
        self.previous_drive_strategy = self.current_drive_strategy

        self.lead, self.gap_to_lead = self.find_lead_and_gap(self.sensing_distance)
        current_speed = float(np.linalg.norm(self.vehicle.velocity))

        minimum_static_gap = float(self.smallest_follow_distance)
        time_headway_ms = float(self.desired_time_headway)  # use the sampled one
        # desired_headway_gap_distance = minimum_static_gap + time_headway_ms * current_speed
        desired_headway_gap_distance = self.desired_gap

        # add hysteresis buffer so you do not bounce into braking too early
        safe_gap_buffer_mm = max(2000.0, 0.10 * desired_headway_gap_distance)  # 10% or at least 2 m
        brake_threshold = desired_headway_gap_distance - safe_gap_buffer_mm

        # # Check for emergency brake ahead
        # emergency_lead, emergency_gap = self.find_lead_and_gap(self.emergency_sensing_distance)
        # if(emergency_lead):
        #     emergency_leader_speed = float(np.linalg.norm(emergency_lead.vehicle.velocity))
        #     emergency_closing_speed = current_speed - emergency_leader_speed
        #     if(self.is_uncomfortable_closing_speed(emergency_closing_speed, current_speed)):
        #         self.assign_strategy(BrakeStrategy)

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
                if(self.is_uncomfortable_closing_speed(closing_speed, current_speed)):
                    self.assign_strategy(BrakeStrategy)
                # accelerate only if under desired, else cruise
                # if current_speed + EPS < self.desired_speed:
                #     self.assign_strategy(AccelerateStrategy)
                # else:
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
    def is_uncomfortable_closing_speed(self, closing_speed, velocity):
        if(velocity < 15):
            return closing_speed > 10
        if(velocity > 25):
            return closing_speed > 13
        if(velocity > 45):
            return closing_speed > 15
        if velocity > 65:
            return closing_speed > 20
    def current_lane_vector(self) -> np.ndarray:
        lane = self.model.highway.lanes[self.lane_intent]
        d = lane.end_position - self.vehicle.position
        return to_unit(d)

    # def find_lead_and_gap(self, sense):
    def find_lead_and_gap(self, sense):
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
