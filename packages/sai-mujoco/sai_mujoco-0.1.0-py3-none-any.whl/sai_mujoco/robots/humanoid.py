import numpy as np

from sai_mujoco.base.robot import BaseArticulatedMujoco
from sai_mujoco.sensors.humanoid_sensor import HumanoidBodySensor

class HumanoidRobot(BaseArticulatedMujoco):

    default_pose: list = [0, 0, 1.21948, 0.971588, -0.179973, 0.135318, -0.0729076, -0.0516, -0.202, 0.23, -0.24, -0.007, -0.34, -1.76, -0.466, -0.0415, -0.08,  -0.01,  -0.37,  -0.685,  -0.35,  -0.09, 0.109,  -0.067]
    init_ctr: list = [-0.0516, -0.202, 0.23, -0.24, -0.007, -0.34, -1.76, -0.466, -0.0415, -0.08,  -0.01,  -0.37,  -0.685,  -0.35,  -0.09, 0.109,  -0.067]

    name: str = "humanoid"
    xml_file_name: str = "humanoid"

    root: str = "torso"
    fix_base_link: bool = False

    joint_names = [
        "robot:abdomen_y",
        "robot:abdomen_z",
        "robot:abdomen_x",
        "robot:right_hip_x",
        "robot:right_hip_z",
        "robot:right_hip_y",
        "robot:right_knee",
        "robot:left_hip_x",
        "robot:left_hip_z",
        "robot:left_hip_y",
        "robot:left_knee",
        "robot:right_shoulder1",
        "robot:right_shoulder2",
        "robot:right_elbow",
        "robot:left_shoulder1",
        "robot:left_shoulder2",
        "robot:left_elbow"
    ]

    joint_limits = {
        "robot:abdomen_y": (-0.4, 0.4),
        "robot:abdomen_z": (-0.4, 0.4),
        "robot:abdomen_x": (-0.4, 0.4),
        "robot:right_hip_x": (-0.4, 0.4),
        "robot:right_hip_z": (-0.4, 0.4),
        "robot:right_hip_y": (-0.4, 0.4),
        "robot:right_knee": (-0.4, 0.4),
        "robot:left_hip_x": (-0.4, 0.4),
        "robot:left_hip_z": (-0.4, 0.4),
        "robot:left_hip_y": (-0.4, 0.4),
        "robot:left_knee": (-0.4, 0.4),
        "robot:right_shoulder1": (-0.4, 0.4),
        "robot:right_shoulder2": (-0.4, 0.4),
        "robot:right_elbow": (-0.4, 0.4),
        "robot:left_shoulder1": (-0.4, 0.4),
        "robot:left_shoulder2": (-0.4, 0.4),
        "robot:left_elbow": (-0.4, 0.4)
    }

    dofs: int = len(joint_limits)
    standing_height: list = [0.6, 2.0]

    FEET_SITES = ["left_foot","right_foot"]
    LEFT_FEET_GEOMS = [f"left_foot_{i}" for i in range(1, 5)]
    RIGHT_FEET_GEOMS = [f"right_foot_{i}" for i in range(1, 5)]
    foot_linvel_sensor_adr = []

    phase = np.array([0, np.pi])
    phase_dt = 0.01

    sensor_model = HumanoidBodySensor()
