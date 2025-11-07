import random
from .AbstractPersonality import AbstractPersonality


class AggressivePersonality(AbstractPersonality):
    def __init__(self):
        super().__init__()

        self.max_speed = random.uniform(35, 40)  # mm/ms
        self.sensing_distance = random.uniform(100_000, 150_000)  # mm (100-200 meters)
        self.desired_speed = random.uniform(0.75, 0.95) * self.max_speed

        self.max_acceleration = random.uniform(0.0040, 0.0055)  # mm/ms^2 (Represents 2.5-4 m/s^2)
        self.cruise_gain = random.uniform(0.0015, 0.0020)   # 1/ms
        self.braking_comfortable = random.uniform(0.0045, 0.006) # mm/ms^2 (Represents 2-4 m/s^2, a comfortable brake)
        self.desired_time_headway = random.uniform(1000, 1200)  # ms
        self.b_max = random.uniform(0.012, 0.015)  # mm/ms^2 (Represents 8-10 m/s^2, max emergency braking)

        # These values depend on vehicle length, so they are calculated in TrafficAgent after vehicle is known
        self.smallest_follow_distance_factor = random.uniform(0.5, 1.0)
        self.desired_gap_factor = random.uniform(1.5, 2.0)

        # Lane change parameters
        self.politeness_factor = random.uniform(0.05, 0.1) # 0 is egoistic, >1 is altruistic
        self.lane_change_threshold = random.uniform(0.000001, 0.000003) # Min acceleration gain to justify a change
        self.decision_time = random.randint(150, 200)  # ms