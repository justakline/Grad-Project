import numpy as np

class Lane:
    startPosition: np.array
    endPosition:np.array 
    laneWidth: float 

    def __init__(self, startPosition: np.array, endPosition:np.array, laneWidth: float) -> None: 
        self.startPosition = startPosition
        self.endPosition = endPosition
        self.laneWidth = laneWidth
