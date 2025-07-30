from sai_mujoco.base.robot import BaseArticulatedMujoco, BaseArticulatedMujocoIK

class Xarm7Robot(BaseArticulatedMujoco):

    default_pose: list = [-0.429652443, -0.229498065,  0.458771622,  0.544016349, -3.01473430, -0.715247935,  1.43422194,  0.849951942, 0, 0, 0, 0, 0]
    init_ctr: list = [-0.429652443, -0.229498065,  0.458771622,  0.544016349, -3.01473430, -0.715247935,  1.43422194,  0.849951942]


    name: str = "xarm7"
    xml_file_name: str = "xarm7"

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
        "robot:right_driver_joint",
        "robot:left_driver_joint"
    ]

    joint_limits: dict[str, tuple[float, float]] = {
        "act1" : (-2.9, 2.9),
        "act2" : (-2.059, 2.0944),
        "act3" : (-2,9, 2.9),
        "act4" : (-0.19198, 3.927),
        "act5" : (-2.9, 2.9),
        "act6" : (-1.69297, 3.14159),
        "act7" : (-2.9, 2.9),
        "gripper" : (0, 255)
    }

    end_effector: str = "end_effector"
    gripper_link: str = "end_effector"
    left_finger: str = "left_finger"
    right_finger: str = "right_finger"

    keyframes = {
        "pick_place" : {
            "init_qpos" : [-0.429652443, -0.229498065,  0.458771622,  0.544016349, -3.01473430, -0.715247935,  1.43422194,  0.849951942, 0, 0, 0, 0, 0],
            "ctr" : [-0.429652443, -0.229498065,  0.458771622,  0.544016349, -3.01473430, -0.715247935,  1.43422194,  0.849951942],
            "qvel" : [0, 0, 0, 0, 0, 0],
            "mpos" : [0.965, 0.103, 0.74],
            "mquat" : [0.01545121,  0.03128406, -0.99765352,  0.05890685],
        },
    }

    sensor_model = None

class Xarm7IKRobot(BaseArticulatedMujocoIK):

    default_pose: list = [-0.429652443, -0.229498065,  0.458771622,  0.544016349, -3.01473430, -0.715247935,  1.43422194,  0.849951942, 0, 0, 0, 0, 0]
    init_ctr: list = [-0.429652443, -0.229498065,  0.458771622,  0.544016349, -3.01473430, -0.715247935,  1.43422194,  0.849951942]


    name: str = "xarm7"
    xml_file_name: str = "xarm7_ik"

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
        "robot:right_driver_joint",
        "robot:left_driver_joint"
    ]

    target_name: str = "target_robot"
    end_effector: str = "end_effector"
    gripper_link: str = "end_effector"
    left_finger: str = "left_finger"
    right_finger: str = "right_finger"

    keyframes = {
        "pick_place" : {
            "init_qpos" : [-0.429652443, -0.229498065,  0.458771622,  0.544016349, -3.01473430, -0.715247935,  1.43422194,  0.849951942, 0, 0, 0, 0, 0],
            "ctr" : [-0.429652443, -0.229498065,  0.458771622,  0.544016349, -3.01473430, -0.715247935,  1.43422194,  0.849951942],
            "qvel" : [0, 0, 0, 0, 0, 0],
            "mpos" : [0.965, 0.103, 0.74],
            "mquat" : [0.01545121,  0.03128406, -0.99765352,  0.05890685],
        },
    }

    sensor_model = None
