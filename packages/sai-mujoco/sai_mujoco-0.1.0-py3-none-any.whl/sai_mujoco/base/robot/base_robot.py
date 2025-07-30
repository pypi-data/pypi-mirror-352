import mujoco
import numpy as np
from os import path
from typing import Optional

from gymnasium.envs.mujoco.mujoco_env import MujocoEnv
from sai_mujoco.utils.mujoco_utils import MujocoModelNames

DEFAULT_CAMERA_CONFIG = {
    "trackbodyid": 0,
    "distance": 3,
}

SCREEN_HEIGHT = 700
SCREEN_WIDTH = 1200

class RobotClass(MujocoEnv):
    """
    A base class for MuJoCo environments with support for custom robot configurations and simulation management.

    This class defines a generic MuJoCo environment tailored for robotic simulations, providing functionality
    to load custom environment and robot configurations, create and reset the simulation, and manage the rendering
    of the environment. It can be configured for various robot types and is designed to support flexible task execution.

    Inherits from:
        MujocoEnv: Gymnasium's base class for MuJoCo environments.

    Attributes:
        env_config (dict): Configuration dictionary specifying environment settings (e.g., environment name, model paths).
        robot_config (dict): Configuration dictionary specifying robot details (e.g., control type, default pose, actuators).
        sensor_config (dict): Sensor configuration for the robot (if applicable).
        obs_list (list): List of observation extraction functions.
        obs_size (int): Total size of the observation space.
        init_qpos (np.ndarray): Initial joint positions for resetting the robot.
        init_qvel (np.ndarray): Initial joint velocities for resetting the robot.
        model_names (MujocoModelNames): Contains names for various elements in the model (e.g., bodies, joints).
        robot_info (dict): Information about the robot, such as joint names and count.
    """

    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
        "render_fps": 12,
    }

    def __init__(
        self,
        frame_skip: int = 40,
        default_camera_config: dict = DEFAULT_CAMERA_CONFIG,
        xml_file_name: str = "combined_model",
        **kwargs,
    ) -> None:
        """
        Initialize the robot environment.

        Args:
            frame_skip (int): Number of frames to skip per simulation step.
            default_camera_config (dict): Default camera view settings.
            xml_file_name (str): File name for the combined MJCF model.
        """
        self.dir_path = path.dirname(path.dirname(path.dirname(path.realpath(__file__))))

        self.xml_file_name = xml_file_name

        super().__init__(
            f"{self.dir_path}/assets/{xml_file_name}.xml",
            frame_skip,
            observation_space=None,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            default_camera_config=default_camera_config,
            **kwargs,
        )

        self.model_names = MujocoModelNames(self.model)
        self.viewer = self.mujoco_renderer._get_viewer

    def load_xml(self, xml_path: str) -> str:
        """Loads XML from the given path."""
        with open(xml_path, "r") as f:
            return f.read()

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        mujoco.mj_resetData(self.model, self.data)
        self.reset_model()

        if self.render_mode == "human":
            self.render()

    def reset_model(self) -> np.ndarray:
        """Resets the simulation to initial state and returns the observation."""
        self.data.qpos[: len(self.default_pose)] = self.default_pose
        self.data.qvel[: len(self.init_ctr)] = self.init_ctr

        self.set_state(self.data.qpos, self.data.qvel)
