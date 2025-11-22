
from ..Highway import Highway

from ..DriveStrategies.AbstractState import AbstractState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..TrafficAgent import TrafficAgent


class AbstractDriveStrategy(AbstractState):

    def step(self, traffic_agent: "TrafficAgent"):
        pass