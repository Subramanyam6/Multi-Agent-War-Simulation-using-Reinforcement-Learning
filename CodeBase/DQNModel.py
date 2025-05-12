import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random

class AgentNetwork(nn.Module):
    """Neural network model for approximating the Q-function for agents"""
    def __init__(self, input_size, hidden_size, output_size):
        super(AgentNetwork, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )
    
    def forward(self, x):
        return self.network(x)

class ReplayBuffer:
    """Experience replay buffer for storing and sampling agent experiences"""
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []
        self.position = 0
    
    def push(self, state, action, reward, next_state, done):
        """Add a new experience to the buffer"""
        if len(self.buffer) < self.capacity:
            self.buffer.append(None)
        self.buffer[self.position] = (state, action, reward, next_state, done)
        self.position = (self.position + 1) % self.capacity
    
    def sample(self, batch_size):
        """Sample a random batch of experiences"""
        batch = random.sample(self.buffer, min(len(self.buffer), batch_size))
        state, action, reward, next_state, done = map(np.stack, zip(*batch))
        return state, action, reward, next_state, done
    
    def __len__(self):
        return len(self.buffer) 