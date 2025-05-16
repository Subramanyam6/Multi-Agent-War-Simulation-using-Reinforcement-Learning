import random
import itertools
import time
import os
import torch
from CodeBase.Environment import Environment
from CodeBase.GameStatusUpdate import GameStatusUpdate

class Simulation:
    def __init__(self, settings):
        self.game_status_update = GameStatusUpdate(settings)
        self.settings = settings
        number_of_agents = self.settings.number_of_agents

        # initializing each agent's health based on the input setting
        starting_health_config = self.settings.starting_health_config
        start_health_list = []
        if starting_health_config == 1: #full health
            for eachagent in range(number_of_agents):
                start_health_list.append(settings.max_health)
        elif starting_health_config == 2: #low health
            for eachagent in range(number_of_agents):
                start_health_list.append(settings.max_health / 2)
        elif starting_health_config == 3: #random health
            for eachagent in range(number_of_agents):
                # Generate random health with the specified granularity
                steps = int(settings.max_health / settings.health_granularity) + 1
                random_step = random.randrange(0, steps)
                random_health = random_step * settings.health_granularity
                start_health_list.append(random_health)
        elif starting_health_config == 4: #half-half
            for eachagent in range(number_of_agents):
                if eachagent < number_of_agents/2:
                    start_health_list.append(settings.max_health / 2)
                else:
                    start_health_list.append(settings.max_health)

        self.env = Environment(number_of_agents, start_health_list, self.settings)
        self.max_iteration = self.settings.max_iteration
        self.game_is_on = True
        self.max_subgames = 100  # Maximum number of subgames for training
        self.current_step = 0  # Track current time step
        
        # Initialize state history tracking for stalemate detection
        self.state_history = []
        self.stalemate_counter = 0  # Counter for detecting stalemates

    def train(self):
        """Train the agents for 100 subgames"""
        print('\n=== TRAINING PHASE ===')
        print('Agents are now training', end="")
        time.sleep(1)
        for i in range(4):
            print('.', end="")
            time.sleep(1)
        print('\n')
        
        # Count how many RL agents we have
        rl_agent_count = sum(1 for agent in self.env.agents_list if agent.agent_type == "RL")
        # Adjust number of subgames based on RL agent count and max_iteration
        if rl_agent_count > 0:
            # Scale subgames based on max_iteration - fewer iterations need more subgames
            iteration_factor = 1000 / max(100, self.settings.max_iteration)
            # But also reduce if there are multiple RL agents
            self.max_subgames = max(20, int(100 * iteration_factor / max(1, rl_agent_count)))
        else:
            # No RL agents, minimal training needed
            self.max_subgames = 10
            
        print(f"Training {rl_agent_count} RL agents for {self.max_subgames} subgames")
        
        subgame_count = 0
        
        while subgame_count < self.max_subgames:
            t = 0
            reset = False
            subgame_count += 1
            print(f"\nTraining Subgame {subgame_count}/{self.max_subgames}")
            
            while t < self.max_iteration and not reset:
                alive_list = []

                # Collect current states for all agents
                for eachagent in self.env.agents_list:
                    eachagent.current_state = eachagent.health_list + [eachagent.alliance_status]

                # choosing an action for each agent:
                for eachagent in self.env.agents_list:
                    eachagent.choose_action(t)

                # updating the dummy game's state:
                self.game_status_update.update(self.env)

                # Collect next states and rewards - only for RL agents to save computation
                for eachagent in self.env.agents_list:
                    if eachagent.agent_type == "RL":
                        eachagent.next_state = eachagent.health_list + [eachagent.alliance_status]
                        eachagent.compute_val_snext()
                        
                        # Learn from experience using neural network
                        done = not eachagent.is_alive
                        eachagent.learn(
                            eachagent.current_state,
                            eachagent.latest_action,
                            eachagent.current_reward,
                            eachagent.next_state,
                            done
                        )

                # checking how many agents are alive:
                for eachagent in self.env.agents_list:
                    if eachagent.is_alive == True:
                        alive_list.append(eachagent)

                # checking if members from only one alliance are left:
                if len(alive_list) == 2:
                    if alive_list[0].alliance_pair == alive_list[1]:
                        reset = True

                # checking if only one agent is left:
                elif len(alive_list) == 1:
                    reset = True

                # resetting to the original state if the dummy game is over:
                if reset == True:
                    self.env.health_list = list(self.env.stable_health_list)
                    self.animosity_table = list(self.env.stable_animosity_table)

                    for eachagent in self.env.agents_list:
                        eachagent.health_list = list(eachagent.stable_health_list)
                        eachagent.alliance_status = eachagent.stable_alliance_status
                        eachagent.alliance_pair = eachagent.stable_alliance_pair
                        eachagent.is_alive = eachagent.stable_is_alive

                t += 1
            
            # Only print progress every 5 subgames to reduce console output
            if subgame_count % 5 == 0 or subgame_count == self.max_subgames:
                print(f"Training progress: {subgame_count}/{self.max_subgames} subgames completed")

        print("\nTraining completed!")
        self.reset_environment()

    def play_final_game(self):
        """Play a single final game with the trained agents"""
        print('\n=== FINAL GAME ===')
        print('Starting the final game with trained agents...')
        self.game_is_on = True
        self.current_step = 0  # Reset step counter
        
        # Add a maximum iteration limit to prevent infinite loops
        max_iterations = self.max_iteration
        
        while self.game_is_on and self.current_step < max_iterations:
            self.update_time_step()
            self.current_step += 1
            
            # Check if we're in a stalemate situation
            if self.current_step >= max_iterations:
                print(f"\nTime Step {self.current_step}: Simulation reached maximum iterations without a winner.")
                print("Game appears to be in a stalemate - all agents may be in a stable state.")
                self.game_is_on = False
                
                # Save final models even in case of stalemate
                self.env.save_all_agent_models("models_final")

    def reset_environment(self):
        """Reset the environment to initial state"""
        self.env.health_list = list(self.env.stable_health_list)
        self.animosity_table = list(self.env.stable_animosity_table)
        
        for eachagent in self.env.agents_list:
            eachagent.health_list = list(eachagent.stable_health_list)
            eachagent.alliance_status = eachagent.stable_alliance_status
            eachagent.alliance_pair = eachagent.stable_alliance_pair
            eachagent.is_alive = eachagent.stable_is_alive

    def run(self):
        """Main run method that handles both training and final game"""
        # First train the agents
        self.train()
        
        # Then play the final game
        self.play_final_game()

    # executing the actions of each agent and taking the game to the next time step:
    def update_time_step(self):
        alive_list_final = []

        # refreshing environment health_list and animosity table with the original values:
        self.env.health_list = list(self.env.stable_health_list)
        self.animosity_table = list(self.env.stable_animosity_table)

        # refreshing the attributes of the agent with original values:
        for eachagent in self.env.agents_list:
            eachagent.health_list = list(eachagent.stable_health_list)
            eachagent.alliance_status = eachagent.stable_alliance_status
            eachagent.alliance_pair = eachagent.stable_alliance_pair
            eachagent.is_alive = eachagent.stable_is_alive

        # choosing action for each agent:
        for eachagent in self.env.agents_list:
            eachagent.choose_action(999999999) # agents don't choose random actions anymore since learning is complete

        # updating the game:
        self.game_status_update.update(self.env)

        # updating the environment health_list and animosity table:
        self.env.stable_health_list = list(self.env.health_list)
        self.env.stable_animosity_table = list(self.env.animosity_table)

        # updating the state indirectly by updating the health list and alliance status:
        for eachagent in self.env.agents_list:
            eachagent.stable_health_list = list(eachagent.health_list)
            eachagent.stable_alliance_status = eachagent.alliance_status
            eachagent.stable_alliance_pair = eachagent.alliance_pair
            eachagent.stable_is_alive = eachagent.is_alive

        # Check game state to see if we have a winner or all agents are allied
        self.check_game_state()
        
        # If game is already over, return
        if not self.game_is_on:
            return

        # Check for stalemate by comparing current state with history
        current_state = self._get_current_game_state()
        
        # If we have state history and current state matches the previous state
        if self.state_history and self._states_equal(current_state, self.state_history[-1]):
            self.stalemate_counter += 1
            if self.stalemate_counter >= 100:  # If state hasn't changed for 100 iterations
                print("\nDetected a stalemate: Game state hasn't changed for 100 iterations.")
                print("Ending simulation as agents appear to be in a stable equilibrium.")
                self.game_is_on = False
                return
        else:
            # Reset counter if state changed
            self.stalemate_counter = 0
            
        # Add current state to history, keep only last 10 states
        self.state_history.append(current_state)
        if len(self.state_history) > 10:
            self.state_history.pop(0)

        # If no winners yet, print current game state
        alive_list_final = [agent for agent in self.env.agents_list if agent.is_alive]
        print(f"\nTime Step {self.current_step}: {len(alive_list_final)} agents still alive")
        # List all alive agents with their health
        for agent in alive_list_final:
            print(f"Agent {agent.agent_id}: Health={agent.health_list[agent.agent_id]}, Alliance status={agent.alliance_status}")
        print("Continuing simulation...")
        
    def check_game_state(self):
        """Check if the game has ended due to a winner or all agents being allied"""
        alive_agents = [agent for agent in self.env.agents_list if agent.is_alive]
        
        # If only one agent remains, they win
        if len(alive_agents) == 1:
            self.game_is_on = False
            print(f'\nTime Step {self.current_step}: The winner is Agent - {alive_agents[0].agent_id}')
            return
            
        # If two agents remain and they're allied, they win
        elif len(alive_agents) == 2:
            if alive_agents[0].alliance_pair == alive_agents[1]:
                self.game_is_on = False
                print(f'\nTime Step {self.current_step}: The winner is the team of Agents - {alive_agents[0].agent_id} and {alive_agents[1].agent_id}')
                return
                
        # If all remaining agents are allied in pairs, end the game
        elif len(alive_agents) > 2 and len(alive_agents) % 2 == 0:  # Even number of agents
            all_allied = True
            alliance_pairs = set()
            
            for agent in alive_agents:
                # If an agent doesn't have an alliance or their ally is dead, not all are allied
                if agent.alliance_pair is None or not agent.alliance_pair.is_alive:
                    all_allied = False
                    break
                    
                # Add alliance pair to set (in sorted order to avoid duplicates)
                pair = tuple(sorted([agent.agent_id, agent.alliance_pair.agent_id]))
                alliance_pairs.add(pair)
            
            # Check if number of unique pairs matches expected number
            if all_allied and len(alliance_pairs) == len(alive_agents) // 2:
                self.game_is_on = False
                print(f'\nTime Step {self.current_step}: Game over - All remaining agents are allied in pairs')
                print("Alliance pairs:", alliance_pairs)
                return

    def _get_current_game_state(self):
        """Create a representation of the current game state for stalemate detection"""
        state = []
        for agent in self.env.agents_list:
            if agent.is_alive:
                # Include agent ID, health, alliance status, and alliance pair ID if any
                alliance_pair_id = agent.alliance_pair.agent_id if agent.alliance_pair else -1
                state.append((agent.agent_id, agent.health_list[agent.agent_id], 
                             agent.alliance_status, alliance_pair_id))
        return tuple(sorted(state))  # Sort to ensure consistent comparison
        
    def _states_equal(self, state1, state2):
        """Compare two game states to check if they're identical"""
        return state1 == state2