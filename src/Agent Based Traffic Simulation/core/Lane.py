import numpy as np

class Lane:

    def __init__(startPosition: np.array, endPosition:np,array, laneWidth: float):
        self.startPosition:np.array = startPosition
        self.endPosition:np.array = endPosition
        self.laneWidth: float = laneWidth
