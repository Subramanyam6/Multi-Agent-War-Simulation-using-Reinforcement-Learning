#!/usr/bin/env python3
"""
Flask web application for Multi-Agent War Simulation
"""

import logging
import traceback
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check numpy availability
try:
    import numpy as np
    logger.info(f"NumPy version: {np.__version__}")
except ImportError as e:
    logger.error(f"Failed to import numpy: {str(e)}")
    logger.error(f"Python path: {sys.path}")
    logger.error(traceback.format_exc())
    raise

from flask import Flask, render_template, request, jsonify
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for generating static images
import matplotlib.pyplot as plt
import io
import base64
import os
from web_visualizer import WebSimulationVisualizer
from CodeBase.Settings import Settings
from CodeBase.Simulation import Simulation

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    """Run a simulation with the given parameters"""
    try:
        # Get parameters from request
        data = request.json
        logger.info(f"Received simulation request with parameters: {data}")
        
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
        if 'beta' in data:
            settings.beta = float(data['beta'])
        
        # Apply RL settings if provided
        if 'learning_rate' in data:
            settings.learning_rate = float(data['learning_rate'])
        if 'target_update_frequency' in data:
            settings.target_update_frequency = int(data['target_update_frequency'])
        if 'replay_buffer_size' in data:
            settings.replay_buffer_size = int(data['replay_buffer_size'])
        if 'batch_size' in data:
            settings.batch_size = int(data['batch_size'])
        if 'initial_epsilon' in data:
            settings.initial_epsilon = float(data['initial_epsilon'])
        if 'epsilon_decay' in data:
            settings.epsilon_decay = float(data['epsilon_decay'])
        if 'min_epsilon' in data:
            settings.min_epsilon = float(data['min_epsilon'])
        if 'hidden_size' in data:
            settings.hidden_size = int(data['hidden_size'])
        
        logger.info("Initializing simulation with settings")
        # Initialize simulation
        simulation = Simulation(settings)
        
        logger.info("Creating visualizer")
        # Create visualizer
        visualizer = WebSimulationVisualizer(simulation)
        
        logger.info("Generating HTML animation")
        # Get HTML animation
        html_animation = visualizer.get_html_animation()
        
        logger.info("Simulation completed successfully")
        # Return HTML animation
        return jsonify({'animation_html': html_animation})
        
    except Exception as e:
        logger.error(f"Error in run_simulation: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

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
    try:
        # Get parameters from request
        data = request.json
        logger.info(f"Received train_and_run request with parameters: {data}")
        
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
        if 'beta' in data:
            settings.beta = float(data['beta'])
        
        # Apply RL settings if provided
        if 'learning_rate' in data:
            settings.learning_rate = float(data['learning_rate'])
        if 'target_update_frequency' in data:
            settings.target_update_frequency = int(data['target_update_frequency'])
        if 'replay_buffer_size' in data:
            settings.replay_buffer_size = int(data['replay_buffer_size'])
        if 'batch_size' in data:
            settings.batch_size = int(data['batch_size'])
        if 'initial_epsilon' in data:
            settings.initial_epsilon = float(data['initial_epsilon'])
        if 'epsilon_decay' in data:
            settings.epsilon_decay = float(data['epsilon_decay'])
        if 'min_epsilon' in data:
            settings.min_epsilon = float(data['min_epsilon'])
        if 'hidden_size' in data:
            settings.hidden_size = int(data['hidden_size'])
        
        logger.info("Initializing simulation with settings")
        # Initialize simulation
        simulation = Simulation(settings)
        
        logger.info("Starting agent training")
        # Train agents
        simulation.train()
        
        logger.info("Creating visualizer for final game")
        # Create visualizer for the final game
        visualizer = WebSimulationVisualizer(simulation)
        
        logger.info("Generating HTML animation")
        # Get HTML animation
        html_animation = visualizer.get_html_animation()
        
        logger.info("Training and simulation completed successfully")
        # Return HTML animation
        return jsonify({'animation_html': html_animation})
        
    except Exception as e:
        logger.error(f"Error in train_and_run: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Gunicorn will serve the app when deployed to Render.com
if __name__ == '__main__':
    # When running locally, use debug mode
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True) 