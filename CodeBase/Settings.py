class Settings:

    def __init__(self, auto_config=False):
        if auto_config:
            # Use default settings for visualization
            self.number_of_agents = 6 # Number of agents
            self.starting_health_config = 1  # 1 = Full health, 2 = Low health, 3 = Random health, 4 = Half health
            self.max_iteration = 1000 # Number of iterations (reduced from 1000)
            self.anim_profile = 1  # 1 = High initial animosity, 2 = Low initial animosity, 3 = Random initial animosity
            self.alpha = 0.8 # Learning rate
            self.beta = 0.95 # Discount factor
            
            # Configure agent types: RL, Heuristic, or Random
            # This list defines the type of each agent by index
            # Valid values are "RL", "Heuristic", "Random"
            self.agent_types = ["RL", "Random", "RL", "Random", "Random", "Random"]
            
            # Health granularity setting
            # 1.0 = Standard health (0, 1, 2)
            # 0.1 = Fine-grained health (0, 0.1, 0.2, ..., 1.9, 2.0)
            self.health_granularity = 0.1
            
            # Maximum health value
            self.max_health = 2.0
        else:
            # Original interactive configuration
            self.number_of_agents = \
                int(input('Please enter the number of agents for the battle (> 1): \n'))

            self.starting_health_config = \
                int(input(
                     '\nPlease select the beginning health profile for the agents, input a number from (1, 2, 3, 4): \
                      \n  1. Each agent starts with full health \
                      \n  2. Each agent starts with low health \
                      \n  3. Each agent starts with random health \
                      \n  4. Half the agents start with low health and half the agents start with full health\n'))

            self.max_iteration = \
                int(input('\nPlease input the number of iterations for the Q-learning algorithm:\n'))

            self.anim_profile = \
                int(input(
                     '\nPlease select the beginning animosities profile, input a number from (1,2,3): \
                      \n  1. High initial animosity between all the agents \
                      \n  2. Low initial animosity between all the agents \
                      \n  3. Random initial animosities between all the agents\n'))

            self.alpha = \
                float(input('\nPlease input the learning rate (decimal value between 0 and 1):\n'))

            self.beta = float(input('\nPlease input the discount factor (decimal value between 0 and 1):\n'))
            
            # Default agent types for interactive mode
            self.agent_types = ["RL"] + ["Random"] * (self.number_of_agents - 1)
            
            # Default health granularity
            self.health_granularity = 1.0
            self.max_health = 2.0

        # Common settings for both auto and manual configuration
        # Combat parameters - balanced to give the RL agent a fair chance
        self.baseline_att_prob = 0.1 # Attack strength
        self.baseline_def_prob = 0.9 # Defense strength
        self.baseline_recover_prob = 0.0 # Recovery probability
        self.baseline_underattack_attack_multiplier = 1.0 # Attack multiplier when under attack
        self.baseline_notunderattack_attack_prob = 0.6 # Attack probability when not under attack
        self.attack_dead_opponent_penalty = 0.5 # Penalty for attacking dead opponents
        self.attack_alliance_member_penalty = 0.9 # Penalty for attacking alliance members
        self.propose_alliance_member_penalty = 0.9 # Penalty for proposing to alliance members
        
        # Alliance and animosity parameters
        self.animosity_decrease_prob = 0.7 # Probability of animosity reduction
        self.animosity_decrease_prob_alliance_proposal = 0.7 # Alliance proposal success rate
        self.animosity_increase_prob = 0.7 # Probability of animosity increase
        self.alliance_prob_with_some_animosity_baseline = 0.5 # Alliance probability with animosity
        self.alliance_prob_with_no_animosity = 0.8 # Alliance probability without animosity
        self.alliance_status_weight = 1.9 # Alliance status weight
        
        # Neural network hyperparameters - optimized for faster learning
        self.learning_rate = 0.001 # Learning rate for neural network
        self.target_update_frequency = 10 # Target network update frequency (increased from 5)
        self.replay_buffer_size = 5000 # Replay buffer size (reduced from 10000)
        self.batch_size = 32 # Batch size (reduced from 64)
        self.initial_epsilon = 1.0 # Initial exploration rate
        self.epsilon_decay = 0.98 # Exploration rate decay (faster decay than 0.99)
        self.min_epsilon = 0.1 # Minimum exploration rate (increased from 0.05)
        self.hidden_size = 64 # Hidden layer size (reduced from 128)

    def check_game_state(self):
        alive_agents = [agent for agent in self.env.agents_list if agent.is_alive]
        
        # If only one agent remains, they win
        if len(alive_agents) <= 1:
            self.game_is_on = False
            return
        
        # If all remaining agents are allied in pairs
        if len(alive_agents) % 2 == 0:  # Even number of agents
            all_allied = True
            for agent in alive_agents:
                if agent.alliance_pair is None or not agent.alliance_pair.is_alive:
                    all_allied = False
                    break
            
            if all_allied:
                self.game_is_on = False

    def train_rl_agents(self, agents_list, env):
        # Collect experiences from all RL agents
        all_experiences = []
        for agent in agents_list:
            if agent.agent_type == "RL":
                all_experiences.extend(agent.collect_experiences(env))
        
        # Update the shared policy using all experiences
        if Agent.shared_rl_policy is not None and all_experiences:
            Agent.shared_rl_policy.update(all_experiences)