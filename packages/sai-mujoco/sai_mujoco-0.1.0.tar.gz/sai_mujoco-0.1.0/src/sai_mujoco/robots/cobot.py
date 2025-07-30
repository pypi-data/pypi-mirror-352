from sai_mujoco.base.robot import BaseArticulatedMujoco, BaseArticulatedMujocoIK

class CobotRobot(BaseArticulatedMujoco):
    default_pose: list = [-0.815990461,  1.01492790,  0.0,  2.06982485, -0.611301964, -1.51379419,  0.0,  0.0, 0.0, 0.0, 0.0, 0.0]
    init_ctr: list = [-1.55902942, -0.6, -0.00866798778, -0.863875032, 1.57012168,  1.56181935, 0.0]

    name: str = "cobot"
    xml_file_name: str = "cobot"

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
        "robot:right_gear_joint",
        "robot:left_gear_joint"
    ]

    joint_limits: dict[str, tuple[float, float]] = {
        "actuator1" : (-2.9, 2.9),
        "actuator2" : (-1.7628, 1.7628),
        "actuator3" : (-2,9, 2.9),
        "actuator4" : (-3.0718, -0.0698),
        "actuator5" : (-2.9, 2.9),
        "actuator6" : (-0.0175, 3.7525),
        "actuator8" : (0, 1)
    }

    dofs: int = len(joint_limits)
    end_effector: str = "end_effector"
    gripper_link: str = "end_effector"
    left_finger: str = "left_finger"
    right_finger: str = "right_finger"

    keyframes = {
        "init_frame" : {
            "init_qpos" : [-0.815990461,  1.01492790,  0.0,  2.06982485, -0.611301964, -1.51379419,  0.0,  0.0, 0.0, 0.0, 0.0, 0.0],
            "ctr" : [-1.55902942, -0.600806595, -0.008667987, -0.863875032, 1.57012168, 1.56181935, 0.0],
            "qvel" : [0, 0, 0, 0, 0, 0],
            "mpos" : [0.7,  0.0,  0.1],
            "mquat" : [0.707, 0.707, 0, 0]
        },
    }

    sensor_model = None

class CobotIKRobot(BaseArticulatedMujocoIK):
    default_pose: list = [-0.815990461,  1.01492790,  0.0,  2.06982485, -0.611301964, -1.51379419,  0.0,  0.0, 0.0, 0.0, 0.0, 0.0]
    init_ctr: list = [-1.55902942, -0.6, -0.00866798778, -0.863875032, 1.57012168,  1.56181935, 0.0]

    name: str = "cobot"
    xml_file_name: str = "cobot_ik"

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
        "robot:right_gear_joint",
        "robot:left_gear_joint"
    ]

    target_name: str = "target_robot"
    end_effector: str = "end_effector"
    gripper_link: str = "end_effector"
    left_finger: str = "left_finger"
    right_finger: str = "right_finger"

    keyframes = {
        "init_frame" : {
            "init_qpos" : [-0.815990461,  1.01492790,  0.0,  2.06982485, -0.611301964, -1.51379419,  0.0,  0.0, 0.0, 0.0, 0.0, 0.0],
            "ctr" : [-1.55902942, -0.600806595, -0.008667987, -0.863875032, 1.57012168, 1.56181935, 0.0],
            "qvel" : [0, 0, 0, 0, 0, 0],
            "mpos" : [0.7,  0.0,  0.1],
            "mquat" : [0.707, 0.707, 0, 0]
        },
    }

    sensor_model = None
