import numpy as np
import gymnasium as gym


def is_data_nan(env: gym.Env) -> bool:
    return (
        np.isnan(env.robot_model.data.qpos).any()
        | np.isnan(env.robot_model.data.qvel).any()
    )
