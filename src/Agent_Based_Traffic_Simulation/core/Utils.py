


import numpy as np

e = 1e-9
def to_unit(vector: np.array) -> np.array:
    if vector is None:
        return None
    magnitude = np.linalg.norm(vector)

    # No divide by 0
    if magnitude < e:
        return None
    return vector/magnitude

def change_magnitude(vector: np.array, scalar: float) -> np.array:
    unit = to_unit(vector)
    # default to straight up
    if(unit is None):
        return np.array([0.0, 1.0])
    return unit*scalar