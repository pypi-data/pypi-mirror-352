from .franka import FrankaRobot, FrankaIKRobot
from .cobot import CobotRobot, CobotIKRobot
from .xarm7 import Xarm7Robot, Xarm7IKRobot
from .humanoid import HumanoidRobot

ROBOT_CLASS_REGISTORY = {

    # Manipulators
    "franka" : FrankaRobot,
    "franka_ik": FrankaIKRobot,
    "cobot": CobotRobot,
    "cobot_ik": CobotIKRobot,
    "xarm7": Xarm7Robot,
    "xarm7_ik": Xarm7IKRobot,

    # Humanoids
    "humanoid": HumanoidRobot,
}

def get_robot_class_registory(robot_name):

    if robot_name in ROBOT_CLASS_REGISTORY:
        return ROBOT_CLASS_REGISTORY[robot_name]
    else:
        ValueError("RobotClassNotFoundError: Robot name doesn't exist in the robot class registory !!!")