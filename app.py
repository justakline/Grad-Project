import sys
import os
import json
import math
import warnings
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import traceback

import numpy as np
import logging
logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger("werkzeug").disabled = True

# Make project modules importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'Agent Based Traffic Simulation', 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'Agent Based Traffic Simulation', 'demo'))

app = Flask(__name__)
CORS(app)
warnings.filterwarnings("ignore", category=UserWarning)

simulation_model = None
simulation_type = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/init/<sim_type>')
def init_simulation(sim_type):
    global simulation_model, simulation_type
    try:
        if sim_type == 'traffic':
            from src.Agent_Based_Traffic_Simulation.core.TrafficModel import TrafficModel
            from src.Agent_Based_Traffic_Simulation.core.Highway import Highway

            highway_length = 200_000
            highway_lanes = 2
            lane_size = 3657
            highway_width = highway_lanes * lane_size * 1.01 # 1.01 due to index out of bounds exceptions
            dt = 20 #ms
            
            # Highway units are millimeters
            highway = Highway(highway_width, highway_length, True, highway_lanes, lane_size)
            simulation_model = TrafficModel(40,1, dt, highway)
            simulation_type = 'traffic'
            return jsonify({
                'status': 'success',
                'message': 'Traffic simulation initialized',
                'x_max': simulation_model.highway.x_max,
                'y_max': simulation_model.highway.y_max,
                # send lane count and width in case you want to draw lanes later
                'lane_count': len(simulation_model.highway.lanes),
                'lane_width': int(simulation_model.highway.lanes[0].lane_width) if simulation_model.highway.lanes else None,
                    'lane_centers': [int(l.start_position[0]) for l in simulation_model.highway.lanes]
            })

        elif sim_type == 'demo':
            from src.Agent_Based_Traffic_Simulation.demo.MyModel import MyModel
            simulation_model = MyModel(n_agents=100)
            simulation_type = 'demo'
            return jsonify({
                'status': 'success',
                'message': 'Demo simulation initialized',
                'x_max': simulation_model.x_max,
                'y_max': simulation_model.y_max
            })
        else:
            return jsonify({'status': 'error', 'message': 'Invalid simulation type'}), 400

    except Exception:
        print("Exception in /api/init:\n" + traceback.format_exc())
        return jsonify({'status': 'error', 'message': 'Initialization failed'}), 500

@app.route('/api/step')
def step_simulation():
    global simulation_model, simulation_type
    if simulation_model is None:
        return jsonify({'status': 'error', 'message': 'No simulation initialized'}), 400

    try:
        simulation_model.step()

        agents_data = []
        aggregate_data = []
        avg_speed = 0
        for agent in simulation_model.agents:
            if simulation_type == 'traffic':
                # Real-world values straight from the model (mm, mm/ms)
                x = float(agent.vehicle.position[0])
                y = float(agent.vehicle.position[1])
                vx = float(agent.vehicle.velocity[0])
                vy = float(agent.vehicle.velocity[1])
                speed = np.linalg.norm(agent.vehicle.velocity)
                length_mm = float(agent.vehicle.length)  # already mm
                width_mm = float(agent.vehicle.width)    # already mm
                # Heading in radians from velocity; fall back to lane direction if stopped
                if speed > 0:
                    heading = math.atan2(vy, vx)
                else:
                    lane = simulation_model.highway.lanes[agent.lane_intent]
                    dx, dy = (lane.end_position - lane.start_position)
                    heading = math.atan2(float(dy), float(dx))
                dt = simulation_model.dt
                agents_data.append({
                    'id': agent.unique_id,
                    'x': x,                # mm
                    'y': y,                # mm
                    'vx': vx,              # mm/ms
                    'vy': vy,              # mm/ms
                    'speed': speed,        # mm/ms
                    'length': length_mm,   # mm
                    'width': width_mm,     # mm
                    'heading': heading,    # radians
                    'drive_strategy': getattr(agent.current_drive_strategy, "name", "unknown"),
                    'sensing_distance':  getattr(agent, "sensing_distance", "unknown"),
                })
                avg_speed += speed
            else:
                agents_data.append({
                    'id': agent.unique_id,
                    'x': float(agent.pos[0]),
                    'y': float(agent.pos[1])
                })
        avg_speed /= len(simulation_model.agents)
        avg_speed *= 2.23694   #convert to miles per hour
        total_time = simulation_model.total_time / 1000 #convert to seconds
        aggregate_data.append({
            'avg_speed': round(float(avg_speed), 2),
            'time_elapsed' : round(float(total_time) , 2)
        })

        return jsonify({
            'status': 'success',
            'agents': agents_data,
            'aggregateData': aggregate_data,
            'step': simulation_model.steps
        })

    except Exception:
        print("Exception in /api/step:\n" + traceback.format_exc())
        return jsonify({'status': 'error', 'message': 'Step failed'}), 500

@app.route('/api/reset')
def reset_simulation():
    global simulation_model, simulation_type
    simulation_model = None
    simulation_type = None
    return jsonify({'status': 'success', 'message': 'Simulation reset'})

if __name__ == '__main__':
    # debug=False to avoid double-running model (Flask reloader)
    app.run(host='0.0.0.0', port=5000, debug=False)
