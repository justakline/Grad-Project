import random
import numpy as np
from mesa import Model
from .Highway import Highway
from .TrafficAgent import TrafficAgent
from .Personalities import DefensivePersonality, AggressivePersonality

from .VehicleTypes import AbstractVehicle, SUV, Truck,  Motorcycle



class TrafficModel(Model):
    """
    All spatial units are in millimeters; time in milliseconds.
    Agents spawn on lane CENTERS coming from Highway.lanes[*].start_position[0].
    """

    def __init__(self, n_agents: int, seed: int, dt: int, highway: Highway, is_generate_agents:bool = False, agent_rate:float = 0.0, percents_and_ratios:dict = None):
        super().__init__(seed=seed)
        self.highway = highway
        self.steps = 0
        self.dt = dt
        self.total_time = 0
        self.last_generated_agent_time = 0
        self.is_generate_agents = is_generate_agents
        self.agent_rate = agent_rate # -> Agents per second
        # self.aggressive_percent = aggressive_pct
        self.percents_and_ratios = percents_and_ratios


        # Congestion management
        self.is_in_cooldown = False
        self.cooldown_timer = 0.0
        self.initial_accelerate_time = 500 #ms
        self.last_in_lane =[None for _ in range(self.highway.lane_count)]
        
        default_velocity = random.uniform(25, 30) 
        # default_velocity = random.uniform(25, 30) 
        agent = self.create_agent(0, default_velocity)

        self.last_in_lane[0] = agent
        self.highway.place_agent(agent, tuple(agent.vehicle.position))
        self.agents.add(agent)
        self.top_agent = agent
        self.last_agent = agent

        if(n_agents == 0):
            return

        for i in range(n_agents):
            lane_intent = i % len(self.highway.lanes)

            agent = self.create_agent(lane_intent, default_velocity)
            # Spawn on lane center X
            start_position = self._find_clear_spawn(
                lane_idx=lane_intent,
                vehicle_length_mm=agent.vehicle.length,
                tries=150
            )
            if start_position is None:
                # There are no more open spots so we can not add any more into the sim
                print("removed")
                agent.remove_self()
                break

            agent.pos = tuple(start_position)
            agent.vehicle.position = start_position
            
            # Place once in the space
            self.highway.place_agent(agent, tuple(agent.vehicle.position))
            self.agents.add(agent)

        # After populating, find the actual last agent in each lane
        last_in_lane_list = []
        for lane_idx in range(self.highway.lane_count):
            agents_in_lane = [agent for agent in self.agents if agent.current_lane == lane_idx]
            if agents_in_lane:
                last_in_lane_list.append(min(agents_in_lane, key=lambda a: a.pos[1]))
            else:
                last_in_lane_list.append(None)
        self.last_in_lane = last_in_lane_list



    def step(self):
        self.agents.do("step")
        self.steps += 1
        self.total_time +=self.dt

        # Safely remove agents that have been marked for removal during the previous step
        self.remove_out_of_bounds_agents()

        if self.is_generate_agents and self.agent_rate > 0:            
            # Time in ms between agent spawns
            spawn_interval = 1000.0 / self.agent_rate
            
            # Check if it's time to try spawning a new agent
            if self.total_time >= self.last_generated_agent_time + spawn_interval:
             
                # Find a clear lane to spawn in by checking them in a random order
                available_lanes = [i for i in range(self.highway.lane_count) if i != self.last_agent.current_lane]
                self.try_to_spawn_agent(available_lanes)

        if len(self.agents) > 0:
            # Find the agent with the highest y-position value
            self.top_agent = max(self.agents, key=lambda agent: agent.pos[1])
        else:
            self.top_agent = None
    
    def remove_out_of_bounds_agents(self):
        agents_to_remove = [agent for agent in self.agents if agent.is_removed]
        for agent in agents_to_remove:
            self.highway.remove_agent(agent)
            self.agents.remove(agent)
            # Update last_in_lane if the removed agent was the last one
            if self.last_in_lane[agent.current_lane] == agent:
                self.last_in_lane[agent.current_lane] = None
                
    def choose_personality(self):
        if random.randint(0,100) < self.percents_and_ratios['aggressive_percent']  :
            return AggressivePersonality()
        return DefensivePersonality()

    def choose_vehicle_type(self, position):
        # Since truck + motorcycle + suv = 100, then i could say anything between 0 - truck is truck, anything between truck and truck + motorcylce = motorcycle
        total = float(self.percents_and_ratios['truck_ratio'] + self.percents_and_ratios['motorcycle_ratio'] + self.percents_and_ratios['suv_ratio'])
        truck_percent = self.percents_and_ratios['truck_ratio']/total
        motorcycle_percent = self.percents_and_ratios['motorcycle_ratio']/total

        random_number = random.random()
        if random_number < truck_percent :
            return Truck(position)
        if random_number < truck_percent + motorcycle_percent  :
            return Motorcycle(position)
        return SUV(position)


    def create_agent(self, lane_idx: int, new_velocity: float=0):

        lane = self.highway.lanes[lane_idx]

        position =  lane.start_position + np.array([0,100])
        # vehicle = SUV(position)
        # personality = AggressivePersonality() if random.randint(0,100) < self.aggressive_percent else DefensivePersonality()
        personality = self.choose_personality()
        vehicle = self.choose_vehicle_type(position)


        # small initial push along lane

        return TrafficAgent(
                            model=self,
                            goal=lane.end_position,
                            lane_intent=lane_idx,
                            spawn_time=self.total_time,
                            vehicle=vehicle,
                            personality=personality,
                            velocity=new_velocity
                            
                    )
   
    # def is_too_dangerous_to_spawn(self, last_agent_in_lane: TrafficAgent) -> bool:
    #     # There is no car in the lane so all good
    #     min_clear_lengths = 4
    #     if not last_agent_in_lane:
    #         return False
    #     # If last car is too close to the start, this lane is blocked.
    #     if last_agent_in_lane.vehicle.position[1] <= last_agent_in_lane.vehicle.length * min_clear_lengths:
    #         return True 
    #     # If last car is moving too slowly, this lane is blocked.
    #     if np.linalg.norm(last_agent_in_lane.vehicle.velocity) <= last_agent_in_lane.desired_speed * 0.3:
    #         return True  # Try next lane
    #     if(self.is_collision_ahead(last_agent_in_lane)):
    #         return True 
    #     return False
    def is_too_dangerous_to_spawn(self, last_agent_in_lane: TrafficAgent) -> bool:
        """
        Light gate: we only block if the last agent is extremely close to the start
        OR almost stopped and very close, which would cause immediate overlap.
        Otherwise we allow spawning downstream via _find_clear_spawn_scan.
        """
        if not last_agent_in_lane:
            return False

        min_clear_lengths = 2.0   # reduced from 4 to improve throughput
        near_start_limit = last_agent_in_lane.vehicle.length * min_clear_lengths
        if last_agent_in_lane.vehicle.position[1] <= near_start_limit:
            # too close to the entrance; try downstream instead
            return True

        # consider velocity relative to desired_speed if available
        v = float(np.linalg.norm(last_agent_in_lane.vehicle.velocity))
        desired = getattr(last_agent_in_lane, "desired_speed", 30.0)  # mm/ms fallback
        # if crawling and still very near the start, block
        if v <= desired * 0.15 and last_agent_in_lane.vehicle.position[1] <= near_start_limit * 1.2:
            return True

        return False



    def try_to_spawn_agent(self, available_lanes:list[int]):
        random.shuffle(available_lanes)
                
        for lane_idx in available_lanes:
            last_agent_in_lane = self.last_in_lane[lane_idx]

            if self.is_too_dangerous_to_spawn(last_agent_in_lane):
                continue
            
            # This lane is clear for spawning.
            new_velocity = random.uniform(25, 30)
            if last_agent_in_lane:
                # Set velocity relative to the car that was last in this lane for smoother flow
                new_velocity = np.linalg.norm(last_agent_in_lane.vehicle.velocity) * 0.85

            agent = self.create_agent(lane_idx, new_velocity)

            # Make sure they are slowing down if the agent in fron is slowing down
            if(last_agent_in_lane):
                agent.assign_strategy(type(last_agent_in_lane.current_drive_strategy))
            self.last_in_lane[lane_idx] = agent
            self.highway.place_agent(agent, tuple(agent.vehicle.position))
            self.agents.add(agent)
            self.last_generated_agent_time = self.total_time
            self.last_agent = agent

            break # Exit the loop since we successfully spawned an agent.

    def is_collision_ahead(self, agent: TrafficAgent) -> bool:
        """
        Checks if any pair of agents in the local vicinity of the given 'agent'
        is currently colliding.
        """
        # Get all agents in the local area, including the reference agent.
        local_agents = self.highway.get_neighbors(agent.pos, agent.vehicle.length * 12, include_center=True)
        local_agents = [a for a in local_agents if a.current_lane == agent.current_lane or a.lane_intent == agent.lane_intent]

        if len(local_agents) < 2:
            return False  # Not enough agents to have a collision.

        num_agents = len(local_agents)
        # Check every unique pair of agents for a potential collision.
        for i in range(num_agents):
            for j in range(i + 1, num_agents):
                if(self.is_collision(local_agents[i], local_agents[j])):
                   return True
        return False  # No collisions detected among any pair.

    def is_collision(self, agent_a, agent_b):
        """
        Checks if two rectangular vehicles (agent_a, agent_b) collide.
        Handles rotated rectangles using Separating Axis Theorem (SAT). AI Generateed, I dont understand this
        """
        # Get positions (centers)
        pos_a = np.array(agent_a.vehicle.position, dtype=float)
        pos_b = np.array(agent_b.vehicle.position, dtype=float)

        # Dimensions
        half_w_a, half_l_a = agent_a.vehicle.width / 2, agent_a.vehicle.length / 2
        half_w_b, half_l_b = agent_b.vehicle.width / 2, agent_b.vehicle.length / 2

        # Get orientation vectors (unit)
        vel_a = agent_a.vehicle.velocity
        vel_b = agent_b.vehicle.velocity

        def direction_from_velocity(vel, default=np.array([0, 1])):
            """Return a normalized direction vector; fall back to straight if stopped."""
            norm = np.linalg.norm(vel)
            if norm < 1e-6:
                return default
            return vel / norm

        forward_a = direction_from_velocity(vel_a)
        forward_b = direction_from_velocity(vel_b)

        # Perpendicular (right) vectors
        right_a = np.array([-forward_a[1], forward_a[0]])
        right_b = np.array([-forward_b[1], forward_b[0]])

        # Construct corners of both rectangles (center ± forward/right)
        def get_corners(center, fwd, right, half_l, half_w):
            return np.array([
                center + fwd * half_l + right * half_w,
                center + fwd * half_l - right * half_w,
                center - fwd * half_l - right * half_w,
                center - fwd * half_l + right * half_w
            ])

        corners_a = get_corners(pos_a, forward_a, right_a, half_l_a, half_w_a)
        corners_b = get_corners(pos_b, forward_b, right_b, half_l_b, half_w_b)

        # --- Separating Axis Theorem (SAT) ---
        # Projection axes are rectangle normals
        axes = [forward_a, right_a, forward_b, right_b]

        def project(points, axis):
            """Project corners onto an axis and return min, max."""
            dots = np.dot(points, axis)
            return np.min(dots), np.max(dots)

        for axis in axes:
            min_a, max_a = project(corners_a, axis)
            min_b, max_b = project(corners_b, axis)
            # Check for separation
            if max_a < min_b or max_b < min_a:
                return False  # Separated along this axis → no collision

        return True  # No separating axis found → collision

    def _find_clear_spawn(self, lane_idx: int, vehicle_length_mm: float, tries: int = 50):
        """
        Pick a start position on lane `lane_idx` with no nearby agents.
        Uses Mesa get_neighbors so we avoid overlaps at t=0.
        """
        lane = self.highway.lanes[lane_idx]
        x_center = float(lane.start_position[0])  # lane center X

        # At least one car length worth of spacing, with a small buffer
        spawn_radius_mm: float = float(vehicle_length_mm) * 1.2

        # Keep a small vertical margin so spawns are not right at the bounds
        top_margin = 500.0
        bottom_margin = 500.0
        y_min = top_margin
        y_max = float(self.highway.y_max) - bottom_margin

        for _ in range(tries):
            y = random.uniform(y_min, y_max)
            pos = np.array([x_center, y], dtype=float)
            if len(self.agents) == 0:
                return pos
            # Get the neighbors that are in the same lane
            neighbors:list = list(filter( lambda a: a.lane_intent == lane_idx,self.highway.get_neighbors(tuple(pos), spawn_radius_mm, False)))
            if  len(neighbors) ==0 :
                return pos

        return None  # could not find a clear spot
        
