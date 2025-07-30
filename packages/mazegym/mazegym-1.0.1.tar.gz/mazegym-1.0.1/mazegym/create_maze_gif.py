import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from PIL import Image
import io
import random
from mazegym.maze_gym_env import MazeEnvironment

def create_maze_gif(width=21, height=21, num_moves=600, gif_filename="maze_animation.gif"):
    """
    Create a GIF animation of a maze environment with random moves using the render method.
    
    Args:
        width (int): Width of the maze (must be odd)
        height (int): Height of the maze (must be odd)
        num_moves (int): Number of moves to execute
        gif_filename (str): Name of the output GIF file
    """
    # Create the maze environment with human render mode for visualization
    env = MazeEnvironment(width=width, height=height, render_mode="human")
    
    # Initialize the environment
    observation, info = env.reset()
    
    # Store frames for GIF creation
    frames = []
    
    print(f"Starting maze animation with {num_moves} moves...")
    print("Legend: White=Path, Black=Wall, Blue=Agent, Red=Goal")
    
    # Render and capture the initial frame
    env.render()
    
    # Convert the current matplotlib figure to PIL Image
    fig = env.fig
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    frames.append(Image.open(buf).copy())
    buf.close()
    
    # Execute moves and collect frames
    done = False
    truncated = False
    move_count = 0
    
    while move_count < num_moves and not done and not truncated:
        # Get valid moves
        valid_moves = info.get("valid_moves", [0, 1, 2, 3])
        
        if not valid_moves:
            print(f"No valid moves available at move {move_count}")
            break
        
        # Choose a random valid action
        action = random.choice(valid_moves)
        
        try:
            # Take the action
            observation, reward, done, truncated, info = env.step(action)
            move_count += 1
            
            # Render the current state
            env.render()
            
            # Update the title to show current move
            
            # Capture frame
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            frames.append(Image.open(buf).copy())
            buf.close()
            
            # Print progress every 50 moves
            if move_count % 50 == 0:
                print(f"Completed {move_count} moves...")
            
            # Check if goal reached
            if done:
                print(f"Goal reached at move {move_count}! Reward: {reward}")
                break
                
        except ValueError as e:
            print(f"Error at move {move_count}: {e}")
            break
    
    # Create and save the GIF
    print(f"Creating GIF with {len(frames)} frames...")
    
    if frames:
        # Convert all frames to the same mode (RGB)
        rgb_frames = []
        for frame in frames:
            if frame.mode != 'RGB':
                frame = frame.convert('RGB')
            rgb_frames.append(frame)
        
        # Save as GIF
        rgb_frames[0].save(
            gif_filename,
            save_all=True,
            append_images=rgb_frames[1:],
            duration=100,  # 100ms per frame
            loop=0  # Loop forever
        )
        
        print(f"GIF saved as '{gif_filename}' with {len(frames)} frames")
        print(f"Total moves executed: {move_count}")
    else:
        print("No frames to save!")
    
    # Clean up
    env.close()

def main():
    """Main function to create the maze GIF."""
    print("Creating maze GIF animation...")
    
    # Create GIF with 600 moves
    create_maze_gif(
        width=35,
        height=15,
        num_moves=600,
        gif_filename="maze_35_15.gif"
    )
    
    print("Animation complete!")

if __name__ == "__main__":
    main() 