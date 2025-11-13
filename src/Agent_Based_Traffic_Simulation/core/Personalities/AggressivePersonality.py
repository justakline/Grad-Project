import random
from .AbstractPersonality import AbstractPersonality


class AggressivePersonality(AbstractPersonality):
    def __init__(self):
        super().__init__()

        self.max_speed = random.uniform(35, 40)  # mm/ms
        self.sensing_distance = random.uniform(120_000, 160_000)  # mm (100-200 meters)
        self.desired_speed = random.uniform(0.75, 0.95) * self.max_speed

        self.max_acceleration = random.uniform(0.0022, 0.0030)  # mm/ms^2 (Represents 2.5-4 m/s^2)
        self.cruise_gain = random.uniform(0.0008, 0.0060)   # 1/ms
        self.braking_comfortable = random.uniform(0.0035, 0.0050) # mm/ms^2 (Represents 2-4 m/s^2, a comfortable brake)
        self.desired_time_headway = random.uniform(1000, 1200)  # ms
        self.b_max = random.uniform(0.009, 0.013)  # mm/ms^2 (Represents 8-10 m/s^2, max emergency braking)

        # These values depend on vehicle length, so they are calculated in TrafficAgent after vehicle is known
        self.smallest_follow_distance_factor = random.uniform(0.8, 1.3)
        self.desired_gap_factor = random.uniform(2.0, 3.0)

        # Lane change parameters
        self.politeness_factor = random.uniform(0.0, 0.3) # 0 is egoistic, >1 is altruistic
        self.lane_change_threshold = random.uniform(0.00005, 0.00008) # Min acceleration gain to justify a change
        self.decision_time = random.randint(60, 120)  # ms