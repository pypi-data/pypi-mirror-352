import pytest
import numpy as np
from mazegym.maze_gym_env import MazeEnvironment

@pytest.fixture
def custom_env():
    grid = np.ones((5, 5), dtype=np.int8)
    # Create a path from agent to goal
    grid[1:4, 2] = 0  # Vertical path
    grid[1, 1:3] = 0  # Connect agent
    grid[3, 2:4] = 0  # Connect goal
    # Place agent and goal
    grid[1, 1] = 2  # Agent
    grid[3, 3] = 3  # Goal

    return MazeEnvironment(grid=grid)

def test_user_input_grid():
    """Test that a user can provide a custom grid."""
    grid = np.ones((4, 4), dtype=np.int8)
    grid[1, 1:3] = 0
    grid[2, 1:3] = 0
    grid[1, 1] = 2  # Agent
    grid[2, 2] = 3  # Goal
    
    env = MazeEnvironment(grid=grid)
    
    obs, _ = env.reset()
    
    # Verify grid dimensions match
    assert obs.shape == (4, 4)
    # Verify agent position
    agent_pos = tuple(np.argwhere(obs == 2)[0])
    assert agent_pos == (1, 1)
    # Verify goal position
    goal_pos = tuple(np.argwhere(obs == 3)[0])
    assert goal_pos == (2, 2)

def test_random_generation():
    """Test that a random maze is generated when no grid is provided."""
    width, height = 7, 7
    env = MazeEnvironment(width=width, height=height)
    
    obs, info = env.reset()
    
    # Verify dimensions
    assert obs.shape == (height, width)
    # Verify there's exactly one agent and one goal
    assert np.sum(obs == 2) == 1
    assert np.sum(obs == 3) == 1
    # Verify there are valid moves
    assert "valid_moves" in info
    assert len(info["valid_moves"]) > 0

def test_done_state():
    """Test that reaching the goal sets done to True."""
    grid = np.ones((3, 3), dtype=np.int8)
    grid[1, 0:3] = 0  # Horizontal path
    grid[1, 0] = 2  # Agent
    grid[1, 1] = 3  # Goal (adjacent to agent)
    env = MazeEnvironment(grid=grid)

    _, info = env.reset()
    valid_moves = info["valid_moves"]
    assert valid_moves == [1]
    
    # Execute the move
    obs, reward, done, truncated, _ = env.step(1)
    
    # Verify the done state
    print(obs)
    assert done is True
    assert reward == 100

def test_reset(custom_env):
    """Test that reset returns the environment to its initial state."""
    # Make a move
    obs, info = custom_env.reset()
    if "valid_moves" in info and len(info["valid_moves"]) > 0:
        action = info["valid_moves"][0]
        custom_env.step(action)
    
    # Reset and check it's back to initial state
    reset_maze, _ = custom_env.reset()
    
    # The reset maze should match the original grid with agent and goal
    agent_pos = np.argwhere(obs == 2)[0]
    goal_pos = np.argwhere(obs == 3)[0]

    reset_agent_pos = np.argwhere(reset_maze == 2)[0]
    reset_goal_pos = np.argwhere(reset_maze == 3)[0]
    
    assert np.array_equal(reset_agent_pos, agent_pos)
    assert np.array_equal(reset_goal_pos, goal_pos)

def test_valid_move(custom_env):
    """Test taking a valid move."""
    _, info = custom_env.reset()
    
    assert "valid_moves" in info
    assert info["valid_moves"] == [1]

    next_maze, reward, done, truncated, next_info = custom_env.step(1)
    
    # Verify the step returns all expected values
    assert isinstance(next_maze, np.ndarray)
    assert isinstance(reward, (int, float))
    assert isinstance(done, bool)
    assert isinstance(truncated, bool)
    assert isinstance(next_info, dict)
    
    # Check that agent moved (should be exactly one agent)
    agent_position = np.argwhere(next_maze == 2).tolist()
    assert agent_position == [[1, 2]]

def test_invalid_move(custom_env):
    """Test that an invalid action raises ValueError."""
    with pytest.raises(ValueError):
        invalid_action = 10  # An action index that doesn't exist
        custom_env.step(invalid_action) 