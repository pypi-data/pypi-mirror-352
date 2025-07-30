import time
import random
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from maze_gym_env import MazeEnvironment


class RandomWalker:
    """A class that performs random walks in a maze environment."""
    
    def __init__(self, maze_env):
        """
        Initialize the RandomWalker with a maze environment.
        
        Args:
            maze_env: An instance of MazeEnvironment
        """
        self.env = maze_env
        self.move_count = 0
        self.paused = False
        self.step_ready = False
        
    def _on_next_button(self, event):
        """Callback for the Next button."""
        self.step_ready = True
        
    def _setup_interactive_controls(self):
        """Set up interactive controls for manual stepping."""
        if self.env.render_mode == "human" and self.env.fig is not None:
            # Add a Next button to the figure
            ax_button = plt.axes([0.81, 0.05, 0.15, 0.075])
            self.next_button = Button(ax_button, 'Next Step')
            self.next_button.on_clicked(self._on_next_button)
            return True
        return False
        
    def _wait_for_next_step(self, mode):
        """Wait for next step based on the mode."""
        if mode == "auto":
            time.sleep(0.1)
        elif mode == "manual_input":
            input("Press Enter for next step...")
        elif mode == "manual_button":
            print("Click 'Next Step' button to continue...")
            self.step_ready = False
            while not self.step_ready:
                plt.pause(0.1)  # Allow GUI events to be processed
        
    def walk(self, num_moves=100, mode="auto", sleep_duration=0.1):
        """
        Perform a random walk for the specified number of moves.
        
        Args:
            num_moves: Number of random moves to make (default: 100)
            mode: Control mode - "auto", "manual_input", or "manual_button" (default: "auto")
            sleep_duration: Time to sleep between moves in auto mode (default: 0.1)
        """
        valid_modes = ["auto", "manual_input", "manual_button"]
        if mode not in valid_modes:
            raise ValueError(f"Mode must be one of {valid_modes}")
            
        print(f"Starting random walk with {num_moves} moves in {mode} mode...")
        
        # Reset the environment to start fresh
        obs, info = self.env.reset()
        self.move_count = 0
        
        # Render the initial state
        self.env.render()
        
        # Set up interactive controls if needed
        has_button_controls = False
        if mode == "manual_button":
            has_button_controls = self._setup_interactive_controls()
            if not has_button_controls:
                print("Button controls not available, falling back to manual input mode...")
                mode = "manual_input"
        
        # Show initial instructions
        if mode == "manual_input":
            print("Press Enter to start and continue through each step...")
        elif mode == "manual_button":
            print("Click 'Next Step' button to start and continue through each step...")
        elif mode == "auto":
            print(f"Auto mode: {sleep_duration}s delay between moves")
            
        # Wait for initial input if in manual mode
        if mode in ["manual_input", "manual_button"]:
            self._wait_for_next_step(mode)
        elif mode == "auto":
            time.sleep(sleep_duration)
        
        for move_num in range(1, num_moves + 1):
            # Get valid moves from the environment info
            valid_moves = info.get("valid_moves", [])
            
            if not valid_moves:
                print(f"No valid moves available at move {move_num}. Stopping.")
                break
            
            # Choose a random valid move
            action = random.choice(valid_moves)
            
            try:
                # Take the action
                obs, reward, done, truncated, info = self.env.step(action)
                self.move_count += 1
                
                # Render the current state
                self.env.render()
                
                # Print progress info
                move_info = f"Move {move_num}/{num_moves}: Action {action}"
                if move_num % 10 == 0 or mode != "auto":
                    print(f"{move_info} completed")
                
                # Check if goal is reached
                if done:
                    print(f"🎉 Goal reached after {move_num} moves! Reward: {reward}")
                    if mode in ["manual_input", "manual_button"]:
                        print("Final state displayed above.")
                    break
                
                # Check if episode is truncated (max steps reached)
                if truncated:
                    print(f"Episode truncated after {move_num} moves (max steps reached)")
                    break
                
                # Wait for next step based on mode
                if move_num < num_moves:  # Don't wait after the last move
                    if mode == "auto":
                        time.sleep(sleep_duration)
                    else:
                        self._wait_for_next_step(mode)
                
            except ValueError as e:
                print(f"Error at move {move_num}: {e}")
                break
        
        print(f"Random walk completed. Total moves made: {self.move_count}")
        
        if mode in ["manual_input", "manual_button"]:
            print("Visualization will remain open. Close the window when done.")
            
        return self.move_count


def demo_random_walk():
    """Demonstration function showing how to use the RandomWalker."""
    print("=== RandomWalker Demo ===")
    print("Choose a mode:")
    print("1. Auto mode (0.1s delay between moves)")
    print("2. Manual input mode (press Enter for each step)")
    print("3. Manual button mode (click Next Step button)")
    
    try:
        choice = input("Enter choice (1-3, default=1): ").strip()
        if not choice:
            choice = "1"
            
        mode_map = {
            "1": "auto",
            "2": "manual_input", 
            "3": "manual_button"
        }
        
        mode = mode_map.get(choice, "auto")
        
        print(f"\nCreating a 15x15 maze...")
        
        # Create a maze environment
        env = MazeEnvironment(width=15, height=15, render_mode="human")
        
        # Create a random walker
        walker = RandomWalker(env)
        
        # Perform the random walk
        walker.walk(num_moves=100, mode=mode, sleep_duration=0.1)
        
        # Keep the plot open
        if mode == "auto":
            input("Press Enter to close the visualization...")
        else:
            input("Press Enter to close the visualization...")
        
        # Clean up
        env.close()
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    demo_random_walk() 