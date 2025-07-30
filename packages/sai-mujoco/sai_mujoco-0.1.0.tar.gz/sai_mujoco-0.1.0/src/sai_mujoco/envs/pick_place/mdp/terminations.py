from sai_mujoco.utils import mujoco_utils
from .rewards import goal_distance


def episode_success(env, obj_name: str, target_name: str, threshold=0.05):
    # Get club grip position and orientation
    """Penalize if the club is dropped."""
    object_pos = mujoco_utils.get_site_xpos(
        env.robot_model.model, env.robot_model.data, obj_name
    )
    target_pos = mujoco_utils.get_site_xpos(
        env.robot_model.model, env.robot_model.data, target_name
    )

    object_target_dist = goal_distance(object_pos, target_pos)

    return float(object_target_dist < threshold)
