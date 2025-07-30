from gymnasium.envs.registration import register
from .grid_world import GridWorldV0, GridWorldMapsIndex
from .point_maze import PointMazeV0, PointMazeMapsIndex
from .ant_maze import AntMazeV0, AntMazeMapsIndex

register(
    id="GridWorld-v0",
    entry_point="rlnav.grid_world.grid_world_v0:GridWorldV0",
    kwargs={},
)
register(
    id="PointMaze-v0",
    entry_point="rlnav.point_maze.point_maze_v0:PointMazeV0",
    kwargs={},
)
register(
    id="AntMaze-v0",
    entry_point="rlnav.ant_maze.ant_maze_v0:AntMazeV0",
    kwargs={},
)

__all__ = ["GridWorldV0", "GridWorldMapsIndex", 
           "PointMazeV0", "PointMazeMapsIndex", 
           "AntMazeV0", "AntMazeMapsIndex"]
