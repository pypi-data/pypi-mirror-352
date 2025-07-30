import numpy as np
import mujoco
from typing import List, Union
import gymnasium as gym
from sai_mujoco.utils.rotations import quat2mat
from sai_mujoco.utils import mujoco_utils, rotations
from sai_mujoco.base.mdp.rewards import get_sensor_data
from sai_mujoco.utils.extra_utils import geoms_colliding, get_rz
from .terminations import has_robot_fallen

def cost_base_height(env: gym.Env, base_height_target = 0.665) -> float:
    base_height = env.robot_model.data.qpos[2]
    return np.square(base_height - base_height_target)

def get_robot_energy(env: gym.Env):

    forces = env.robot_model.data.actuator_force
    vel = env.robot_model.data.qvel

    return np.sum(np.abs(vel[:env.robot_model.dofs] * forces))

def get_foot_clearance(env: gym.Env, max_foot_height: float = 0.12):

    feet_vel = env.robot_model.data.sensordata[env._foot_linvel_sensor_adr]
    vel_xy = feet_vel[..., :2]
    vel_norm = np.sqrt(np.linalg.norm(vel_xy, axis=-1))
    foot_pos = env.robot_model.data.site_xpos[env._feet_site_id]
    foot_z = foot_pos[..., -1]
    delta = np.abs(foot_z - max_foot_height)

    return np.sum(delta * vel_norm)

def get_contact(env: gym.Env):

    left_feet_contact = np.array([
        geoms_colliding(env.robot_model.data, geom_id, env._floor_geom_id)
        for geom_id in env._left_feet_geom_id
    ])
    right_feet_contact = np.array([
        geoms_colliding(env.robot_model.data, geom_id, env._floor_geom_id)
        for geom_id in env._right_feet_geom_id
    ])
    contact = np.hstack([np.any(left_feet_contact), np.any(right_feet_contact)])

    return contact

def get_foot_slip(env: gym.Env):

    contact = get_contact(env)
    body_vel = get_sensor_data(env,"global_linvel")[:2]
    reward = np.sum(np.linalg.norm(body_vel, axis=-1) * contact)
    return reward

def is_alive(env: gym.Env):

    has_fallen = has_robot_fallen(env)

    return ~has_fallen

def get_feet_distance(env: gym.Env):

    left_foot_pos = env.robot_model.data.site_xpos[env._feet_site_id[0]]
    right_foot_pos = env.robot_model.data.site_xpos[env._feet_site_id[1]]
    base_xmat = env.robot_model.data.site_xmat[env._site_id]
    base_yaw = np.arctan2(base_xmat[1], base_xmat[0])
    feet_distance = np.abs(
        np.cos(base_yaw) * (left_foot_pos[1] - right_foot_pos[1])
        - np.sin(base_yaw) * (left_foot_pos[0] - right_foot_pos[0])
    )
    return np.clip(0.2 - feet_distance, 0.0, 0.1)

# def get_feet_phase(env: gym.Env, max_foot_height: float = 0.12):

#     foot_pos = env.robot_model.data.site_xpos[env._feet_site_id]
#     foot_z = foot_pos[..., -1]
#     rz = get_rz(phase, swing_height=max_foot_height)
#     error = np.sum(np.square(foot_z - rz))
#     reward = np.exp(-error / 0.01)
#     return reward
