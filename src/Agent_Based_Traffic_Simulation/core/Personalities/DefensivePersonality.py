import random
from .AbstractPersonality import AbstractPersonality


class DefensivePersonality(AbstractPersonality):
    def __init__(self):
        super().__init__()

        self.max_speed = random.uniform(22, 27)  # mm/ms
        # NOTE: 1 mm/ms = 1 m/s. At 35 m/s, a car travels 70m in 2s. Sensing distance should be generous.
        self.sensing_distance = random.uniform(175_000, 200_000)  # mm (100-200 meters)
        self.desired_speed = random.uniform(0.75, 0.95) * self.max_speed

        # NOTE: 1 mm/ms^2 = 1000 m/s^2. Realistic car acceleration is 1-3 m/s^2.
        # So we need values in the range of 0.001 to 0.003.
        self.max_acceleration = random.uniform(0.0017, 0.0025)  # mm/ms^2 (Represents 2.5-4 m/s^2)
        self.cruise_gain = random.uniform(0.0003, 0.006)   # 1/ms
        self.braking_comfortable = random.uniform(0.003, 0.0045) # mm/ms^2 (Represents 2-4 m/s^2, a comfortable brake)
        self.desired_time_headway = random.uniform(2000, 2500)  # ms
        self.b_max = random.uniform(0.008, 0.010)  # mm/ms^2 (Represents 8-10 m/s^2, max emergency braking)

        # control params
        # These values depend on vehicle length, so they are calculated in TrafficAgent after vehicle is known
        self.smallest_follow_distance_factor = random.uniform(1.6, 2.0)
        self.desired_gap_factor = random.uniform(3.5, 4.5)

        # Lane change parameters
        self.politeness_factor = random.uniform(0.6, 0.8) # 0 is egoistic, >1 is altruistic
        self.lane_change_threshold = random.uniform(0.00001, 0.00003) # Min acceleration gain to justify a change
        self.decision_time = random.randint(100, 150)  # ms