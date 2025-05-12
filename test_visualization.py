#!/usr/bin/env python3
"""
Test script for the Multi-Agent War Simulation web visualization
"""

from CodeBase.Settings import Settings
from CodeBase.Simulation import Simulation
from web_visualizer import WebSimulationVisualizer
import matplotlib.pyplot as plt

def test_static_visualization():
    """Test static visualization"""
    print("Testing static visualization...")
    
    # Initialize settings with auto-configuration
    settings = Settings(auto_config=True)
    
    # Initialize simulation
    simulation = Simulation(settings)
    
    # Create visualizer
    visualizer = WebSimulationVisualizer(simulation)
    
    # Run a few steps to get interesting state
    for _ in range(5):
        if simulation.game_is_on:
            simulation.update_time_step()
    
    # Update the plot
    visualizer.update_plot(0)
    
    # Save figure to file
    visualizer.fig.savefig('test_visualization.png', dpi=100, bbox_inches='tight')
    print("Static visualization saved to test_visualization.png")

def test_animation():
    """Test animation generation"""
    print("Testing animation generation...")
    
    # Initialize settings with auto-configuration
    settings = Settings(auto_config=True)
    settings.max_iteration = 20  # Reduce iterations for testing
    
    # Initialize simulation
    simulation = Simulation(settings)
    
    # Create visualizer
    visualizer = WebSimulationVisualizer(simulation)
    
    # Save animation to file
    visualizer.save_animation('test_animation.mp4')
    print("Animation saved to test_animation.mp4")

if __name__ == '__main__':
    test_static_visualization()
    # Uncomment to test animation (requires ffmpeg)
    # test_animation() 