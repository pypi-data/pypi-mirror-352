import gymnasium as gym
import numpy as np
from gymnasium import spaces
from typing import Optional, Tuple, Dict, Any, Union
from parkinglotpuzzle.lot import Lot
import matplotlib.pyplot as plt


class ParkingLotEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self, layout_str_or_moves: Union[str, int, None] = None):
        super(ParkingLotEnv, self).__init__()

        # Initialize the parking lot
        self.lot = Lot(layout_str_or_moves)
        
        if isinstance(layout_str_or_moves, str):
            self.initial_layout = layout_str_or_moves
        else:
            grid = self.lot.grid()
            self.initial_layout = '\n'.join(''.join(row) for row in grid)

        # Define action space: (vehicle_id, move)
        # vehicle_id is an integer index into the list of vehicles
        self.vehicle_ids = list(self.lot.query_vehicles().keys())

        self.width, self.height = self.lot.dimensions()
        max_moves = max(self.width, self.height) - 1
        self.action_space = spaces.MultiDiscrete([
            len(self.vehicle_ids),
            max_moves * 2
        ], start=[2, -max_moves])

        # Observation space: grid state
        # Each cell can be: empty (0), wall (1), or vehicle (2+)
        self.observation_space = spaces.Box(
            low=0,
            high=len(self.vehicle_ids) + 1,  # +1 for walls
            shape=(self.height, self.width),
            dtype=np.int32
        )

        # For rendering
        self._fig = None
        self._ax = None

        self.reset()

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        """Reset the environment to initial state."""
        super().reset(seed=seed)
        self.lot = Lot(self.initial_layout)
        observation = self._get_observation()
        info = {
            'available_moves': self._get_available_moves(),
        }
        return observation, info

    def step(self, action: Tuple[int, int]) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """Execute one time step within the environment."""
        vehicle_id_num, move = action
        if vehicle_id_num < 2 or vehicle_id_num >= len(self.vehicle_ids) + 2:
            raise ValueError(
                f"Invalid vehicle ID: {vehicle_id_num}. Vehicles start at index 2 and go up to {len(self.vehicle_ids) + 1}.")
        vehicle_id = self.vehicle_ids[vehicle_id_num - 2]

        try:
            # Attempt to make the move
            self.lot.move(vehicle_id, move)

            # Check if the game is solved
            done = self.lot.is_solved()
            reward = 0 if done else -1  # Small negative reward for each move

        except ValueError as _:
            # Invalid move
            done = False
            reward = -2

        # Get the new observation
        observation = self._get_observation()

        # Additional info
        info = {
            'available_moves': self._get_available_moves(),
        }

        return observation, reward, done, False, info

    def _get_available_moves(self) -> Dict[int, tuple]:
        """Get available moves for movable vehicles."""
        legal_moves = self.lot.query_legal_moves()
        return {
            self.vehicle_ids.index(vehicle_id) + 2: tuple(-i for i in range(1, backward + 1)) + tuple(i for i in range(1, forward + 1))
            for vehicle_id, (backward, forward) in legal_moves.items()
            if backward > 0 or forward > 0
        }

    def _get_observation(self) -> np.ndarray:
        """Convert the current grid state to a numpy array."""
        obs = np.zeros((self.height, self.width), dtype=np.int32)
        grid = self.lot.grid()

        for y in range(self.height):
            for x in range(self.width):
                cell = grid[y][x]
                if cell == '#':
                    obs[y, x] = 1
                elif cell == '.':
                    obs[y, x] = 0
                else:
                    # Map vehicle IDs to numbers starting from 2
                    obs[y, x] = self.vehicle_ids.index(cell) + 2

        return obs

    def render(self, mode='human'): # pragma: no cover
        """Render the environment to the screen."""
        if mode == 'human':
            grid = self.lot.grid()
            
            if self._fig is None or self._ax is None:
                self._fig, self._ax = plt.subplots(figsize=(6, 6))
                plt.ion()
                self._fig.show()
            
            self._ax.clear()
            
            # Draw grid lines
            for i in range(self.height + 1):
                self._ax.axhline(i, color='black', lw=2)
            for j in range(self.width + 1):
                self._ax.axvline(j, color='black', lw=2)
            
            # Fill in the cells
            for i in range(self.height):
                for j in range(self.width):
                    cell = grid[i][j]
                    if cell == '#':  # Wall
                        self._ax.add_patch(plt.Rectangle((j, self.height - i - 1), 1, 1, 
                                                       facecolor='gray', edgecolor='black'))
                    elif cell != '.':  # Vehicle
                        # Use different colors for different vehicles
                        color = plt.cm.tab20((ord(cell) - ord('A') + 6) % 20)
                        self._ax.add_patch(plt.Rectangle((j, self.height - i - 1), 1, 1, 
                                                       facecolor=color, edgecolor='black'))
                        self._ax.text(j + 0.5, self.height - i - 0.5, cell, 
                                    fontsize=20, ha='center', va='center')
            
            self._ax.set_xlim(0, self.width)
            self._ax.set_ylim(0, self.height)
            self._ax.set_xticks([])
            self._ax.set_yticks([])
            self._ax.set_title('Parking Lot Puzzle')
            
            self._fig.canvas.draw()
            self._fig.canvas.flush_events()
            
            return None
        else:
            raise NotImplementedError(f"Rendering mode {mode} not implemented.")

    def close(self):  # pragma: no cover
        """Clean up environment resources."""
        if self._fig is not None:
            plt.close(self._fig)
            self._fig = None
            self._ax = None