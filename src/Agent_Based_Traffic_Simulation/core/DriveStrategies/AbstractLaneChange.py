
from ..Highway import Highway
from ..TrafficAgent import TrafficAgent
from ..DriveStrategies.AbstractState import AbstractState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..TrafficAgent import TrafficAgent


class AbstractLaneChange(AbstractState):
    def step(self, traffic_agent: TrafficAgent):
        pass