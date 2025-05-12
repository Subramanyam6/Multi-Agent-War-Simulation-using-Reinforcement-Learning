#!/usr/bin/env python3
"""
Simplified Flask web application for Multi-Agent War Simulation
Uses static images instead of animations
"""

from flask import Flask, render_template, request, jsonify
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for generating static images
import matplotlib.pyplot as plt
import io
import base64
import time
import json
from web_visualizer import WebSimulationVisualizer
from CodeBase.Settings import Settings
from CodeBase.Simulation import Simulation

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index_simple.html')

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    """Run a simulation with the given parameters and return frames as images"""
    # Get parameters from request
    data = request.json
    
    # Set up settings
    settings = Settings(auto_config=True)
    
    # Override settings with user input if provided
    if 'num_agents' in data:
        settings.number_of_agents = int(data['num_agents'])
    if 'max_iteration' in data:
        settings.max_iteration = int(data['max_iteration'])
    if 'agent_types' in data:
        settings.agent_types = data['agent_types']
    if 'health_config' in data:
        settings.starting_health_config = int(data['health_config'])
    if 'anim_profile' in data:
        settings.anim_profile = int(data['anim_profile'])
    if 'alpha' in data:
        settings.alpha = float(data['alpha'])
    if 'beta' in data:
        settings.beta = float(data['beta'])
    
    # Limit max frames to prevent overloading the browser
    max_frames = min(50, settings.max_iteration)
    
    # Initialize simulation
    simulation = Simulation(settings)
    
    # Create visualizer
    visualizer = WebSimulationVisualizer(simulation)
    
    # Generate frames
    frames = []
    for i in range(max_frames):
        if not simulation.game_is_on:
            break
        
        # Update simulation and plot
        visualizer.update_plot(i)
        
        # Save figure to bytes
        buf = io.BytesIO()
        visualizer.fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        
        # Encode image to base64
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        frames.append(f'data:image/png;base64,{img_str}')
        
        # Add delay to prevent browser from freezing
        time.sleep(0.01)
    
    # Return frames
    return jsonify({'frames': frames, 'game_over': not simulation.game_is_on})

@app.route('/static_image', methods=['POST'])
def static_image():
    """Generate a static image of the simulation state"""
    # Get parameters from request
    data = request.json
    
    # Set up settings
    settings = Settings(auto_config=True)
    
    # Override settings with user input if provided
    if 'num_agents' in data:
        settings.number_of_agents = int(data['num_agents'])
    if 'agent_types' in data:
        settings.agent_types = data['agent_types']
    
    # Initialize simulation
    simulation = Simulation(settings)
    
    # Create visualizer
    visualizer = WebSimulationVisualizer(simulation)
    
    # Run a few steps to get interesting state
    for _ in range(min(5, settings.max_iteration)):
        if simulation.game_is_on:
            simulation.update_time_step()
    
    # Update the plot
    visualizer.update_plot(0)
    
    # Save figure to bytes
    buf = io.BytesIO()
    visualizer.fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    
    # Encode image to base64
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    
    # Return image as base64 string
    return jsonify({'image': f'data:image/png;base64,{img_str}'})

@app.route('/train_and_run', methods=['POST'])
def train_and_run():
    """Train agents and run a full simulation"""
    # Get parameters from request
    data = request.json
    
    # Set up settings
    settings = Settings(auto_config=True)
    
    # Override settings with user input if provided
    if 'num_agents' in data:
        settings.number_of_agents = int(data['num_agents'])
    if 'max_iteration' in data:
        settings.max_iteration = int(data['max_iteration'])
    if 'agent_types' in data:
        settings.agent_types = data['agent_types']
    if 'health_config' in data:
        settings.starting_health_config = int(data['health_config'])
    if 'anim_profile' in data:
        settings.anim_profile = int(data['anim_profile'])
    if 'alpha' in data:
        settings.alpha = float(data['alpha'])
    if 'beta' in data:
        settings.beta = float(data['beta'])
    
    # Limit max frames to prevent overloading the browser
    max_frames = min(50, settings.max_iteration)
    
    # Initialize simulation
    simulation = Simulation(settings)
    
    # Train agents
    simulation.train()
    
    # Create visualizer for the final game
    visualizer = WebSimulationVisualizer(simulation)
    
    # Generate frames
    frames = []
    for i in range(max_frames):
        if not simulation.game_is_on:
            break
        
        # Update simulation and plot
        visualizer.update_plot(i)
        
        # Save figure to bytes
        buf = io.BytesIO()
        visualizer.fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        
        # Encode image to base64
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        frames.append(f'data:image/png;base64,{img_str}')
        
        # Add delay to prevent browser from freezing
        time.sleep(0.01)
    
    # Return frames
    return jsonify({'frames': frames, 'game_over': not simulation.game_is_on})

if __name__ == '__main__':
    app.run(debug=True, port=5001) 