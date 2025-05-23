# Multi-Agent War Simulation using Reinforcement Learning

A browser-based visualization tool for multi-agent reinforcement learning in a war simulation environment.

## Features

- Simulate interactions between multiple agents with different learning strategies
- Configure agent health, number of agents, and mutual animosity
- Visualize simulation results with interactive charts and animations
- Train RL agents and observe learning behavior
- Modern, responsive UI for a better user experience

## Technologies Used

- **Backend**: Flask, Python
- **ML/AI**: PyTorch, NumPy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Visualization**: Matplotlib, Plotly

## Getting Started

### Local Development

1. Clone the repository
   ```bash
   git clone https://github.com/Subramanyam6/Multi-Agent-War-Simulation-using-Reinforcement-Learning.git
   cd Multi-Agent-War-Simulation-using-Reinforcement-Learning
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application
   ```bash
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

## Configuration Options

### Agent Types
- **RL**: Reinforcement Learning agents that learn and adapt over time
- **Heuristic**: Rule-based agents with predefined strategies
- **Random**: Agents that take random actions

### Health Configurations
- **Full Health**: All agents start at maximum health
- **Low Health**: All agents start with low health
- **Random Health**: Agents start with random health values
- **Half-Half**: 50% of agents have high health, 50% have low health

### Reinforcement Learning Settings
- **Discount Factor (β)**: Determines how much the agent values future rewards
- **Learning Rate (α)**: Controls how quickly the agent updates its knowledge
- **Target Update Frequency**: How often the target network is updated
- **Replay Buffer Size**: Size of the experience replay buffer
- **Batch Size**: Number of samples processed together during training
- **Epsilon Parameters**: Control exploration vs. exploitation behavior

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Bala Subramanyam
