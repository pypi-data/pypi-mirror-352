import numpy as np
import mujoco

from sai_mujoco.utils.rotations import quat2mat


def approach_ee_club_grip(env):
    """Reward the robot for reaching the club grip using a steeper function for more responsive rewards."""

    ee_pos = env.robot_model.data.site(env.ee_id).xpos
    club_grip_pos = env.robot_model.data.xpos[env.golf_club_id]

    target_pos = club_grip_pos
    target_pos[2] += 0.15  # Add offset for z axis
    distance = np.linalg.norm(ee_pos - target_pos)
    scale_factor = 15.0
    reward = np.exp(-scale_factor * distance)
    return reward


def align_ee_handle(env):
    """Reward for aligning the end-effector with the handle.

    The correct alignment is when:
    - The z direction of the gripper is aligned with the -y direction of the handle
    - The -y direction of the gripper is aligned with the x direction of the handle

    This ensures the gripper is oriented correctly to grasp the handle.
    """
    ee_xmat = env.robot_model.data.site(env.ee_id).xmat
    ee_quat = np.zeros(4)
    mujoco.mju_mat2Quat(ee_quat, ee_xmat)
    handle_quat = env.robot_model.data.xquat[env.golf_club_id]

    # Convert quaternions to rotation matrices
    ee_rot_mat = quat2mat(ee_quat)
    handle_mat = quat2mat(handle_quat)

    # Get current x, y, z directions of the handle
    handle_x, handle_y, handle_z = (
        handle_mat[:, 0],
        handle_mat[:, 1],
        handle_mat[:, 2],
    )

    # Get current x, y, z directions of the gripper
    ee_x, ee_y, ee_z = ee_rot_mat[:, 0], ee_rot_mat[:, 1], ee_rot_mat[:, 2]

    # Calculate alignment scores
    # For correct alignment:
    # - ee_z should be aligned with -handle_y (dot product should be close to 1)
    # - -ee_y should be aligned with handle_x (dot product should be close to 1)
    align_z = np.dot(ee_z, -handle_y)
    align_y = np.dot(-ee_y, handle_x)

    # Penalize misalignment more strongly
    # We want to reward when alignments are close to 1 and penalize when they're close to -1
    # Using a quadratic function that peaks at 1 and is negative for values less than 0
    z_reward = 2 * align_z**2 - 1 if align_z > 0 else -1
    y_reward = 2 * align_y**2 - 1 if align_y > 0 else -1

    # Combine rewards, ensuring both alignments must be positive for a good reward
    reward = z_reward * y_reward

    return reward


def approach_gripper_handle(env, offset=0.04):
    """Reward the robot's gripper reaching the club grip with the right pose.

    This function returns the distance of fingertips to the handle when the fingers are in a grasping orientation
    (i.e., the left finger is to the left of the handle and the right finger is to the right of the handle).
    Otherwise, it returns zero.
    """
    ee_pos = env.robot_model.data.site(env.ee_id).xpos

    # Get club grip position and orientation
    handle_pos = env.robot_model.data.xpos[env.golf_club_id]

    left_finger_pos = env.robot_model.data.xpos[env.left_finger_id]
    right_finger_pos = env.robot_model.data.xpos[env.right_finger_id]

    # Check if hand is in a graspable pose
    is_graspable = (right_finger_pos[1] < handle_pos[1]) & (
        left_finger_pos[1] > handle_pos[1]
    )

    is_graspable = (
        is_graspable
        & (ee_pos[2] < handle_pos[2] + 0.03)
        & (ee_pos[0] - handle_pos[0] < 0.02)
    )

    if not is_graspable:
        return 0.0

    # Compute the distance of each finger from the handle
    lfinger_dist = np.abs(left_finger_pos[1] - handle_pos[1])
    rfinger_dist = np.abs(right_finger_pos[1] - handle_pos[1])

    # Reward is proportional to how close the fingers are to the handle when in a graspable pose
    reward = is_graspable * ((offset - lfinger_dist) + (offset - rfinger_dist)) * 10
    return reward


def approach_ball_hole(env):
    """Reward for approaching the ball to the hole."""

    # Get ball and hole positions
    ball_pos = env.robot_model.data.xpos[env.golf_ball_id]
    hole_pos = env.robot_model.data.xpos[env.golf_hole_id]
    distance = np.linalg.norm(ball_pos - hole_pos)
    reward = np.exp(distance * -3.0)
    return reward


def club_dropped(env, minimum_height=0.25):
    """Penalize if the club is dropped."""

    # Get club grip position and orientation
    club_grip_pos = env.robot_model.data.xpos[env.golf_club_id]
    return float(club_grip_pos[2] < minimum_height)


def ball_passed_hole(env):
    """Penalize if the ball passed the hole."""
    # Get ball and hole positions
    ball_pos = env.robot_model.data.xpos[env.golf_ball_id]
    hole_pos = env.robot_model.data.xpos[env.golf_hole_id]
    # Check if the ball has passed the hole in the x direction
    return float(ball_pos[0] < hole_pos[0] - 0.1)
