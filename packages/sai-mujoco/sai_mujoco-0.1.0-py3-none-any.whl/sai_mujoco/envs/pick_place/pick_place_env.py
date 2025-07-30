from typing import Optional, Union

import mujoco
import numpy as np
from os import path

import gymnasium as gym
from gymnasium import spaces
from gymnasium.utils.ezpickle import EzPickle
from sai_mujoco.base.robot.base_robot import RobotClass

from . import mdp

from sai_mujoco.base.mdp_cfg import RewardCfg, TerminationCfg, ObservationCfg, SceneCfg
from sai_mujoco.base.mdp_term import RewardTerm, ObsTerm, DoneTerm, SceneTerm

from sai_mujoco.utils import mujoco_utils, rotations
from sai_mujoco.utils.env import SAIMujocoBase

class PickAndPlaceSceneCfg(SceneCfg):

    def __init__(self, env_config, robot_model):
        # 1. Move the end effector towards the club
        self.dir_path = path.dirname(path.dirname(path.dirname(path.realpath(__file__))))

        scene_xml = f"{self.dir_path}/assets/scene/base_scene.xml"
        env_xml = f"{self.dir_path}/assets/envs/pick_place/pick_place_env.xml"
        robot_xml = f"{self.dir_path}/assets/robots/{robot_model.name}/{robot_model.xml_file_name}.xml"
        

        if robot_model.sensor_model:
            sensor_xml = f"{self.dir_path}/assets/sensors/{robot_model.sensor_model.xml_file_name}.xml"
            self.sensor = SceneTerm(sensor_xml)

        self.scene = SceneTerm(scene_xml)

        self.env = SceneTerm(env_xml)

        self.robot = SceneTerm(robot_xml,
                               params={"position": env_config["position"],
                                       "orientation": env_config["orientation"],
                                       "body_name": robot_model.root})

class PickAndPlaceRewardCfg(RewardCfg):
    """
    Reward configuration for the Pick-and-Place environment.

    Reward Terms:
    - grasp_reward: Positive reward when the gripper successfully grasps the object.
    - place_reward: Positive reward when the object is successfully placed at the target.
    - success_reward: Final reward indicating successful task completion.
    """

    def __init__(self, robot_model: RobotClass):
        # 1. Grasp reward
            
        self.grasp_reward = RewardTerm(
            mdp.grasp_reward,
            weight=1.0,
            params={
                "gripper_name": robot_model.gripper_link,
                "target_name": "target0",
            },
        )

        # 2. Place reward
        self.place_reward = RewardTerm(
            mdp.place_reward,
            weight=1.0,
            params={"obj_name": "object0", "target_name": "target0"},
        )

        # 3. Positive reward if episode is success
        self.success_reward = RewardTerm(
            mdp.episode_success,
            weight=1.0,
            params={"obj_name": "object0", "target_name": "target0"},
        )

class PickAndPlaceSparseRewardCfg(RewardCfg):
    """
    Reward configuration for the Pick-and-Place environment.

    Reward Terms:
    - grasp_reward: Positive reward when the gripper successfully grasps the object.
    - place_reward: Positive reward when the object is successfully placed at the target.
    - success_reward: Final reward indicating successful task completion.
    """

    def __init__(self):
        # 1. Sparse reward 
        self.sparse_reward = RewardTerm(
            mdp.episode_success,
            weight=1.0,
            params={"obj_name": "object0", "target_name": "target0"},
        )

class PickAndPlaceTerminationCfg(TerminationCfg):
    """
    Termination configuration for the Pick-and-Place environment.

    Termination Terms:
    - success: Episode ends when the object is correctly placed at the target.
    """

    def __init__(self):
        self.success = DoneTerm(
            mdp.episode_success,
            params={"obj_name": "object0", "target_name": "target0"},
        )


class PickAndPlaceObsCfg(ObservationCfg):
    """
    Observation configuration for the Pick-and-Place environment.

    Observation Terms:
    - robot_state: General robot joint states (positions, velocities).
    - gripper_pose: 3D position of the robot's gripper.
    - object_rel_pos: Position of the object relative to the gripper.
    - object_rel_vel: Velocity of the object relative to the gripper.
    - object_rot: Rotation matrix or quaternion of the object.
    - object_velp: Linear velocity of the object.
    - object_velr: Angular velocity of the object.
    - target_pose: 3D position of the target location.
    - target_rot: Orientation of the target.
    """

    def __init__(self, robot_model: RobotClass):
        # 1. Robot state
        self.robot_state = ObsTerm(func=mdp.get_robot_obs)

        # 2. Gripper Pose
        self.gripper_pose = ObsTerm(
            func=mdp.get_position_in_world_frame,
            params={"object_name": robot_model.gripper_link},
        )

        # 3. Relative position and velocity of object and robot grippers
        self.object_rel_pos = ObsTerm(
            func=mdp.get_relative_position,
            params={
                "object_name": "object0",
                "target_name": robot_model.gripper_link,
            },
        )
        self.object_rel_vel = ObsTerm(
            func=mdp.get_relative_velocity,
            params={
                "object_name": "object0",
                "target_name": robot_model.gripper_link,
            },
        )

        # 4. Object rotation, linear and rotational velocity
        self.object_rot = ObsTerm(
            func=mdp.get_rotation_in_world_frame, params={"object_name": "object0"}
        )
        self.object_velp = ObsTerm(
            func=mdp.get_object_velp, params={"object_name": "object0"}
        )
        self.object_velr = ObsTerm(
            func=mdp.get_object_velr, params={"object_name": "object0"}
        )

        # 5. Target object position and rotation
        self.target_pose = ObsTerm(
            func=mdp.get_position_in_world_frame, params={"object_name": "target0"}
        )
        self.target_rot = ObsTerm(
            func=mdp.get_rotation_in_world_frame, params={"object_name": "target0"}
        )

        if robot_model.sensor_model and robot_model.sensor_model.state_sensor_space:
            sensors = robot_model.sensor_model.state_sensor_space
            for sensor_name in sensors:
                if sensor_name == "camera":
                    for name, render in robot_model.sensor_model.camera.items():
                        sensor = ObsTerm(
                            func=mdp.get_camera_data,
                            params={"camera_name": name, "render_mode": render},
                        )
                        setattr(self, f"sensor_{name}", sensor)
                else:
                    sensor = ObsTerm(
                        func=mdp.get_sensor_data, params={"sensor_name": sensor_name}
                    )
                    setattr(self, f"sensor_{sensor_name}", sensor)

class PickAndPlaceMujocoEnv(gym.Env, EzPickle, SAIMujocoBase):
    """
    A MuJoCo-based pick and place environment where a robot learns to pick up and place an object.

    This environment simulates a robotic system performing pick-and-place tasks with custom robot and environment configurations.
    It supports calculating rewards, determining termination conditions, and generating observations based on the robot's actions.

    Attributes:
        robot_model (object): The robot model used in the environment.
        rewards (PickAndPlaceRewardCfg): Configuration for the reward calculation.
        termination (PickAndPlaceTerminationCfg): Configuration for the termination condition.
        observations (PickAndPlaceObsCfg): Configuration for calculating observations.
        render_mode (str): The selected render mode for visualization (e.g., "human", "rgb_array").
        action_space (gym.Space): The action space for the robot.
        observation_space (gym.Space): The observation space for the environment.
        init_qpos (np.ndarray): Initial joint positions of the robot.
        init_qvel (np.ndarray): Initial joint velocities of the robot.

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
        env_config: dict,
        robot_class: RobotClass,
        keyframe: Union[str,dict] = "pick_place",
        xml_file_name: str = "combined_model",
        show_overlay: bool = False,
        **kwargs,
    ):
        """
        Initializes the PickAndPlaceMujocoEnv.

        Args:
            xml_file_name (str): Name of the combined XML model file.
        """

        # Reward, termination, and observation configurations specific to the golf course task.
        self.scene: PickAndPlaceSceneCfg = PickAndPlaceSceneCfg(env_config, robot_class)
        self.scene.compute()

        self.robot_model = robot_class(xml_file_name=xml_file_name, **kwargs)

        self.rewards: PickAndPlaceRewardCfg = PickAndPlaceRewardCfg(self.robot_model)
        self.termination: PickAndPlaceTerminationCfg = PickAndPlaceTerminationCfg()
        self.observations: PickAndPlaceObsCfg = PickAndPlaceObsCfg(self.robot_model)

        self.keyframe = keyframe
        # Initialize render mode and action space from the robot model.
        self.render_mode = self.robot_model.render_mode
        self.action_space = self.robot_model.action_space

        self.mujoco_renderer = self.robot_model.mujoco_renderer
        self._toggle_overlay(show_overlay, self.render_mode)

        # Calculate the observation space based on the robot's configuration.
        obs = self.observations.calculate(self)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=obs.shape, dtype=np.float32
        )

        self.pick_place_keyframe = {
            "init_qpos" : [0.7500, 0, -0.0003, 0.7074, -0.0000, 0.0000, 0.7068, 0.75, 0, 0.6545, 1.0000, -0.0000, -0.0000, 0],
            "ctr" : [],
            "qvel" : [0.0001, -0.0001, 0.0001, 0, 0, 0, 0, 0, 0, -0.0000, 0.0000, 0, 0, 0, 0],
            "mpos" : [],
            "mquat" : [] 
        }

        if self.keyframe != "random":
            self._create_keyframe()

    def compute_reward(self) -> float:
        """Compute the reward for the current state."""
        return self.rewards.calculate(self)

    def step(self, action):
        """
        Take a step in the environment based on the action and update the state.
        """
        self.robot_model.step(action)
        obs = self.observations.calculate(self)
        reward = self.compute_reward()

        terminated = self.compute_terminated()

        return obs, reward, terminated, False, {}

    def compute_terminated(self):
        """
        Compute whether the current episode has terminated based on specific criteria.
        """
        return self.termination.calculate(self)

    def reset(self, *, seed: Optional[int] = None, **kwargs):
        """
        Reset the environment to an initial state.
        """
        self._sample_object()
        self.goal_pos = self._sample_goal()
        self.robot_model.reset(seed=seed)
        self._reset_keyframe(seed=seed)
        obs = self.observations.calculate(self)
        # self._reset_keyframe()

        return obs, {}
    
    def _create_keyframe(self):

        if self.keyframe in self.robot_model.keyframes:
            robot_keyframe = self.robot_model.keyframes[self.keyframe]
        else:
            robot_keyframe = self.keyframe

        self.complete_keyframe = {
            "init_qpos": robot_keyframe["init_qpos"] + self.pick_place_keyframe["init_qpos"],
            "ctr": robot_keyframe["ctr"] + self.pick_place_keyframe["ctr"],
            "qvel": robot_keyframe["qvel"] + self.pick_place_keyframe["qvel"],
            "mpos": robot_keyframe["mpos"] + self.pick_place_keyframe["mpos"],
            "mquat": robot_keyframe["mquat"] + self.pick_place_keyframe["mquat"]
        }
    
    def _reset_keyframe(self, seed):

        if self.keyframe == "random":
            self.robot_model._random_keyframe(self.pick_place_keyframe, seed)
        else:
            self.robot_model._reset_keyframe(self.complete_keyframe)

        for _ in range(self.robot_model.frame_skip):
            mujoco.mj_step(self.robot_model.model, self.robot_model.data)

    def _sample_goal(self):
        """Sample a new goal position and orientation.

        Returns:
            np.array: (goal_pos) where goal_pos is the position
        """
        object_xpos = mujoco_utils.get_site_xpos(
            self.robot_model.model, self.robot_model.data, "object0"
        )
        goal_pos = np.array([0.75, 0, 0.68])
        goal_pos[2] = object_xpos[2] + np.random.uniform(0, 0.3)
        while np.linalg.norm(goal_pos[:2] - object_xpos[:2]) < 0.2:
            goal_pos[0] += np.random.uniform(-0.15, 0)
            goal_pos[1] += np.random.uniform(-0.3, 0.3)
        return goal_pos.copy()

    def render(self):
        """
        Render the environment based on the selected render mode.
        """

        self._render_callback()
        return self.robot_model.render()

    def close(self):
        """
        Clean up resources used by the environment.
        """
        self.robot_model.close()

    def _sample_object(self):
        """Sample a new initial position for the object.

        Returns:
            bool: True if successful
        """
        object_xpos = mujoco_utils.get_site_xpos(
            self.robot_model.model, self.robot_model.data, "object0"
        )
        object_x = object_xpos[0] + self.np_random.uniform(-0.2, 0.05)
        object_y = object_xpos[1] + self.np_random.uniform(-0.3, 0.3)
        object_xpos[:2] = np.array([object_x, object_y])
        object_qpos = mujoco_utils.get_joint_qpos(
            self.robot_model.model, self.robot_model.data, "object0:joint"
        )
        assert object_qpos.shape == (7,)
        object_qpos[:2] = object_xpos[:2]
        mujoco_utils.set_joint_qpos(
            self.robot_model.model, self.robot_model.data, "object0:joint", object_qpos
        )
        mujoco.mj_forward(self.robot_model.model, self.robot_model.data)
        return True

    def _render_callback(self):
        """Update the visualization of the target site."""
        sites_offset = (
            self.robot_model.data.site_xpos - self.robot_model.model.site_pos
        ).copy()
        site_id = mujoco.mj_name2id(
            self.robot_model.model, mujoco.mjtObj.mjOBJ_SITE, "target0"
        )
        self.robot_model.model.site_pos[site_id] = self.goal_pos - sites_offset[site_id]
        mujoco.mj_forward(self.robot_model.model, self.robot_model.data)

    @property
    def renderer(self):
        return self.robot_model.mujoco_renderer

class SparseRewardPickAndPlaceMujocoEnv(PickAndPlaceMujocoEnv):

    def __init__(
        self,
        env_config: dict,
        robot_class: RobotClass,
        xml_file_name: str = "combined_model",
        **kwargs,
    ):
        
        super().__init__(env_config,
                         robot_class,
                         xml_file_name,
                         **kwargs)
        
        self.rewards: PickAndPlaceSparseRewardCfg = PickAndPlaceSparseRewardCfg()