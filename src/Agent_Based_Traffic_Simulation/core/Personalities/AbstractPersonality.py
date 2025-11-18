from abc import ABC

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..VehicleTypes.AbstractVehicle import AbstractVehicle


class AbstractPersonality(ABC):

    # dynamics and sensing (mm, ms)
    max_speed: float

    desired_speed: float

    # NOTE: 1 mm/ms = 1 m/s. At 35 m/s, a car travels 70m in 2s. Sensing distance should be generous.
    # NOTE: 1 mm/ms^2 = 1000 m/s^2. Realistic car acceleration is 1-3 m/s^2.
    # So we need values in the range of 0.001 to 0.003.
    sensing_distance: float
    max_acceleration: float
    cruise_gain: float
    braking_comfortable: float
    desired_time_headway: float
    b_max: float
    desired_gap: float
    vehicle: "AbstractVehicle"


    # control params
    smallest_follow_distance: float

    # Lane change parameters
    politeness_factor: float
    lane_change_threshold: float
    decision_time: int
    def __init__(self  ):
        pass