from typing import Tuple

import numpy as np
from gymnasium import spaces

from sai_mujoco.utils.controllers import IKController
from sai_mujoco.utils.rotations import euler2quat, quat2euler
from .base_robot import RobotClass

DEFAULT_CAMERA_CONFIG = {
    "trackbodyid": 0,
    "distance": 3,
}

class BaseArticulatedMujoco(RobotClass):
    """
    Base class for MuJoCo manipulation robots supporting both task-space and joint-space control.

    Inherits:
        RobotClass: Base robot class for MuJoCo environments.
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
        Initialize the manipulation robot.
        """

        super().__init__(
            frame_skip,
            default_camera_config,
            xml_file_name,
            **kwargs,
        )
        
        self._get_action_space()

    def step(self, action: np.ndarray) -> None:
        """
        Executes a simulation step.
        """

        action = np.clip(action, -1.0, 1.0)

        self.do_simulation(action, self.frame_skip)

    def _get_action_space(self) -> None:
        """Initializes the robot action space."""

        actuated_elements = len(self.joint_limits)
        action_space_low = np.array([limits[0] for limits in self.joint_limits.values()]).astype(np.float32)
        action_space_high = np.array([limits[1] for limits in self.joint_limits.values()]).astype(np.float32)

        self.action_space = spaces.Box(
            low=action_space_low,
            high=action_space_high,
            shape=(actuated_elements,),
            dtype=np.float32,
        )

    def _random_keyframe(self, env_keyframe, seed):

        np.random.seed(seed)

        noise_low = -self._reset_noise_scale
        noise_high = self._reset_noise_scale

        qpos = self.default_pose + self.np_random.uniform(
            low=noise_low, high=noise_high, size=len(self.default_pose)
        )
        qpos = np.concatenate([qpos, env_keyframe["init_qpos"]])
        self.data.qpos[:len(qpos)] = qpos

    def _reset_keyframe(self, keyframe):

        self.data.qpos[:len(keyframe["init_qpos"])] = keyframe["init_qpos"]
        self.data.ctrl[:len(keyframe["ctr"])] = keyframe["ctr"]
        self.data.qvel[:len(keyframe["qvel"])] = keyframe["qvel"]

class BaseArticulatedMujocoIK(RobotClass):
    """
    Base class for MuJoCo manipulation robots supporting both task-space control.

    Inherits:
        RobotClass: Base robot class for MuJoCo environments.
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
        Initialize the manipulation robot.
        """

        super().__init__(
            frame_skip,
            default_camera_config,
            xml_file_name,
            **kwargs,
        )

        self._get_action_space()

    def step(self, action: np.ndarray) -> None:
        """
        Executes a simulation step.
        """
        action = np.clip(action, -1.0, 1.0)

        delta_pos = action[:3]
        delta_euler = action[3:6]
        gripper_action = action[6]

        mocap_pos = self.data.mocap_pos[self.target_mocap_id]
        mocap_quat = self.data.mocap_quat[self.target_mocap_id]

        mocap_pos += delta_pos

        mocap_euler = quat2euler(mocap_quat)
        mocap_euler += delta_euler
        mocap_quat = euler2quat(mocap_euler)

        self.data.mocap_pos[self.target_mocap_id] = mocap_pos
        self.data.mocap_quat[self.target_mocap_id] = mocap_quat

        ctrl = self.ik_controller.calculate_ik()
        ctrl = ctrl[: len(self.data.ctrl)]

        gripper_ctrl_range = self.model.actuator_ctrlrange[-1]
        if gripper_action > 0:
            ctrl[-1] = gripper_ctrl_range[1]
        else:
            ctrl[-1] = gripper_ctrl_range[0]

        self.do_simulation(ctrl, self.frame_skip)

    def _get_action_space(self) -> None:
        """Initializes the robot action space."""

        self.action_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(7,),
            dtype=np.float64,
        )

        self.target_mocap_id = self.model.body(self.target_name).mocapid[0]

        self.ik_controller = IKController(
            self.model,
            self.data,
            target_mocap_name=self.target_name,
            end_effector_site_name=self.end_effector,
            joint_names=self.joint_names,
        )

    def _random_keyframe(self, env_keyframe, seed):

        np.random.seed(seed)

        noise_low = -self._reset_noise_scale
        noise_high = self._reset_noise_scale

        qpos = self.default_pose + self.np_random.uniform(
            low=noise_low, high=noise_high, size=len(self.default_pose)
        )
        qpos = np.concatenate([qpos, env_keyframe["init_qpos"]])
        self.data.qpos[:len(qpos)] = qpos

    def _reset_keyframe(self, keyframe):
        self.data.qpos[:len(keyframe["init_qpos"])] = keyframe["init_qpos"]
        self.data.qvel[:len(keyframe["qvel"])] = keyframe["qvel"]
        self.data.mocap_quat[:len(keyframe["mquat"])] = keyframe["mquat"]
        self.data.mocap_pos[:len(keyframe["mpos"])] = keyframe["mpos"]
