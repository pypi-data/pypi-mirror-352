import numpy as np
import gymnasium as gym
from sai_mujoco.base.mdp.observation import get_sensor_data

def has_robot_fallen(env: gym.Env, min_height = 1.0, max_height = 2.0):

    height = env.robot_model.data.qpos[2]
    fallen = min_height < height < max_height
    return not fallen

