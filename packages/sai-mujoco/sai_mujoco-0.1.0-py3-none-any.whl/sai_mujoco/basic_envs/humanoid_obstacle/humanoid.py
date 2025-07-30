# Adapted from Gymnasium's Humanoidv5 and currently uses the code directly
# TODO: replace with the class inheritance based code once v5 is integrated with gymnasium
from typing import Dict, Tuple

import numpy as np
import os

from gymnasium import utils
from gymnasium.envs.mujoco.mujoco_env import MujocoEnv
from gymnasium.spaces import Box

from sai_mujoco.utils.env import SAIMujocoBase


DEFAULT_CAMERA_CONFIG = {
    "trackbodyid": 1,
    "distance": 4.0,
    "lookat": np.array((0.0, 0.0, 2.0)),
    "elevation": -20.0,
}


def mass_center(model, data):
    mass = np.expand_dims(model.body_mass, axis=1)
    xpos = data.xipos
    return (np.sum(mass * xpos, axis=0) / np.sum(mass))[0:2].copy()


class HumanoidObstacleEnv(MujocoEnv, utils.EzPickle, SAIMujocoBase):
    """
    ## Description
    This environment is based on the environment introduced by Tassa, Erez and Todorov in
    ["Synthesis and stabilization of complex behaviors through online trajectory optimization"](https://ieeexplore.ieee.org/document/6386025).

    The environment simulates a 3D bipedal humanoid robot with a torso, legs and arms. The legs each have three segments
    (representing thigh, shin and foot) and the arms have two segments (representing upper and lower arm). The goal is to
    make the humanoid walk forward as fast as possible without falling over.

    ## Action Space
    The action space is a `Box(-1, 1, (17,), float32)` representing torques applied at each joint:

    - Abdomen (3 DOF): y, z, x rotations
    - Hips (3 DOF each): x, z, y rotations for right and left
    - Knees (1 DOF each): angle between thigh and shin for right and left
    - Shoulders (2 DOF each): two rotation coordinates for right and left
    - Elbows (1 DOF each): angle between upper and lower arm for right and left

    All joint torques are limited to [-0.4, 0.4] N⋅m.

    ## Observation Space
    The observation space is a `Box(-Inf, Inf, (348,), float64)` containing:

    - Robot joint positions (22 values)
    - Joint velocities (23 values)
    - Mass/inertia information (130 values)
    - Center of mass velocities (78 values)
    - Actuator forces (17 values)
    - External forces (78 values)

    The x/y position of the torso is excluded by default but can be included by setting
    `exclude_current_positions_from_observation=False`.

    ## Rewards
    The reward consists of four terms:

    1. Healthy reward: Fixed bonus for staying alive
    2. Forward reward: Bonus proportional to forward velocity
    3. Control cost: Penalty for large control inputs
    4. Contact cost: Penalty for large contact forces
    5. Fence cost: Penalty for touching fence

    Total reward = healthy_reward + forward_reward - ctrl_cost - contact_cost

    ## Episode End
    The episode ends if:
    - The humanoid falls (torso height outside allowed range)
    - Maximum episode steps reached (1000 by default)

    ## Configuration
    The environment can be customized through various parameters:

    - Reward weights and ranges
    - Health criteria
    - Initial state noise
    - Observation space contents
    - Physics simulation parameters

    See the Arguments section below for full details.

    ## Version History
    - v5: Major update with improved observation space, bug fixes, and new configuration options
    - v4: Updated to use native MuJoCo bindings
    - v3: Added support for custom XML and parameters
    - v2: Updated to MuJoCo-py >= 1.50
    - v1: Increased episode length to 1000 steps
    - v0: Initial release

    ## Arguments
    - `xml_file` (str): Path to MuJoCo model XML file
    - `frame_skip` (int): Number of physics steps per environment step
    - `forward_reward_weight` (float): Weight for forward movement reward
    - `ctrl_cost_weight` (float): Weight for control cost penalty
    - `contact_cost_weight` (float): Weight for contact force penalty
    - `healthy_reward` (float): Reward for staying alive
    - `terminate_when_unhealthy` (bool): Whether to end episode on failure
    - `healthy_z_range` (tuple): Allowed range for torso height
    - `reset_noise_scale` (float): Scale of initial state randomization
    - `exclude_current_positions_from_observation` (bool): Whether to exclude x/y position
    - Various observation component flags to customize observation space

    See source code for additional parameters and default values.
    """

    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
    }

    def __init__(
        self,
        xml_file: str = "humanoid.xml",
        frame_skip: int = 5,
        default_camera_config: Dict[str, float] = DEFAULT_CAMERA_CONFIG,
        forward_reward_weight: float = 1.25,
        ctrl_cost_weight: float = 0.1,
        touch_fence_weight: float = 0.1,
        contact_cost_weight: float = 5e-7,
        contact_cost_range: Tuple[float, float] = (-np.inf, 10.0),
        healthy_reward: float = 5.0,
        terminate_when_unhealthy: bool = True,
        healthy_z_range: Tuple[float, float] = (0.75, 3.0),
        reset_noise_scale: float = 1e-2,
        exclude_current_positions_from_observation: bool = True,
        include_cinert_in_observation: bool = True,
        include_cvel_in_observation: bool = True,
        include_qfrc_actuator_in_observation: bool = True,
        include_cfrc_ext_in_observation: bool = True,
        show_overlay: bool = False,
        **kwargs,
    ):
        xml_file_path = os.path.join(os.path.dirname(__file__), "assets", xml_file)
        utils.EzPickle.__init__(
            self,
            xml_file_path,
            frame_skip,
            default_camera_config,
            forward_reward_weight,
            ctrl_cost_weight,
            touch_fence_weight,
            contact_cost_weight,
            contact_cost_range,
            healthy_reward,
            terminate_when_unhealthy,
            healthy_z_range,
            reset_noise_scale,
            exclude_current_positions_from_observation,
            include_cinert_in_observation,
            include_cvel_in_observation,
            include_qfrc_actuator_in_observation,
            include_cfrc_ext_in_observation,
            **kwargs,
        )

        self._forward_reward_weight = forward_reward_weight
        self._ctrl_cost_weight = ctrl_cost_weight
        self._touch_fence_weight = touch_fence_weight
        self._contact_cost_weight = contact_cost_weight
        self._contact_cost_range = contact_cost_range
        self._healthy_reward = healthy_reward
        self._terminate_when_unhealthy = terminate_when_unhealthy
        self._healthy_z_range = healthy_z_range

        self._reset_noise_scale = reset_noise_scale

        self._exclude_current_positions_from_observation = (
            exclude_current_positions_from_observation
        )

        self._include_cinert_in_observation = include_cinert_in_observation
        self._include_cvel_in_observation = include_cvel_in_observation
        self._include_qfrc_actuator_in_observation = (
            include_qfrc_actuator_in_observation
        )
        self._include_cfrc_ext_in_observation = include_cfrc_ext_in_observation

        MujocoEnv.__init__(
            self,
            xml_file_path,
            frame_skip,
            observation_space=None,
            default_camera_config=default_camera_config,
            **kwargs,
        )

        self._toggle_overlay(show_overlay, kwargs["render_mode"])

        self.metadata = {
            "render_modes": [
                "human",
                "rgb_array",
                "depth_array",
            ],
            "render_fps": int(np.round(1.0 / self.dt)),
        }

        obs_size = self.data.qpos.size + self.data.qvel.size
        obs_size -= 2 * exclude_current_positions_from_observation
        obs_size += self.data.cinert[1:].size * include_cinert_in_observation
        obs_size += self.data.cvel[1:].size * include_cvel_in_observation
        obs_size += (self.data.qvel.size - 6) * include_qfrc_actuator_in_observation
        obs_size += self.data.cfrc_ext[1:].size * include_cfrc_ext_in_observation

        self.observation_space = Box(
            low=-np.inf, high=np.inf, shape=(obs_size,), dtype=np.float64
        )

        self.observation_structure = {
            "skipped_qpos": 2 * exclude_current_positions_from_observation,
            "qpos": self.data.qpos.size
            - 2 * exclude_current_positions_from_observation,
            "qvel": self.data.qvel.size,
            "cinert": self.data.cinert[1:].size * include_cinert_in_observation,
            "cvel": self.data.cvel[1:].size * include_cvel_in_observation,
            "qfrc_actuator": (self.data.qvel.size - 6)
            * include_qfrc_actuator_in_observation,
            "cfrc_ext": self.data.cfrc_ext[1:].size * include_cfrc_ext_in_observation,
            "ten_length": 0,
            "ten_velocity": 0,
        }

    @property
    def healthy_reward(self):
        return self.is_healthy * self._healthy_reward

    def control_cost(self, action):
        control_cost = self._ctrl_cost_weight * np.sum(np.square(self.data.ctrl))
        return control_cost

    @property
    def contact_cost(self):
        contact_forces = self.data.cfrc_ext
        contact_cost = self._contact_cost_weight * np.sum(np.square(contact_forces))
        min_cost, max_cost = self._contact_cost_range
        contact_cost = np.clip(contact_cost, min_cost, max_cost)
        return contact_cost

    @property
    def fence_cost(self):
        fence_geom = self.model.body_geomadr[self.model.body("hurdle").id]
        fence_geoms = range(
            fence_geom,
            fence_geom + self.model.body_geomnum[self.model.body("hurdle").id],
        )
        for i in range(self.data.ncon):
            contact = self.data.contact[i]
            if contact.geom1 in fence_geoms or contact.geom2 in fence_geoms:
                return self._touch_fence_weight
        return 0

    @property
    def is_healthy(self):
        min_z, max_z = self._healthy_z_range
        is_healthy = min_z < self.data.qpos[2] < max_z

        return is_healthy

    @property
    def terminated(self):
        terminated = (not self.is_healthy) and self._terminate_when_unhealthy
        return terminated

    def _get_obs(self):
        position = self.data.qpos.flat.copy()
        velocity = self.data.qvel.flat.copy()

        if self._include_cinert_in_observation is True:
            com_inertia = self.data.cinert[1:].flat.copy()
        else:
            com_inertia = np.array([])
        if self._include_cvel_in_observation is True:
            com_velocity = self.data.cvel[1:].flat.copy()
        else:
            com_velocity = np.array([])

        if self._include_qfrc_actuator_in_observation is True:
            actuator_forces = self.data.qfrc_actuator[6:].flat.copy()
        else:
            actuator_forces = np.array([])
        if self._include_cfrc_ext_in_observation is True:
            external_contact_forces = self.data.cfrc_ext[1:].flat.copy()
        else:
            external_contact_forces = np.array([])

        if self._exclude_current_positions_from_observation:
            position = position[2:]

        return np.concatenate(
            (
                position,
                velocity,
                com_inertia,
                com_velocity,
                actuator_forces,
                external_contact_forces,
            )
        )

    def step(self, action):
        # rescale action
        if self.rescale_bool:
            action = self._rescale_action(action)

        xy_position_before = mass_center(self.model, self.data)
        self.do_simulation(action, self.frame_skip)
        xy_position_after = mass_center(self.model, self.data)

        xy_velocity = (xy_position_after - xy_position_before) / self.dt
        x_velocity, y_velocity = xy_velocity

        ctrl_cost = self.control_cost(action)
        contact_cost = self.contact_cost
        fence_cost = self.fence_cost
        costs = ctrl_cost + contact_cost + fence_cost

        forward_reward = self._forward_reward_weight * x_velocity
        healthy_reward = self.healthy_reward

        rewards = forward_reward + healthy_reward

        observation = self._get_obs()
        reward = rewards - costs
        terminated = self.terminated
        info = {
            "reward_survive": healthy_reward,
            "reward_forward": forward_reward,
            "reward_ctrl": -ctrl_cost,
            "reward_contact": -contact_cost,
            "x_position": self.data.qpos[0],
            "y_position": self.data.qpos[1],
            "tendon_length": self.data.ten_length,
            "tendon_velocity": self.data.ten_velocity,
            "distance_from_origin": np.linalg.norm(self.data.qpos[0:2], ord=2),
            "x_velocity": x_velocity,
            "y_velocity": y_velocity,
        }

        if self.render_mode == "human":
            self.render()
        return observation, reward, terminated, False, info

    def reset_model(self):
        noise_low = -self._reset_noise_scale
        noise_high = self._reset_noise_scale

        qpos = self.init_qpos + self.np_random.uniform(
            low=noise_low, high=noise_high, size=self.model.nq
        )
        qvel = self.init_qvel + self.np_random.uniform(
            low=noise_low, high=noise_high, size=self.model.nv
        )
        self.set_state(qpos, qvel)

        observation = self._get_obs()
        return observation

    def _get_reset_info(self):
        return {
            "x_position": self.data.qpos[0],
            "y_position": self.data.qpos[1],
            "tendon_length": self.data.ten_length,
            "tendon_velocity": self.data.ten_velocity,
            "distance_from_origin": np.linalg.norm(self.data.qpos[0:2], ord=2),
        }
