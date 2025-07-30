from gymnasium.envs.registration import register
from .grid_world import GridWorld
from .point_maze import PointMazeV1
from .ant_maze import AntMaze, AntMazeMapsIndex
from .visual_ant_maze import VisualAntMaze, VisualAntMazeMapsIndex

register(
    id="GridWorld-v0",
    entry_point="rlnav.grid_world.grid_world:GridWorld",
    kwargs={},
)
register(
    id="PointMaze-v1",
    entry_point="rlnav.point_maze.point_maze_v1:PointMazeV1",
    kwargs={},
)

__all__ = ["GridWorld", "PointMazeV1"]


# OLD STUFF BELOW
supress_import_warnings = True

# For every environment module, we use try except statements in case one environment have unmeet dependencies but the
# user wants to use the others.
# For an example, it allows you to import GridWorld without having mujoco or vizdoom installed.

# Import grid-world
try:
    from .grid_world import *
except Exception as e:
    if not supress_import_warnings:
        print(f"Warning: module 'grid_world' cannot be imported due to the following error: ", e, sep="")


# Import point-maze-v1
try:
    from .point_maze import *
except Exception as e:
    if not supress_import_warnings:
        print(f"Warning: module 'point_maze' cannot be imported due to the following error: ", e, sep="")

# Import ant-maze
try:
    from .ant_maze import *
except Exception as e:
    if not supress_import_warnings:
        print(f"Warning: module 'ant_maze' cannot be imported due to the following error: ", e, sep="")

# Import doom-maze
try:
    from .doom_maze import *
except Exception as e:
    if not supress_import_warnings:
        print(f"Warning: module 'doom_maze' cannot be imported due to the following error: ", e, sep="")
