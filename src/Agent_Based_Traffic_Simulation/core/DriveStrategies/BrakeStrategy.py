# BrakeStrategy.py
import numpy as np

from .AbstractDriveStrategy import AbstractDriveStrategy

class BrakeStrategy(AbstractDriveStrategy):
    name = "brake"

    def step(self, traffic_agent):
        import numpy

        # Speeds (mm/ms)
        other = traffic_agent.lead
        vehicle_speed = float(numpy.linalg.norm(traffic_agent.vehicle.velocity))
        leader_speed = float(numpy.linalg.norm(other.vehicle.velocity))
        closing_speed = vehicle_speed - leader_speed  # > 0 means we are faster

        # Distances and timing (mm, ms)
        gap_distance = float(traffic_agent.gap_to_lead)
        minimum_follow_distance = float(traffic_agent.smallest_follow_distance)
        hard_brake_distance_start = float(traffic_agent.hard_brake_distance_start)
        dt = float(traffic_agent.model.dt)

        # Check for if we've accidentally gone to close, so change the acceleration to 
        # make it slower thant the car in front of me



        #Rendevous formula -> a1 = a2 - [ (mag(v2-v1)^2)/ (2* ((p2-p1) dot (v2-v1)) )] dot (v2-v1)

        # Comments about the formula ################
        # the positions need to be in terms of the gap and the front/back of each car.
        # so we can use p1's front bumper position as it's position
        # and we can use p2's back bumper position - minimum follow distance to be p2
        v1 = traffic_agent.vehicle.velocity
        v2 = other.vehicle.velocity
        v_diff = v2-v1

        p1 = traffic_agent.vehicle.position + np.array([0, traffic_agent.vehicle.length/2])
        p2 = other.vehicle.position - np.array([0, other.vehicle.length/2]) - np.array([0,minimum_follow_distance])
        p_diff = p2-p1
        a1 = traffic_agent.vehicle.acceleration
        a2 = other.vehicle.acceleration
        small_value = 0.0001
        
        # We are in the gap so rendevous does not work
        if(np.linalg.norm(p_diff) < minimum_follow_distance ):
            traffic_agent.vehicle.velocity = np.array([0,0])
            return
        denominator = (2 * np.dot(p_diff, v_diff))
        

        # Division by 0 blocked
        if(denominator > -1 * small_value and denominator < small_value):
            traffic_agent.vehicle.setAcceleration(np.array([0,0]))
            return
        
        new_a = (np.linalg.norm(v_diff) ** 2) / denominator

        if(new_a > 0 ):
            traffic_agent.vehicle.setAcceleration(np.array([0,0]))
            return
        
        new_a = a2 - new_a * v_diff
        traffic_agent.vehicle.setAcceleration(new_a)




