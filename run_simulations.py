# run_profile.py
from src.Agent_Based_Traffic_Simulation.core.TrafficModel import TrafficModel
from src.Agent_Based_Traffic_Simulation.core.Highway import Highway
from src.Agent_Based_Traffic_Simulation.core.Logger import Logger
import cProfile, pstats



def run():
    dt =  200
    highway_length = 2_000_000
    highway_lanes = 3
    lane_size = 3_657
    n_agents = 0

    is_logging = True

    current_sim_time = 0
    total_time = 30 * 60 * 1000 # 30 mins
    

    aggressive_pct =0
    defensive_pct = 100
    truck_ratio =  0
    motorcycle_ratio = 0
    suv_ratio = 100
    percents_and_ratios = {
        'aggressive_percent': aggressive_pct,
        'defensive_percent': defensive_pct,
        'truck_ratio': truck_ratio,
        'motorcycle_ratio': motorcycle_ratio,
        'suv_ratio': suv_ratio
    }

    agent_rate = 6

    generate_agents = True
    highway_width = highway_lanes * lane_size * 1.01 # 1.01 due to index out of bounds exceptions

    

    for i in range(4,5): 
        aggressive_pct = i * 25
        defensive_pct = 100 - aggressive_pct

        percents_and_ratios = {
            'aggressive_percent': aggressive_pct,
            'defensive_percent': defensive_pct,
            'truck_ratio': truck_ratio,
            'motorcycle_ratio': motorcycle_ratio,
            'suv_ratio': suv_ratio
        }
        highway = Highway(highway_width, highway_length, highway_lanes, lane_size)
        simulation_model = TrafficModel(n_agents,1, dt, highway, generate_agents, agent_rate, percents_and_ratios)

        logger = Logger( dt, is_logging, f"logs/traffic_agent_log_a{aggressive_pct}_d{defensive_pct}.csv", f"logs/collisions_log_a{aggressive_pct}_d{defensive_pct}.csv")
        current_sim_time = 0
        while (current_sim_time < total_time):
            simulation_model.step()
            logger.log_all(simulation_model)
            current_sim_time = simulation_model.total_time
        


if __name__ == "__main__":
    cProfile.run("run()", "profile.out")
    p = pstats.Stats("profile.out")
    p.sort_stats("cumulative").print_stats(40)
