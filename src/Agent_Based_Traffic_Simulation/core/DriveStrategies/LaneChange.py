
from ..Highway import Highway
from ..TrafficAgent import TrafficAgent
from ..DriveStrategies.AbstractLaneChange import AbstractLaneChange

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..TrafficAgent import TrafficAgent


class LaneChange(AbstractLaneChange):
    def step(self, traffic_agent: TrafficAgent):
         
         
        pass