
from ..Highway import Highway


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..TrafficAgent import TrafficAgent

class AbstractState:
    name:str = "abstractState"
    def step(self, traffic_agent: "TrafficAgent"):  
        pass