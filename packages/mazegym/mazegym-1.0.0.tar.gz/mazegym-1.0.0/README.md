# MazeGym

A Gymnasium-based environment for maze-based reinforcement learning tasks.

## Installation

```bash
# From PyPI (once published)
pip install mazegym

# From source
git clone https://github.com/yourusername/mazegym.git
cd mazegym
pip install -e .
```

## Usage

### Creating a random maze

```python
import gymnasium as gym
import mazegym
import numpy as np
import matplotlib.pyplot as plt

# Create a 10x10 maze environment
env = mazegym.MazeEnvironment(width=10, height=10)

# Reset the environment to get initial state
obs, info = env.reset()

# Visualize the maze
plt.figure(figsize=(8, 8))
plt.imshow(obs, cmap='gray')
plt.title('Maze Environment')
plt.colorbar(ticks=[0, 1, 2, 3], labels=['Path', 'Wall', 'Agent', 'Goal'])
plt.show()

# Get valid moves
print(f"Valid moves: {info['valid_moves']}")
```

### Creating a custom maze

```python
import gymnasium as gym
import mazegym
import numpy as np

# Create a custom 5x5 maze with a specific layout
grid = np.ones((5, 5), dtype=np.int8)  # All walls
grid[1:4, 2] = 0  # Vertical path
grid[1, 1:3] = 0  # Horizontal path for agent
grid[3, 2:4] = 0  # Horizontal path for goal
grid[1, 1] = 2    # Agent position
grid[3, 3] = 3    # Goal position

env = mazegym.MazeEnvironment(grid=grid)
```

### Taking actions

```python
# Take a step with action 1 (right)
obs, reward, done, truncated, info = env.step(1)

# Check if the episode is done (reached goal)
if done:
    print(f"Goal reached! Reward: {reward}")
```

## License

GNU General Public License v3.0

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.