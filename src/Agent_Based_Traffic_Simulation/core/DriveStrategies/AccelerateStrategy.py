import numpy as np
from ..Utils import to_unit, change_magnitude, e
from .AbstractDriveStrategy import AbstractDriveStrategy


class AccelerateStrategy(AbstractDriveStrategy):
    name = 'accelerate'
    def step(self, traffic_agent):
        
       
        
        
        dt = traffic_agent.model.dt 
        v = traffic_agent.vehicle.velocity
        speed = float(np.linalg.norm(v))
        max_speed = float(traffic_agent.max_speed)
        acceleration_increase = traffic_agent.acceleration_increase
        lane_dir = traffic_agent.current_lane_vector()
        
        

        old_acceleration_vector = traffic_agent.vehicle.acceleration
        old_acceleration_scalar = np.linalg.norm(old_acceleration_vector)
        if(old_acceleration_scalar == 0):
            traffic_agent.vehicle.setAcceleration(lane_dir + np.array([0, acceleration_increase * dt * dt]))
            return


        old_acceleration_unit_vector  = old_acceleration_vector/old_acceleration_scalar
        new_acceleration_scalar = old_acceleration_scalar + acceleration_increase
        new_acceleration_vector = old_acceleration_unit_vector * new_acceleration_scalar



        traffic_agent.vehicle.setAcceleration(new_acceleration_vector*dt*dt)
