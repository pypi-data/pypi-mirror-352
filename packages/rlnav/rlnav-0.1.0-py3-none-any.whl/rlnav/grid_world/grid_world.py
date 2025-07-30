import copy
import importlib
import math
import random
from enum import Enum
from typing import Tuple, Optional, Any
import numpy as np
from gymnasium import spaces, Env


class GridWorldMapsIndex(Enum):
    EMPTY = "empty_room"
    FOUR_ROOMS = "four_rooms"
    MEDIUM = "medium_maze"
    HARD = "hard_maze"
    EXTREME = "extreme_maze"


class Colors(Enum):
    EMPTY = [250, 250, 250]
    WALL = [50, 54, 51]
    START = [213, 219, 214]
    TRAP = [255, 0, 0]
    TILE_BORDER = [50, 54, 51]
    AGENT = [0, 0, 255]
    GOAL = [73, 179, 101]


class TileType(Enum):
    EMPTY = 0
    WALL = 1
    START = 2
    REWARD = 3
    TRAP = 4


class Directions(Enum):
    TOP = 0
    BOTTOM = 1
    LEFT = 2
    RIGHT = 3


class GridWorld(Env):
    def __init__(self, **params):
        self.map_name: str = params.get("map_name", GridWorldMapsIndex.EMPTY.value)
        self.goal_conditioned: bool = params.get("goal_conditioned", True)
        self.reset_anywhere: bool = params.get("reset_anywhere", True)
        self.stochasticity: float = params.get("stochasticity", 0.0)
        assert 0.0 <= self.stochasticity <= 1.0, f"Invalid stochasticity value: {self.stochasticity}"

        self.goal_position: Optional[Tuple[int, int]] = None
        self.agent_coordinates: Optional[Tuple[int, int]] = None

        self.maze_array = np.array(importlib.import_module(f"rlnav.grid_world.maps.{self.map_name}").maze_array)
        self.height, self.width = self.maze_array.shape

        self.observation_space = spaces.Discrete(self.height * self.width)
        self.action_space = spaces.Discrete(len(Directions))

        self.reset()

    def reset(self, *,
              seed: int | None = None,
              options: dict[str, Any] | None = None, ):

        if seed is not None:
            random.seed(seed)

        if self.goal_conditioned:
            self.goal_position = self.sample_reachable_position()
            assert self.goal_position is not None, "No valid goal positions found."

        start_positions = np.argwhere(self.maze_array == TileType.START.value)
        assert len(start_positions) > 0, "No valid start positions found."
        self.agent_coordinates = tuple(random.choice(start_positions))

        return self._get_observation(*self.agent_coordinates), {}

    def step(self, action: int):
        action = self._apply_stochasticity(action)
        new_i, new_j = self._compute_new_position(action)

        if not self._is_valid_move(new_i, new_j):
            return self._get_observation(*self.agent_coordinates), 0, False, False, {}

        tile_type = self.get_tile_type(new_i, new_j)
        reward = -1 if tile_type == TileType.TRAP else 0
        done = tile_type in {TileType.REWARD, TileType.TRAP}

        if self.goal_conditioned:
            if (new_i, new_j) == self.goal_position:
                reward = 1
                done = True

        self.agent_coordinates = (new_i, new_j)
        return self._get_observation(new_i, new_j), reward, done, done, {}

    def _apply_stochasticity(self, action: int) -> int:
        if self.stochasticity > 0.0 and random.random() < self.stochasticity:
            action = (action + random.choice([-1, 1])) % 4
        return action

    def _compute_new_position(self, action: int) -> Tuple[int, int]:
        i, j = self.agent_coordinates
        if action == Directions.TOP.value and i > 0:
            i -= 1
        elif action == Directions.BOTTOM.value and i < self.height - 1:
            i += 1
        elif action == Directions.LEFT.value and j > 0:
            j -= 1
        elif action == Directions.RIGHT.value and j < self.width - 1:
            j += 1
        return i, j

    def _is_valid_move(self, i: int, j: int) -> bool:
        return 0 <= i < self.width and 0 <= j < self.height and self.get_tile_type(i, j) != TileType.WALL

    def _get_observation(self, i: int, j: int) -> int:
        return i * self.width + j

    def get_tile_type(self, i: int, j: int) -> TileType:
        return TileType(self.maze_array[i, j])

    def sample_reachable_position(self) -> Optional[Tuple[int, int]]:
        empty_positions = np.argwhere(
            np.logical_or(self.maze_array == TileType.EMPTY.value, self.maze_array == TileType.REWARD.value))
        if len(empty_positions) == 0:
            raise ValueError("No valid goal positions found.")
        return tuple(random.choice(empty_positions))

    def is_available(self, i: int, j: int) -> bool:
        return self._is_valid_move(i, j)
    
    def render(self, show_agent=True, show_rewards=True):
        pixels_per_tile = 10
        def set_tile_color(image_, i, j, color):
            image_[expanded_array == TileType.REWARD.value] = Colors.EMPTY.value
            i_start, i_end = i * pixels_per_tile, (i + 1) * pixels_per_tile
            j_start, j_end = j * pixels_per_tile, (j + 1) * pixels_per_tile
            image_[i_start:i_end, j_start:j_end, :] = color
            return image_

        # Second trial
        expanded_array = np.kron(self.maze_array, np.ones((pixels_per_tile, pixels_per_tile), dtype=int))
        image = np.zeros(expanded_array.shape + (3,), dtype=np.uint8)
        image[expanded_array == TileType.WALL.value] = Colors.WALL.value
        image[expanded_array == TileType.EMPTY.value] = Colors.EMPTY.value
        image[expanded_array == TileType.START.value] = Colors.START.value
        if show_rewards:
            image[expanded_array == TileType.TRAP.value] = Colors.TRAP.value
            if self.goal_conditioned:
                image = set_tile_color(image, *self.goal_position, Colors.GOAL.value)
            else:
                image[expanded_array == TileType.REWARD.value] = Colors.GOAL.value
        if show_agent:
            image = set_tile_color(image, *self.agent_coordinates, Colors.AGENT.value)
        return image
                
    def copy(self):
        return copy.deepcopy(self)
