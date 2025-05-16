import random
import torch
import numpy as np
from CodeBase.DQNModel import AgentNetwork, ReplayBuffer

# Define agent types as constants
AGENT_TYPE_RL = "RL"
AGENT_TYPE_HEURISTIC = "Heuristic"
AGENT_TYPE_RANDOM = "Random"

class Agent:
    # Class-level variables for shared RL policy
    shared_policy_net = None
    shared_target_net = None
    shared_optimizer = None
    shared_memory = None
    shared_update_counter = 0

    def __init__(self, agent_id, number_of_agents, health_list, settings, agent_type=None):
        self.number_of_agents = number_of_agents
        self.agent_id = agent_id
        self.health_list = list(health_list) # this is reset over training loops
        self.stable_health_list = list(health_list) #this is the actual game-variable
        self.actions = self.create_actions(agent_id, number_of_agents)
        self.latest_action = None
        self.alliance_status = 1  # this is 1 by default, will change to 1.5 with alliance formations
        self.stable_alliance_status = 1
        self.proposal_request = None
        self.alliance_pair = None  # this agent object is updated as per alliance formation/breakups
        self.stable_alliance_pair = None
        self.is_alive = True
        self.stable_is_alive = True
        
        # Neural network parameters
        self.settings = settings
        self.state_size = len(health_list) + 1  # health list + alliance status
        self.action_size = number_of_agents * 3 + 2  # Same action space as original
        
        # Check if MPS (Metal Performance Shaders) is available for Apple Silicon
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        
        # Determine agent type based on settings or parameter
        if agent_type is None:
            # Use the agent_types list from settings if available
            if hasattr(settings, 'agent_types') and agent_id < len(settings.agent_types):
                self.agent_type = settings.agent_types[agent_id]
            else:
                # Default to RL for agent 0, random for others (backward compatibility)
                self.agent_type = AGENT_TYPE_RL if agent_id == 0 else AGENT_TYPE_RANDOM
        else:
            self.agent_type = agent_type
            
        # Set up RL components if this is an RL agent
        self.uses_rl = (self.agent_type == AGENT_TYPE_RL)
        
        if self.uses_rl:
            # Initialize shared policy networks if they don't exist yet
            if Agent.shared_policy_net is None:
                print(f"Agent {agent_id}: Initializing shared RL policy network")
                Agent.shared_policy_net = AgentNetwork(self.state_size, settings.hidden_size, self.action_size).to(self.device)
                Agent.shared_target_net = AgentNetwork(self.state_size, settings.hidden_size, self.action_size).to(self.device)
                Agent.shared_target_net.load_state_dict(Agent.shared_policy_net.state_dict())
                
                # Use alpha for learning rate if it's meant for RL learning
                learning_rate = settings.alpha if settings.alpha >= 0.001 else settings.learning_rate
                Agent.shared_optimizer = torch.optim.Adam(Agent.shared_policy_net.parameters(), lr=learning_rate)
                Agent.shared_memory = ReplayBuffer(settings.replay_buffer_size)
            
            # All RL agents use the shared networks
            self.policy_net = Agent.shared_policy_net
            self.target_net = Agent.shared_target_net
            self.optimizer = Agent.shared_optimizer
            self.memory = Agent.shared_memory
        
        # Exploration parameters
        self.epsilon = settings.initial_epsilon
        self.epsilon_decay = settings.epsilon_decay
        self.min_epsilon = settings.min_epsilon
        
        # For tracking learning progress
        self.current_state = None
        self.next_state = None
        self.current_reward = 0
        
        # Compatibility with original code
        self.Q_table = []  # Kept for compatibility but not used
        self.s_index = None  # Kept for compatibility but not used
        self.snext_index = None  # Kept for compatibility but not used
        self.val_snext = 0

    def create_actions(self, agent_id, number_of_agents):
        acts = []
        # n_attacks + n_alliances + defend + recover + n_accept_alliances
        for act in range(0, number_of_agents + number_of_agents + 1 + 1 + number_of_agents):
            acts.append(act)
        acts.remove(agent_id)  # removing agent's self-attack
        acts.remove(agent_id + number_of_agents)  # removing agent's self-alliance
        acts.remove(2 * number_of_agents + 2 + agent_id)  # removing agent's self-acceptance
        return acts
    
    def state_to_tensor(self, state):
        """Convert state list to tensor for neural network input"""
        return torch.FloatTensor(state).to(self.device)

    def choose_action_heuristic(self):
        """Choose action using a heuristic strategy"""
        if not self.is_alive:
            return self.agent_id
            
        # Current state
        self.current_state = self.health_list + [self.alliance_status]
        
        # Simple heuristic strategy:
        # 1. If health is low (≤ 1), try to recover
        # 2. If there's a weak opponent (health = 1), attack them
        # 3. If there's a strong opponent (health = 2), try to form alliance
        # 4. Otherwise defend
        
        my_health = self.health_list[self.agent_id]
        
        # If health is low, try to recover
        if my_health <= 1:
            return 2 * self.number_of_agents + 1  # Recover action
            
        # Find weakest opponent to attack
        min_health = float('inf')
        weakest_opponent = None
        
        for i in range(len(self.health_list)):
            if i != self.agent_id and self.health_list[i] > 0:  # Skip self and dead agents
                # Don't attack alliance partner
                if self.alliance_pair is not None and i == self.alliance_pair.agent_id:
                    continue
                    
                if self.health_list[i] < min_health:
                    min_health = self.health_list[i]
                    weakest_opponent = i
        
        # If found a weak opponent, attack them
        if weakest_opponent is not None and min_health <= 1:
            return weakest_opponent  # Attack action
            
        # Try to form alliance with strongest agent
        max_health = 0
        strongest_agent = None
        
        for i in range(len(self.health_list)):
            if i != self.agent_id and self.health_list[i] > 0:  # Skip self and dead agents
                if self.health_list[i] > max_health:
                    max_health = self.health_list[i]
                    strongest_agent = i
                    
        # If found a strong agent and don't already have an alliance, propose alliance
        if strongest_agent is not None and self.alliance_pair is None:
            return strongest_agent + self.number_of_agents  # Alliance proposal action
            
        # Default: defend
        return 2 * self.number_of_agents  # Defend action

    def choose_action(self, t):  # t is a time-step until which agents choose random actions
        chosen_action = self.agent_id
        if self.is_alive == True:
            # Current state is health list + alliance status
            self.current_state = self.health_list + [self.alliance_status]
            
            # Choose action based on agent type
            if self.agent_type == AGENT_TYPE_RANDOM:
                # Random agent always chooses randomly
                chosen_action = random.choice(self.actions)
                
            elif self.agent_type == AGENT_TYPE_HEURISTIC:
                # Heuristic agent uses rule-based strategy
                chosen_action = self.choose_action_heuristic()
                
            elif self.agent_type == AGENT_TYPE_RL:
                # RL agent uses neural network with exploration
                # Use a percentage of max_iteration instead of hardcoded 1000
                explore_threshold = min(1000, int(self.settings.max_iteration * 0.2))
                if t < explore_threshold or random.random() < self.epsilon:
                    chosen_action = random.choice(self.actions)
                else:
                    # Use neural network for decision making
                    state_tensor = self.state_to_tensor(self.current_state)
                    with torch.no_grad():
                        q_values = self.policy_net(state_tensor)
                        # Filter only valid actions
                        valid_q_values = torch.full((self.action_size,), float('-inf'))
                        for action in self.actions:
                            valid_q_values[action] = q_values[action]
                        
                        # With 95% probability choose the best action, 5% choose randomly from top 3
                        if random.random() < 0.95:
                            chosen_action = valid_q_values.argmax().item()
                        else:
                            # Get top 3 actions (or fewer if not enough actions)
                            top_k = min(3, len(self.actions))
                            _, top_indices = torch.topk(valid_q_values, top_k)
                            chosen_action = top_indices[random.randint(0, top_k-1)].item()
                
                # Decay epsilon only for the RL agent
                if self.epsilon > self.min_epsilon:
                    self.epsilon *= self.epsilon_decay
                
        self.latest_action = chosen_action

    def compute_val_snext(self):
        """Calculate value of next state using target network (compatible with original logic)"""
        if not self.uses_rl:
            # For non-RL agents, just set a default value
            self.val_snext = 0
            return
            
        next_state_tensor = self.state_to_tensor(self.health_list + [self.alliance_status])
        with torch.no_grad():
            q_values = self.target_net(next_state_tensor)
            # Filter only valid actions
            valid_q_values = torch.full((self.action_size,), float('-inf'))
            for action in self.actions:
                valid_q_values[action] = q_values[action]
            self.val_snext = valid_q_values.max().item()
    
    def learn(self, state, action, reward, next_state, done):
        """Learn from experience using neural network"""
        # Only RL agents learn from experience
        if not self.uses_rl:
            return
            
        # Store experience in shared replay buffer
        self.memory.push(state, action, reward, next_state, done)
        
        # Need enough samples for a batch and only train periodically to reduce computation
        if len(self.memory) < self.settings.batch_size or Agent.shared_update_counter % 3 != 0:
            Agent.shared_update_counter += 1
            return
            
        # Sample random batch
        states, actions, rewards, next_states, dones = self.memory.sample(self.settings.batch_size)
        
        # Convert to tensors
        states_tensor = torch.FloatTensor(states).to(self.device)
        actions_tensor = torch.LongTensor(actions).to(self.device)
        rewards_tensor = torch.FloatTensor(rewards).to(self.device)
        next_states_tensor = torch.FloatTensor(next_states).to(self.device)
        dones_tensor = torch.FloatTensor(dones).to(self.device)
        
        # Get current Q values
        current_q_values = self.policy_net(states_tensor).gather(1, actions_tensor.unsqueeze(1))
        
        # Compute target Q values
        with torch.no_grad():
            max_next_q_values = self.target_net(next_states_tensor).max(1)[0]
            target_q_values = rewards_tensor + (1 - dones_tensor) * self.settings.beta * max_next_q_values
            
        # Compute loss and optimize
        loss = torch.nn.MSELoss()(current_q_values.squeeze(), target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update target network periodically
        Agent.shared_update_counter += 1
        if Agent.shared_update_counter % self.settings.target_update_frequency == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
    
    def save_model(self, path):
        """Save the trained model"""
        if self.uses_rl:
            # Save only once for all RL agents (using agent 0)
            if self.agent_id == 0:
                torch.save(Agent.shared_policy_net.state_dict(), f"{path}_shared_policy.pth")
                print(f"Saved shared RL policy to {path}_shared_policy.pth")

    def load_model(self, path):
        """Load a trained model"""
        if self.uses_rl:
            # Load only once for all RL agents (using agent 0)
            if self.agent_id == 0 and Agent.shared_policy_net is not None:
                Agent.shared_policy_net.load_state_dict(torch.load(f"{path}_shared_policy.pth", map_location=self.device))
                Agent.shared_target_net.load_state_dict(Agent.shared_policy_net.state_dict())
                print(f"Loaded shared RL policy from {path}_shared_policy.pth")