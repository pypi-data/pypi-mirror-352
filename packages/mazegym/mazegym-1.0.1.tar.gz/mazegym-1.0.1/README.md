# MazeGym

[![codecov](https://codecov.io/gh/EvalVis/MazeGym/branch/main/graph/badge.svg)](https://codecov.io/gh/EvalVis/MazeGym)
[![PyPI version](https://badge.fury.io/py/mazegym.svg)](https://pypi.org/project/mazegym/)

# 9x9 maze

Random moves are used for this demo.

![Maze9x9](images/maze_9_9.gif)

# 21x21 maze

Random moves are used for this demo.

![Maze21x21](images/maze_21_21.gif)

# 35x15 maze

Random moves are used for this demo.

![Maze35x15](images/maze_35_15.gif)

## Environment Details

- **Action Space**: Discrete(4) - Four possible actions: `0` (up), `1` (right), `2` (down), `3` (left). Invalid moves (moving into walls) results in an error.
- **Observation Space**: `Box(0, 3, (height, width), int8)`.
Contains values: `0` for empty paths, `1` for walls, `2` for the agent, `3` for the goal.
- **Reward**: `100` if the goal is reached, `-1` for each step taken.
- **Done**: `True` if the agent reaches the goal, `False` otherwise.
- **Truncated**: `True` if maximum steps `(3 × width × height)` are exceeded, `False` otherwise.