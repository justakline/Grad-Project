import sys
import os
import json
from flask import Flask, render_template, jsonify
from flask_cors import CORS

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'Agent Based Traffic Simulation', 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'Agent Based Traffic Simulation', 'demo'))

app = Flask(__name__)
CORS(app)

simulation_model = None
simulation_type = None

# Flask web server (main entry point)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/init/<sim_type>')
def init_simulation(sim_type):
    global simulation_model, simulation_type
    
    try:
        if sim_type == 'traffic':
            from TrafficModel import TrafficModel
            from Highway import Highway
            
            highway = Highway(20_000, 100_000, False, 4, 3657)
            simulation_model = TrafficModel(50, 1, highway)
            simulation_type = 'traffic'
            return jsonify({
                'status': 'success',
                'message': 'Traffic simulation initialized',
                'x_max': simulation_model.highway.x_max,
                'y_max': simulation_model.highway.y_max
            })
            
        elif sim_type == 'demo':
            from MyModel import MyModel
            
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
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/step')
def step_simulation():
    global simulation_model, simulation_type
    
    if simulation_model is None:
        return jsonify({'status': 'error', 'message': 'No simulation initialized'}), 400
    
    try:
        simulation_model.step()
        
        agents_data = []
        for agent in simulation_model.agents:
            if simulation_type == 'traffic':
                agents_data.append({
                    'x': float(agent.vehicle.position[0]),
                    'y': float(agent.vehicle.position[1]),
                    'id': agent.unique_id
                })
            else:
                agents_data.append({
                    'x': float(agent.pos[0]),
                    'y': float(agent.pos[1]),
                    'id': agent.unique_id
                })
        
        return jsonify({
            'status': 'success',
            'agents': agents_data,
            'step': simulation_model.steps
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/reset')
def reset_simulation():
    global simulation_model, simulation_type
    simulation_model = None
    simulation_type = None
    return jsonify({'status': 'success', 'message': 'Simulation reset'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
