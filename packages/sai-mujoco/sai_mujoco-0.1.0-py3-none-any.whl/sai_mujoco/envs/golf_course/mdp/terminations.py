import numpy as np


def ball_in_hole(env):
    """Check if the ball is in the hole."""
    ball_pos = env.robot_model.data.xpos[env.golf_ball_id]
    hole_pos = env.robot_model.data.xpos[env.golf_hole_id]

    return np.linalg.norm(ball_pos - hole_pos) < 0.06
