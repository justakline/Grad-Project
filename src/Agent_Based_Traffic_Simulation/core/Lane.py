import numpy as np

class Lane:

    # All units will be in millimeters
    def __init__(self, start_position: np.array, end_position:np.array, lane_width: int):
        self.start_position:np.array = start_position
        self.end_position:np.array = end_position
        self.lane_width:int = lane_width

    