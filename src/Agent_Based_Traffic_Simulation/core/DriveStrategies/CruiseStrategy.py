
from ..Highway import Highway
from ..Vehicle import Vehicle
from .DriveStrategy import DriveStrategy


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..TrafficAgent import TrafficAgent

class CruiseStrategy(DriveStrategy):
    def step(self, traffic_agent: "TrafficAgent"):
        traffic_agent.vehicle.changePosition(traffic_agent.vehicle.velocity)
        pass