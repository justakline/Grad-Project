import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'Agent Based Traffic Simulation', 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'Agent Based Traffic Simulation', 'demo'))

import pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'

#  # Console-based entry point (not used in web version)

def main():
    print("=" * 60)
    print("Agent Based Traffic Simulation")
    print("=" * 60)
    print("\nChoose a simulation to run:")
    print("1. Core Traffic Simulation (Highway with Vehicles)")
    print("2. Demo Simulation (Basic Agent Movement)")
    print("\nNote: This simulation uses Pygame and is designed for desktop.")
    print("In Replit, the visualization may not be visible.")
    print("=" * 60)
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == '1':
        print("\nStarting Core Traffic Simulation...")
        from TrafficModel import TrafficModel
        from Highway import Highway
        from ui import run_pygame
        
        highway = Highway(20_000, 100_000, False, 4, 3657)
        model = TrafficModel(50, 1, highway)
        print("Model initialized. Starting Pygame visualization...")
        run_pygame(model)
        
    elif choice == '2':
        print("\nStarting Demo Simulation...")
        from MyModel import MyModel
        from ui import run_pygame
        
        model = MyModel(n_agents=100)
        print("Model initialized. Starting Pygame visualization...")
        run_pygame(model)
        
    else:
        print("Invalid choice. Please run again and choose 1 or 2.")
        sys.exit(1)

if __name__ == "__main__":
    main()
