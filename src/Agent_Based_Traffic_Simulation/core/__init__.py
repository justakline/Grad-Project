from .TrafficModel import TrafficModel
from .Highway import Highway
from .ui import run_pygame

if __name__ == "__main__":
    highway = Highway(20_000, 100_000, False,4, 3657 )
    model = TrafficModel(50, 1, highway)  # reduced count so text is readable
    run_pygame(model)