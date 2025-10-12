
from ..Highway import Highway
from ..TrafficAgent import TrafficAgent

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..TrafficAgent import TrafficAgent

class DriveStrategy():
    name = "drive"
    def step(self, traffic_agent: TrafficAgent):
        pass