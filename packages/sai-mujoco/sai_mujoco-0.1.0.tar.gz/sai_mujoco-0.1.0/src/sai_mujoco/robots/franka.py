import numpy as np
from sai_mujoco.base.robot import BaseArticulatedMujoco, BaseArticulatedMujocoIK

class FrankaRobot(BaseArticulatedMujoco):

    default_pose: list = [0.2555, 0.0117, -0.2936, -2.5540, 1.5981, 1.4609, -1.7311, 0.04, 0.04]
    init_ctr: list = [0.256, -0.00117, -0.294, -2.55, 1.6, 1.46, -1.73, 255]

    name: str = "franka"
    xml_file_name: str = "franka"

    root: str = "robot"
    fix_base_link: bool = True
    _reset_noise_scale: float = 5e-1

    joint_names = [
        "robot:joint1",
        "robot:joint2",
        "robot:joint3",
        "robot:joint4",
        "robot:joint5",
        "robot:joint6",
        "robot:joint7",
        "robot:finger_joint1",
        "robot:finger_joint2"
    ]

    joint_limits: dict[str, tuple[float, float]] = {
        "actuator1" : (-2.9, 2.9),
        "actuator2" : (-1.7628, 1.7628),
        "actuator3" : (-2,9, 2.9),
        "actuator4" : (-3.0718, -0.0698),
        "actuator5" : (-2.9, 2.9),
        "actuator6" : (-0.0175, 3.7525),
        "actuator7" : (-2.9, 2.9),
        "actuator8" : (0, 255)
    }

    dofs: int = len(joint_limits)
    end_effector: str = "end_effector"
    gripper_link: str = "end_effector"
    left_finger: str = "left_finger"
    right_finger: str = "right_finger"

    keyframes = {
        "init_frame" : {
            "init_qpos" : [0.2555, -0.0117, -0.2936, -2.5540, 1.5981, 1.4609, -1.7311, 0.04, 0.04],
            "ctr" : [0.256, -0.00117, -0.294, -2.55, 1.6, 1.46, -1.73, 255],
            "qvel" : [0, 0, 0, 0, 0, 0],
            "mpos" : [0.695, -0.087,  0.34],
            "mquat" : [0.69235922,  0.24279981, -0.6228822,  -0.27148614]
        },
        
        "pick_place" : {
            "init_qpos": [-0.121, -0.5791, 0.0906, -2.42, 0.0635, 1.71, 0.931, 0.04, 0.04],
            "ctr": [-0.121, -0.5791, 0.0906, -2.42, 0.0635, 1.71, 0.931, 255],
            "qvel": [0, 0, 0, 0, 0, 0],
            "mpos": [0.95, 0.0,  1.025],
            "mquat": [0.05742438, -0.87737411, 0.47558214,  0.02]
        },
    }

    sensor_model = None

class FrankaIKRobot(BaseArticulatedMujocoIK):

    default_pose: list = [0.2555, 0.0117, -0.2936, -2.5540, 1.5981, 1.4609, -1.7311, 0.04, 0.04]
    init_ctr: list = [0.256, -0.00117, -0.294, -2.55, 1.6, 1.46, -1.73, 255]

    name: str = "franka"
    xml_file_name: str = "franka_ik"

    num_joints: int = 9
    root: str = "robot"
    fix_base_link: bool = True
    _reset_noise_scale: float = 5e-3

    joint_names = [
        "robot:joint1",
        "robot:joint2",
        "robot:joint3",
        "robot:joint4",
        "robot:joint5",
        "robot:joint6",
        "robot:joint7",
        "robot:finger_joint1",
        "robot:finger_joint2"
    ]

    keyframes = {
        "init_frame" : {
            "init_qpos" : [0.2555, -0.0117, -0.2936, -2.5540, 1.5981, 1.4609, -1.7311, 0.04, 0.04],
            "ctr" : [0.256, -0.00117, -0.294, -2.55, 1.6, 1.46, -1.73, 255],
            "qvel" : [0, 0, 0, 0, 0, 0],
            "mpos" : [0.695, -0.087,  0.34],
            "mquat" : [0.69235922,  0.24279981, -0.6228822,  -0.27148614]
        },
        
        "pick_place" : {
            "init_qpos": [-0.121, -0.5791, 0.0906, -2.42, 0.0635, 1.71, 0.931, 0.04, 0.04],
            "ctr": [-0.121, -0.5791, 0.0906, -2.42, 0.0635, 1.71, 0.931, 255],
            "qvel": [0, 0, 0, 0, 0, 0],
            "mpos": [0.95, 0.0,  1.025],
            "mquat": [0.05742438, -0.87737411, 0.47558214,  0.02]
        },
    }

    target_name: str = "target_robot"
    end_effector: str = "end_effector"
    gripper_link: str = "end_effector"
    left_finger: str = "left_finger"
    right_finger: str = "right_finger"

    sensor_model = None
