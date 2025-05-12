# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 21:27:27 2022

# Updates

2024/03/14
1. Now structured into modules
2. Added a settings file

2024/05/15
1. Made changes for best coding practices
2. Cleaned up comments

2024/06/01
1. Updated to use deep reinforcement learning with neural networks
2. Added support for Apple Silicon

@author: Bala Subramanyam Duggirala
"""
import time
import torch
import os
import sys

# Add the parent directory to the path to resolve module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Change imports to work when run directly
from CodeBase.Agent import Agent
from CodeBase.Environment import Environment
from CodeBase.GameStatusUpdate import GameStatusUpdate
from CodeBase.Simulation import Simulation
from CodeBase.Settings import Settings
        
def main():
    print('_^_ My Dear Gods: Ganeshan-Murugan _^_')
    print('Launching the program', end = "")
    time.sleep(1)
    for i in range(4):
        print('.', end = "")
        time.sleep(1)
    print('\n')
    
    # Check if Apple Silicon GPU is available
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("Using Apple Silicon GPU for neural network training")
    else:
        device = torch.device("cpu")
        print("Using CPU for neural network training")
        
    # Create models directory for saved models
    os.makedirs("models", exist_ok=True)
    os.makedirs("models_final", exist_ok=True)
    
    initialized_settings = Settings() # mix of user-input + preset. Do check the settings file!
    initializeSimulation = Simulation(initialized_settings) # initializes the simulation with the initialized settings
    initializeSimulation.run() # run the simulation

if __name__ == '__main__':
    main()
                
                
            
        
        
        
    
        
    
    

