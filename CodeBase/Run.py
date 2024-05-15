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

@author: Bala Subramanyam Duggirala
"""
import time
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
    initialized_settings = Settings() # mix of user-input + preset. Do check the settings file!
    initializeSimulation = Simulation(initialized_settings) # initializes the simulation with the initialized settings
    initializeSimulation.run() # run the simulation

if __name__ == '__main__':
    main()
                
                
            
        
        
        
    
        
    
    

