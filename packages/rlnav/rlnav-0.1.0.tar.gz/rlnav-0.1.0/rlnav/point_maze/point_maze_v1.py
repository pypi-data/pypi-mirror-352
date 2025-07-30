import gymnasium as gym
from gymnasium import Env
from gymnasium.spaces import Box
import numpy as np
import importlib
import random
from matplotlib import pyplot as plt
from typing import Any, Tuple, Optional, Dict

from rlnav.point_maze.utils.indexes import TileType, Colors, PointMazeMapsIndex


class PointMazeV1(Env):
    """
    2D Point Maze Navigation Environment.
    In the code below, x/y refers to the agent's position in the observation space, i/j refers to the agent's position
    in the maze grid (i refers to the row id, j to the column id).
    """

    name = "Point-Maze"
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 10}

    def __init__(self, **params):
        """
        Initialize the Point Maze environment.

        Args:
            map_name: Name of the map module to load (default: "EMPTY")
            action_noise: Standard deviation of noise added to actions (default: 1.0)
            reset_anywhere: Whether to reset agent at any valid position (default: True)
            goal_conditioned: Whether to use goal-conditioned RL (default: False)
            render_mode: Rendering mode (default: "rgb_array")
        """
        self.map_name: str = params.get("map_name", PointMazeMapsIndex.EMPTY.value)
        self.action_noise = params.get("action_noise", 1.0)
        self.reset_anywhere = params.get("reset_anywhere", True)
        self.goal_conditioned = params.get("goal_conditioned", False)
        self.render_mode = params.get("render_mode", "rgb_array")
        self.render_resolution = params.get("render_resolution", 10)  # Pixels per grid cell

        assert isinstance(self.action_noise, float) and self.action_noise > 0, "Invalid action_noise value."
        assert isinstance(self.reset_anywhere, bool), "reset_anywhere must be a boolean."
        assert isinstance(self.goal_conditioned, bool), "goal_conditioned must be a boolean."
        assert self.render_mode in self.metadata["render_modes"], f"Invalid render_mode: {self.render_mode}"

        # Load the maze map from the given map name
        module_path = f"rlnav.point_maze.maps.{self.map_name}"
        try:
            self.maze_array = np.array(importlib.import_module(module_path).maze_array, dtype=np.float16)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Failed to load maze map '{self.map_name}': {e}")

        self.height, self.width = self.maze_array.shape

        # Define the observation and action spaces
        self.observation_space: Box = Box(
            low=np.array([-self.width / 2, -self.height / 2], dtype=np.float32),
            high=np.array([self.width / 2, self.height / 2], dtype=np.float32)
        )
        self.action_space: Box = Box(
            low=np.array([-1.0, -1.0], dtype=np.float32),
            high=np.array([1.0, 1.0], dtype=np.float32)
        )

        # Initialize state variables
        self.agent_observation = None
        self.goal = None

        # For rendering
        self.window = None
        self.clock = None

        # Reset to initialize agent position and goal
        self.reset()

    def _sample_reachable_position(self) -> np.ndarray:
        """Sample a random reachable position in the maze."""
        empty_tiles = np.argwhere(
            np.logical_or(self.maze_array == TileType.EMPTY.value,
                          self.maze_array == TileType.REWARD.value))
        if len(empty_tiles) == 0:
            raise ValueError("Looking for a reachable position but none was found.")

        # Sample a reachable tile
        reachable_tile = random.choice(empty_tiles)
        # Reachable position at the center of the tile
        position = self.get_observation(*reachable_tile)
        # Sample a point in the selected tile, avoid np.random to keep the reset seed for random package
        noise = np.array([random.random(), random.random()]) - 0.5
        return position + noise

    def get_observation(self, i: int, j: int) -> np.ndarray:
        """Converts grid coordinates to an observation that belongs to the center of the tile."""
        return np.array([j + 0.5 - self.width / 2, -(i + 0.5 - self.height / 2)])

    def get_coordinates(self, observation: np.ndarray) -> Tuple[int, int]:
        """Return the tile that belongs to the given observation."""
        i = int(- observation[1] + self.height / 2)
        j = int(observation[0] + self.width / 2)

        # Ensure coordinates are within bounds
        i = max(0, min(i, self.height - 1))
        j = max(0, min(j, self.width - 1))

        return i, j

    def reset(self, *,
              seed: Optional[int] = None,
              options: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, Dict]:
        """
        Reset the environment to an initial state.

        Args:
            seed: Random seed for reproducibility
            options: Additional options for reset customization

        Returns:
            Initial observation and info dict
        """
        # Set seeds if provided
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            self.np_random, seed = gym.utils.seeding.np_random(seed)

        # Reset the agent's position
        if self.reset_anywhere:
            self.agent_observation = self._sample_reachable_position()
        else:
            valid_tiles = np.argwhere(self.maze_array == TileType.START.value)
            if len(valid_tiles) == 0:
                raise ValueError("Cannot reset with reset_anywhere=False and no available start tiles.")
            self.agent_observation = self.get_observation(*random.choice(valid_tiles))

        assert self.observation_space.contains(self.agent_observation.astype(self.observation_space.dtype)), \
            f"Invalid observation after reset: {self.agent_observation}"

        # Sample a goal for goal-conditioned RL
        info = {}
        if self.goal_conditioned:
            self.goal = self._sample_reachable_position()
            # Return both observation and goal
            return np.concatenate([self.agent_observation.copy(), self.goal.copy()]), info

        return self.agent_observation.copy(), info

    def is_available(self, i: int, j: int) -> bool:
        """
        Check if a position (i, j) in the maze array is available (not a wall or out of bounds).

        Args:
            i: Row index
            j: Column index

        Returns:
            True if the position is available, False otherwise
        """
        return (0 <= j < self.width and
                0 <= i < self.height and
                self.maze_array[i, j] != TileType.WALL.value)

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        Move the agent according to the action and return the new state.

        Args:
            action: Action to take

        Returns:
            Tuple of (observation, reward, terminated, truncated, info)
        """
        assert self.action_space.contains(action.astype(self.action_space.dtype)), \
            f"Invalid action: {action}"

        # Add action noise
        action = np.clip(action + np.random.normal(0, self.action_noise, size=action.shape),
                         self.action_space.low, self.action_space.high)

        # Implement sub-stepping for smoother movement
        for _ in range(10):  # Sub-steps
            new_observation = self.agent_observation + action / 10
            if not self.is_available(*self.get_coordinates(new_observation)):
                break
            self.agent_observation = new_observation

        # Get current tile type
        i, j = self.get_coordinates(self.agent_observation)
        tile_type = self.maze_array[i, j]

        # Calculate reward and check termination conditions
        reward = 10.0 if tile_type == TileType.REWARD.value else -0.1

        # Check if agent reached trap
        terminated = tile_type == TileType.TRAP.value
        truncated = False

        # Additional info for debugging
        info = {
            "position": self.agent_observation.copy(),
            "coordinates": (i, j),
            "tile_type": int(tile_type)
        }

        # If goal-conditioned, add distance to goal in info
        if self.goal_conditioned:
            distance_to_goal = np.linalg.norm(self.agent_observation - self.goal)
            info["distance_to_goal"] = distance_to_goal

            # Add goal-based reward component
            if distance_to_goal < 0.5:  # Within half a tile of goal
                reward += 5.0
                terminated = True

            # Return concatenated observation for goal-conditioned case
            return np.concatenate(
                [self.agent_observation.copy(), self.goal.copy()]), reward, terminated, truncated, info

        return self.agent_observation.copy(), reward, terminated, truncated, info

    def render(self, show_agent=True, show_rewards=True, show_grid=False):
        """
        Render the maze environment with continuous agent position.

        Returns:
            RGB array representation of the environment
        """
        # Create a blank canvas
        img_height = self.height * self.render_resolution
        img_width = self.width * self.render_resolution
        img = np.zeros((img_height, img_width, 3), dtype=np.uint8)

        # Draw the maze grid
        for i in range(self.height):
            for j in range(self.width):
                tile_type = int(self.maze_array[i, j])
                y_start = i * self.render_resolution
                y_end = (i + 1) * self.render_resolution
                x_start = j * self.render_resolution
                x_end = (j + 1) * self.render_resolution

                # Set color based on tile type
                if tile_type == TileType.EMPTY.value:
                    color = Colors.EMPTY.value
                elif tile_type == TileType.WALL.value:
                    color = Colors.WALL.value
                elif tile_type == TileType.START.value:
                    color = Colors.START.value
                elif tile_type == TileType.REWARD.value:
                    color = Colors.REWARD.value
                elif tile_type == TileType.TRAP.value:
                    color = Colors.TRAP.value
                else:
                    color = Colors.EMPTY.value

                img[y_start:y_end, x_start:x_end] = color

                # Add tile border
                if show_grid and tile_type != TileType.WALL.value:
                    img[y_start:y_start + 1, x_start:x_end] = Colors.TILE_BORDER.value  # Top
                    img[y_end - 1:y_end, x_start:x_end] = Colors.TILE_BORDER.value  # Bottom
                    img[y_start:y_end, x_start:x_start + 1] = Colors.TILE_BORDER.value  # Left
                    img[y_start:y_end, x_end - 1:x_end] = Colors.TILE_BORDER.value  # Right

        # Draw the agent using continuous coordinates
        # Assuming self.agent_x and self.agent_y are the continuous coordinates (bounded)
        # and self.x_bounds = (x_min, x_max), self.y_bounds = (y_min, y_max) define the bounds

        # Map from continuous space to pixel space
        x_min, y_min = self.observation_space.low
        x_max, y_max = self.observation_space.high

        if show_agent:
            # Normalize the agent's position to the image dimensions
            agent_x_norm = (self.agent_observation[0] - x_min) / (x_max - x_min) * img_width
            agent_y_norm = (self.agent_observation[1] - y_min) / (y_max - y_min) * img_height

            agent_x_center = int(agent_x_norm)
            agent_y_center = int(agent_y_norm)
            agent_radius = self.render_resolution // 3

            # Draw a circle for the agent
            y, x = np.ogrid[:img_height, :img_width]
            dist = np.sqrt((y - agent_y_center) ** 2 + (x - agent_x_center) ** 2)
            mask = dist <= agent_radius
            img[mask] = Colors.AGENT.value

        # Draw the goal if goal-conditioned and with continuous coordinates
        if show_rewards and self.goal_conditioned and hasattr(self, 'goal_x') and hasattr(self, 'goal_y'):
            # Map from continuous space to pixel space
            goal_x_norm = (self.goal_x - x_min) / (x_max - x_min) * img_width
            goal_y_norm = (self.goal_y - y_min) / (y_max - y_min) * img_height

            goal_x_center = int(goal_x_norm)
            goal_y_center = int(goal_y_norm)
            goal_radius = self.render_resolution // 3

            # Draw a circle for the goal
            y, x = np.ogrid[:img_height, :img_width]
            dist = np.sqrt((y - goal_y_center) ** 2 + (x - goal_x_center) ** 2)
            mask = dist <= goal_radius
            img[mask] = Colors.GOAL.value

        if self.render_mode == "human":
            # Display the image using matplotlib
            plt.figure(figsize=(8, 8))
            plt.imshow(img)
            plt.axis('off')
            plt.title(f"{self.name} Environment")
            plt.show()

        return img

    def close(self):
        """Clean up resources."""
        if self.window is not None:
            plt.close('all')
            self.window = None

    def copy(self):
        """Create a copy of this environment."""
        return PointMazeV1(
            map_name=self.map_name,
            action_noise=self.action_noise,
            reset_anywhere=self.reset_anywhere,
            goal_conditioned=self.goal_conditioned,
            render_mode=self.render_mode,
            render_resolution=self.render_resolution
        )