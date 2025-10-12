
from ..Highway import Highway
from ..Vehicle import Vehicle
from .DriveStrategy import DriveStrategy


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..TrafficAgent import TrafficAgent

class HardBrakeStrategy(DriveStrategy):
    name = "hard_brake"
    def step(self, traffic_agent: "TrafficAgent"):
        
        intensity = traffic_agent.distance_to_closest_agent / traffic_agent.safe_follow_distance_minimum
        if(intensity > 1.0):
            return
        traffic_agent.vehicle.changeVelocity(-1*intensity*traffic_agent.vehicle.acceleration)
        traffic_agent.vehicle.changePosition(traffic_agent.vehicle.velocity)
        

        pass
    
