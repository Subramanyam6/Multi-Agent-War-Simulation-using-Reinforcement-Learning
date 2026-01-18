# Multi-Agent War Simulation

Multi-agent reinforcement learning simulation using Deep Q-Networks. Agents learn, compete, and form alliances.

## Features

- RL, Heuristic, and Random agent types
- Alliance formation
- Real-time browser visualization
- Configurable RL parameters (DQN, epsilon-greedy, etc.)

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5001`

## Docker

```bash
docker build -t multi-agent-sim .
docker run -p 10000:10000 multi-agent-sim
```

Visit `http://localhost:10000`

## Deploy to Render.com

1. Fork this repo
2. Update `repo` URL in `render.yaml`
3. On Render: New+ → Blueprint → Select repo → Deploy

Health check: `/health`

## License

MIT
