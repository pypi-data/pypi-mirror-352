import numpy as np
from typing import List
import gymnasium as gym
from .observation import get_sensor_data
from sai_mujoco.utils import mujoco_utils


def joint_vel_l2(env):
    """Penalize joint velocities."""
    joint_vel = env.robot_model.data.qvel[
        :7
    ]  # Assuming first 7 joints are the arm joints
    return np.sum(joint_vel**2)


def get_sensor_norm(env: gym.Env, sensor_name: str, axis: List[int]):
    data = get_sensor_data(env, sensor_name)

    return np.sum(np.square(data[axis]))


def get_cost_torques(env: gym.Env):
    forces = env.robot_model.data.actuator_force
    return np.sum(np.abs(forces))


def get_action_rate(env: gym.Env):
    return np.sum(np.square(env.action - env.last_action))


def get_dof_velocity(env: gym.Env):
    return np.sum(np.square(env.robot_model.data.qvel[env.robot_model.dofs :]))


def get_dof_acceleration(env: gym.Env):
    return np.sum(np.square(env.robot_model.data.qacc[env.robot_model.dofs :]))


def distance_between_objects(env, obj1: str, obj2: str):
    """Get the distance between two objects."""
    obj1_pose = mujoco_utils.get_site_xpos(
        env.robot_model.model, env.robot_model.data, obj1
    )
    obj2_pose = mujoco_utils.get_site_xpos(env.robot_model, env.robot_model.data, obj2)

    assert obj1_pose.shape == obj2_pose.shape

    return np.linalg.norm(obj1_pose - obj2_pose, axis=-1)
