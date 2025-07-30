# ParkingLotGym

[![codecov](https://codecov.io/gh/EvalVis/ParkingLotGym/branch/main/graph/badge.svg)](https://codecov.io/gh/EvalVis/ParkingLotGym)
[![PyPI version](https://badge.fury.io/py/ParkingLotGym.svg)](https://pypi.org/project/parkinglotgym/)

A custom AI Gymnasium environment for the Rush hour puzzle: https://en.wikipedia.org/wiki/Rush_Hour_(puzzle).

Library used: [![GitHub](https://img.shields.io/badge/GitHub-EvalVis/ParkingLot-black?style=flat&logo=github)](https://github.com/EvalVis/ParkingLot).

# Example solvable in 60 moves

Random moves are used for this demo. Click on `.gif` if still.

![ParkingLot60](images/parking_lot_60.gif)

# Example solvable in 5 moves

Random moves are used for this demo. Click if `.gif` if still.

![ParkingLot5](images/parking_lot_5.gif)

## Usage

### Initiating the env via gym

```python
import gymnasium as gym

env_6x6_random = gym.make('Puzzle6x6Moves15-v0')
env_4x4_random = gym.make('Puzzle6x6Moves30-v0')

env_6x6_fixed = gym.make('Puzzle6x6Moves13Fixed-v0')
env_6x6_fixed = gym.make('Puzzle6x6Moves6Fixed-v0')
```

### Initiating the env directly

```python
from parkinglotgym import ParkingLotEnv

env_random = ParkingLotEnv(15)
env_fixed = ParkingLotEnv
("""
    ....O
    FF..O
    .AA..
    ..BB.
    .CC..
    .DD..
""")
```

### Making moves

```python
import gymnasium as gym

env_3x3_fixed = gym.make('Puzzle6x6Moves13Fixed-v0')

# Reset the environment
observation, info = env_3x3_fixed.reset()

# Make a random valid move
import random

# Grab list of vehicles with their available moves.
available_moves = info["available_moves"]
# Drop moves from now, leave only vehicles.
movable_vehicles = [v for v, moves in available_moves.items()]
# Select a random vehicle to move.
vehicle = random.choice(movable_vehicles)
# Select a random move for the chosen vehicle.
move = random.choice(available_moves[vehicle])

# Render the environment. The only render mode is 'human' which renders visual output.
env_3x3_fixed.render()

# Close the environment
env_3x3_fixed.close()
```

## Environment Details

- **Action Space**: MultiDiscrete([num_vehicles, max_moves*2], start=[2, -max_moves]) - First value selects vehicle ID (starting at 2), second value indicates steps to move (negative for backward, positive for forward). Moving 0 steps is not allowed.
- **Observation Space**: `Box(0, num_vehicles+1, (height, width), int32)`.
Contains values: `0` for empty cells, `1` for walls, `2` and up for vehicles. '2` represents the main vehicle.
- **Reward**: `0` if the puzzle is solved, `-1` if not solved yet, `-2` if invalid move.
- **Done**: `True` if the puzzle is solved, `False` otherwise.