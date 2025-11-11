import csv
import os
import datetime

class Logger:
    def __init__(self, interval_ms: int):
        """
        Parameters
        ----------
        interval_ms : int
            Desired logging interval in milliseconds.
        """

        if not os.path.exists('logs'):
            os.makedirs('logs')
        self.agent_file_name = f"logs/traffic_agent_log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        self.collsions_file_name = f"logs/collisions_log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        self.interval_ms = interval_ms
        self.last_log_time = 0

        # Create raw agent file and its columns
        with open(self.agent_file_name, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp_ms', 'agent_id', 'current_lane', 'lane_intent',
                'x_mm', 'y_mm', 'vx_mm_per_ms', 'vy_mm_per_ms',
                'ax_mm_per_ms2', 'ay_mm_per_ms2',
                'desired_speed', 'max_speed', 'drive_strategy'
            ])
        # Create raw collisions file and its columns... do not need many colums because we can cross reference with raw agent file
        with open(self.collsions_file_name, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp_ms', 'agent1_id', 'agent2_id'
            ])

    def log_all(self, model):
        self.log_collisions(model)
        self.log_agents(model)

    def log_collisions(self, model):
        """
        Log all collisions that happen ie overlap between agents

        Parameters
        ----------
        model : TrafficModel
            The running model instance.
        """
        current_time = model.total_time
        if current_time - self.last_log_time < self.interval_ms:
            return  # Not time to log yet
        with open(self.agent_file_name, 'a', newline='') as f:
            writer = csv.writer(f)
            for agent in model.agents:
                pass

    def log_agents(self, model):
        """
        Log the state of all agents if the logging interval has elapsed.

        Parameters
        ----------
        model : TrafficModel
            The running model instance.  
        """
        current_time = model.total_time
        if current_time - self.last_log_time < self.interval_ms:
            return  # Not time to log yet
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
                    type(agent.current_drive_strategy).__name__
                ])
        self.last_log_time = current_time
