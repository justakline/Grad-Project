import logging
class Logger:


    
    def __init__(self, file_name: str):
        self.file_name = file_name
        logging.basicConfig(filename=file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def log_all_agent_locations(self, traffic_model):
        for agent in traffic_model.agents:
            self.log_agent_location(agent)
        pass

    def log_agent_location(self, agent):
        pass