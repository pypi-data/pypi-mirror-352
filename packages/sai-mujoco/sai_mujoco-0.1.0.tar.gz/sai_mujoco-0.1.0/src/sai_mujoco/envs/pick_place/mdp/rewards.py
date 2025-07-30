import numpy as np
from typing import List, Union

from sai_mujoco.utils import mujoco_utils


def goal_distance(goal_a, goal_b):
    """Calculate the Euclidean distance between two goals.

    Args:
        goal_a (np.ndarray): First goal position
        goal_b (np.ndarray): Second goal position

    Returns:
        float: Euclidean distance between the two goals
    """
    assert goal_a.shape == goal_b.shape
    return np.linalg.norm(goal_a - goal_b, axis=-1)


def grasp_reward(
    env, gripper_name: Union[List[str], str], target_name: str, method="min"
):
    # Get club grip position and orientation

    if method == "min":
        val = np.inf
    else:
        val = 0

    if isinstance(gripper_name, str):
        gripper_name = [gripper_name]

    for name in gripper_name:
        gripper_pos = mujoco_utils.get_site_xpos(
            env.robot_model.model, env.robot_model.data, name
        )
        target_pos = mujoco_utils.get_site_xpos(
            env.robot_model.model, env.robot_model.data, target_name
        )

        gripper_target_dist = goal_distance(gripper_pos, target_pos)

        if method == "min":
            val = np.minimum(val, gripper_target_dist)
        else:
            val += gripper_target_dist / len(gripper_name)

    reward = np.exp(-val)

    return reward


def place_reward(env, obj_name: str, target_name: str):
    # Get club grip position and orientation
    object_pos = mujoco_utils.get_site_xpos(
        env.robot_model.model, env.robot_model.data, obj_name
    )
    target_pos = mujoco_utils.get_site_xpos(
        env.robot_model.model, env.robot_model.data, target_name
    )

    object_target_dist = goal_distance(object_pos, target_pos)

    reward = np.exp(-object_target_dist)

    return reward
