from mazelib import Maze
from mazelib.generate.Prims import Prims
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import matplotlib.pyplot as plt
from matplotlib import colors

class MazeEnvironment(gym.Env):
    def __init__(self, width=None, height=None, grid=None, render_mode="rgb_array"):
        super().__init__()
        self._width = width
        self._height = height
        self._maze = None
        self._agent_pos = None
        self._goal_pos = None
        self._steps_taken = 0
        self._max_steps = None
        
        self._initial_maze = None
        self._initial_agent_pos = None
        self._initial_goal_pos = None
        
        self.action_space = None
        self.observation_space = None
        self.render_mode = render_mode
        self.fig = None
        self.ax = None
        
        # Enable interactive mode for non-blocking plots
        if render_mode == "human":
            plt.ion()

        if width and height is not None:
            if width < 7 or height < 7:
                raise ValueError("Maze cannot be smaller than 7x7.")
            if width % 2 == 0 or height % 2 == 0:
                raise ValueError("Dimensions must be odd numbers.")

        if ((width is not None and height is not None and grid is not None)
                or ((width is None or height is None) and grid is None)):
            raise ValueError("Please enter either width and height or a grid")
        
        if grid is not None:
            self._setup_from_grid(grid)
        else:
            self._generate_maze()

    def _setup_from_grid(self, grid):
        """Set up the environment from a provided grid."""
        if not isinstance(grid, np.ndarray):
            raise ValueError("Grid must be a numpy array")
        
        if grid.dtype != np.int8:
            raise ValueError("Grid must be of dtype np.int8")
            
        if not np.all(np.isin(grid, [0, 1, 2, 3])):
            raise ValueError("Grid must contain only values 0, 1, 2, 3")
        
        agent_positions = np.argwhere(grid == 2)
        if len(agent_positions) != 1:
            raise ValueError("Grid must contain exactly one agent (value 2)")
        self._agent_pos = (int(agent_positions[0][0]), int(agent_positions[0][1]))
        
        goal_positions = np.argwhere(grid == 3)
        if len(goal_positions) != 1:
            raise ValueError("Grid must contain exactly one goal (value 3)")
        self._goal_pos = (int(goal_positions[0][0]), int(goal_positions[0][1]))
        
        self._height, self._width = grid.shape
        self._maze = grid.copy()
        
        self._update_spaces()
        self._store_initial_state()
        
    def _generate_maze(self):
        """Generate a random maze."""
        maze = Maze()
        
        # Convert our dimensions to mazelib dimensions
        # For a maze of width W and height H, mazelib needs dimensions (W*2+1, H*2+1)
        # because it represents walls as cells too
        maze_width = (self._width - 1) // 2
        maze_height = (self._height - 1) // 2
        
        # Ensure minimum size
        maze_width = max(1, maze_width)
        maze_height = max(1, maze_height)
        
        maze.generator = Prims(maze_width, maze_height)
        maze.generate()
        
        grid = np.array(maze.grid, dtype=np.int8)
        path_positions = np.argwhere(grid == 0)
        if path_positions.size == 0:
            raise ValueError("No path found in the maze")
        
        self._agent_pos = (int(path_positions[0][0]), int(path_positions[0][1]))
        grid[self._agent_pos] = 2
        
        self._goal_pos = (int(path_positions[-1][0]), int(path_positions[-1][1]))
        grid[self._goal_pos] = 3
        
        self._maze = grid.copy()
        
        self._update_spaces()
        self._store_initial_state()
    
    def _update_spaces(self):
        """Set up action and observation spaces based on current dimensions."""
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(
            low=0, high=3, shape=(self._height, self._width), dtype=np.int8
        )
    
    def _store_initial_state(self):
        """Store the initial state for reset."""
        self._initial_maze = self._maze.copy()
        self._initial_agent_pos = self._agent_pos
        self._initial_goal_pos = self._goal_pos
        self._steps_taken = 0
        self._max_steps = 3 * self._width * self._height
    
    def _get_valid_moves(self, position):
        row, col = position
        moves = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        valid_moves = []
        
        for i, (dr, dc) in enumerate(moves):
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self._height and 0 <= new_col < self._width and self._maze[new_row, new_col] != 1:
                valid_moves.append(i)
                
        return valid_moves
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        self._maze = self._initial_maze.copy()
        self._agent_pos = self._initial_agent_pos
        self._goal_pos = self._initial_goal_pos
        self._steps_taken = 0

        info = {"valid_moves": self._get_valid_moves(self._agent_pos)}
        return self._maze.copy(), info
    
    def step(self, action):
        if self._steps_taken >= self._max_steps:
            raise ValueError("Episode has already finished.")
            
        self._steps_taken += 1
        current_row, current_col = self._agent_pos
        
        valid_moves = self._get_valid_moves(self._agent_pos)
        
        if action not in valid_moves:
            raise ValueError(f"Invalid action: {action}. Valid moves are {valid_moves}")
            
        moves = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # 0: up, 1: right, 2: down, 3: left
        dr, dc = moves[action]
        
        new_row, new_col = current_row + dr, current_col + dc
        
        self._maze[current_row, current_col] = 0
        self._maze[new_row, new_col] = 2
        self._agent_pos = (new_row, new_col)
        truncated = self._steps_taken >= self._max_steps
              
        if self._agent_pos == self._goal_pos:
            return self._maze.copy(), 100, True, truncated, {}
 
        info = {"valid_moves": self._get_valid_moves(self._agent_pos)}
        return self._maze.copy(), -1, False, truncated, info
    
    def render(self): # pragma: no cover
        if self.render_mode == "rgb_array":
            return self._maze.copy()
        elif self.render_mode == "human":
            custom_cmap = colors.ListedColormap(['white', 'black', 'blue', 'red'])
            
            if self.fig is None or not plt.fignum_exists(self.fig.number):
                self.fig, self.ax = plt.subplots(figsize=(10, 5))
                self.ax.set_title(f"Maze ({self._width}x{self._height})")
                self.ax.set_xticks([])
                self.ax.set_yticks([])
                self.im = self.ax.imshow(self._maze, cmap=custom_cmap, interpolation='nearest')
            else:
                self.im.set_data(self._maze)
            
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            
            return self._maze.copy()
    
    def close(self): # pragma: no cover
        if self.fig is not None:
            plt.close(self.fig)
    