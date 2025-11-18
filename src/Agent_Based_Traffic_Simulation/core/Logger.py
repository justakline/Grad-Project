import csv
import os
import datetime

from .TrafficModel import TrafficModel

class Logger:
    def __init__(self, interval_ms: int, is_logging: bool = True, agent_log_name: str = None, collisions_log_name: str = None):
        """
        Parameters
        ----------
        interval_ms : int
            Desired logging interval in milliseconds.
        """

        if not os.path.exists('logs'):
            os.makedirs('logs')
        self.agent_file_name = f"logs/traffic_agent_log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv" if not agent_log_name else agent_log_name
        self.collsions_file_name = f"logs/collisions_log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv" if not collisions_log_name else collisions_log_name
        self.interval_ms = interval_ms
        self.last_log_time = 0
        self.is_logging = is_logging
        self.is_files_created = False

        
 
    def log_all(self, model):

        if(not self.is_logging):
            return
        
        if(not self.is_files_created):
            self.create_files()
            self.is_files_created = True

        current_time = model.total_time
        if current_time - self.last_log_time < self.interval_ms:
            return  # Not time to log yet
        self.log_collisions(model, current_time)
        self.log_agents(model, current_time)
        self.last_log_time = current_time

    def log_collisions(self, model:TrafficModel, current_time):
        """
        Log all collisions that happen ie overlap between agents

        Parameters
        ----------
        model : TrafficModel
            The running model instance.
        """
        with open(self.collsions_file_name, 'a', newline='') as f:
            writer = csv.writer(f)
            collisions:set[tuple[int,int]] = set()
            # Get the neighbors for each agent within their length (length is always bigger than width)
            # Then check for overlap
            for agent in model.agents:
                neighbors = model.highway.get_neighbors(agent.pos, agent.vehicle.length * 3, include_center=False)
                if (len(neighbors) == 0):
                    continue
                for neighbor in neighbors:
                    if(model.is_collision(agent, neighbor)):
                        collisions.add(tuple(sorted((agent.unique_id, neighbor.unique_id))))

            for collision in collisions:
                writer.writerow([current_time,collision[0], collision[1]])
                    

    def log_agents(self, model: TrafficModel, current_time):
        """
        Log the state of all agents if the logging interval has elapsed.

        Parameters
        ----------
        model : TrafficModel
            The running model instance.  
        """
        with open(self.agent_file_name, 'a', newline='') as f:
            writer = csv.writer(f)
            for agent in model.agents:
                # Use the Mesa-provided unique_id when available; otherwise fall back
                # to Python’s built‑in id()
                agent_id = getattr(agent, 'unique_id', None)
                if agent_id is None:
                    agent_id = id(agent)
                pos = agent.vehicle.position
                vel = agent.vehicle.velocity
                acc = agent.vehicle.acceleration
                writer.writerow([
                    current_time,              # timestamp in ms
                    agent_id,
                    agent.current_lane,
                    agent.lane_intent,
                    float(pos[0]), float(pos[1]),
                    float(vel[0]), float(vel[1]),
                    float(acc[0]), float(acc[1]),
                    agent.desired_speed,
                    agent.max_speed,
                    type(agent.current_drive_strategy).__name__,
                    type(agent.vehicle).__name__
                ])

    def create_files(self):
        # Create raw agent file and its columns
        with open(self.agent_file_name, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp_ms', 'agent_id', 'current_lane', 'lane_intent',
                'x_mm', 'y_mm', 'vx_mm_per_ms', 'vy_mm_per_ms',
                'ax_mm_per_ms2', 'ay_mm_per_ms2',
                'desired_speed', 'max_speed', 'drive_strategy', 'vehicle_type'
            ])
        # Create raw collisions file and its columns... do not need many colums because we can cross reference with raw agent file
        with open(self.collsions_file_name, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp_ms', 'agent1_id', 'agent2_id'
            ])
