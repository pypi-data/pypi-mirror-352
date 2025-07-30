from typing import Optional

import mujoco
import numpy as np
import gymnasium as gym
from os import path
from gymnasium import spaces
from gymnasium.utils.ezpickle import EzPickle
from sai_mujoco.base.robot.base_robot import RobotClass

from . import mdp
from sai_mujoco.base.mdp_cfg import *
from sai_mujoco.base.mdp_term import *

class WalkingSceneCfg(SceneCfg):

    def __init__(self,robot_model,terrain = "base_scene"):
        # 1. Move the end effector towards the club
        self.dir_path = path.dirname(path.dirname(path.dirname(path.realpath(__file__))))

        scene_xml = f"{self.dir_path}/assets/scene/{terrain}.xml"
        robot_xml = f"{self.dir_path}/assets/robots/{robot_model.name}/{robot_model.xml_file_name}.xml"

        if robot_model.sensor_model:
            sensor_xml = f"{self.dir_path}/assets/sensors/{robot_model.sensor_model.xml_file_name}.xml"
            self.sensor = SceneTerm(sensor_xml)

        self.scene = SceneTerm(scene_xml)

        self.robot = SceneTerm(robot_xml)
        
class WalkingRewardCfg(RewardCfg):
    """
    Reward configuration for the Walking environment.

    Reward Terms:
    """
    def __init__(self,robot_model: RobotClass):

        sensors = robot_model.sensor_model
        self.linear_vel_z = RewardTerm(func=mdp.get_sensor_norm, weight = 0.0, params={"sensor_name":sensors.velocimeter[0],"axis":[-1]})
        self.ang_vel_xy = RewardTerm(func=mdp.get_sensor_norm, weight = -0.15, params={"sensor_name":sensors.gyro[0],"axis":[0,1]})
        self.orientation = RewardTerm(func=mdp.get_sensor_norm, weight = -1.0, params={"sensor_name":sensors.framezaxis[0],"axis":[0,1]})
        self.base_height = RewardTerm(func=mdp.cost_base_height, weight = -20)
        self.cost_torques = RewardTerm(func=mdp.get_cost_torques, weight = -2e-4)
        self.action_rate = RewardTerm(func=mdp.get_action_rate, weight = -1.0)
        self.robot_energy = RewardTerm(func=mdp.get_robot_energy, weight = -2e-3)
        self.dof_qacc = RewardTerm(func=mdp.get_dof_acceleration, weight = -1e-7)
        self.dof_qvel = RewardTerm(func=mdp.get_dof_velocity, weight = -1e-4)
        self.foot_clearance = RewardTerm(func=mdp.get_foot_clearance, weight = 0.0)
        self.foot_slip = RewardTerm(func=mdp.get_foot_slip, weight = -0.1)
        self.survival = RewardTerm(func=mdp.is_alive, weight= 0.25)
        self.feet_distance = RewardTerm(func=mdp.get_feet_distance, weight=-1.0)

class WalkingTerminationCfg(TerminationCfg):
    """
    Termination configuration for the Pick-and-Place environment.

    Termination Terms:
    - success: Episode ends when the object is correctly placed at the target.
    """
    def __init__(self,robot_model: RobotClass):
        
        self.robot_fallen = DoneTerm(func=mdp.has_robot_fallen,params={"min_height": robot_model.standing_height[0],
                                                                       "max_height": robot_model.standing_height[1]})
        self.robot_data_nan = DoneTerm(func=mdp.is_data_nan)

class WalkingObsCfg(ObservationCfg):
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

        self.robot_state = ObsTerm(func=mdp.get_robot_obs)
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

class WalkingMujocoEnv(gym.Env, EzPickle):
    """
    A MuJoCo-based pick and place environment where a robot learns to pick up and place an object.

    This environment simulates a robotic system performing pick-and-place tasks with custom robot and environment configurations.
    It supports calculating rewards, determining termination conditions, and generating observations based on the robot's actions.

    Attributes:
        robot_model (object): The robot model used in the environment.
        rewards (WalkingRewardCfg): Configuration for the reward calculation.
        termination (WalkingTerminationCfg): Configuration for the termination condition.
        observations (WalkingObsCfg): Configuration for calculating observations.
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
        terrain: str = "base_scene",
        xml_file_name: str = "combined_model",
        **kwargs,
    ):
        """
        Initializes the WalkingMujocoEnv.

        Args:
            xml_file_name (str): Name of the combined XML model file.
        """
        
        # Reward, termination, and observation configurations specific to the golf course task.
        self.scene: WalkingSceneCfg = WalkingSceneCfg(robot_class,terrain)
        self.scene.compute()

        self.robot_model = robot_class(xml_file_name=xml_file_name, **kwargs)

        self.rewards : WalkingRewardCfg = WalkingRewardCfg(self.robot_model)
        self.termination : WalkingTerminationCfg = WalkingTerminationCfg(self.robot_model)
        self.observations: WalkingObsCfg = WalkingObsCfg(self.robot_model)

        # Initialize render mode and action space from the robot model.
        self.render_mode = self.robot_model.render_mode
        self.action_space = self.robot_model.action_space

        self.last_action = np.zeros(self.action_space.sample().shape)
        self.create_robot_ids()
        # Calculate the observation space based on the robot's configuration.
        obs = self.observations.calculate(self)
        self.observation_space = (
            spaces.Box(low=-np.inf, high=np.inf, shape=obs.shape, dtype=np.float32)
        )

    def compute_reward(self) -> float:
        """Compute the reward for the current state.
        """
        return self.rewards.calculate(self)

    def step(self, action):
        """
        Take a step in the environment based on the action and update the state.
        """

        self.action = action
        self.robot_model.step(action)
        obs = self.observations.calculate(self)
        # obs = self.observation_space.sample()
        reward = self.compute_reward()

        terminated = self.compute_terminated()

        self.last_action = action

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
        self.robot_model.reset(seed=seed)
        # obs = self.observation_space.sample()
        obs = self.observations.calculate(self)
        # self._reset_keyframe()

        return obs, {}

    def render(self):
        """
        Render the environment based on the selected render mode.
        """
        return self.robot_model.render()

    def close(self):
        """
        Clean up resources used by the environment.
        """
        self.robot_model.close()

    def create_robot_ids(self):

        foot_linvel_sensor_adr = []
        for site in self.robot_model.FEET_SITES:
            sensor_id = self.robot_model.model.sensor(f"{site}_global_linvel").id
            sensor_adr = self.robot_model.model.sensor_adr[sensor_id]
            sensor_dim = self.robot_model.model.sensor_dim[sensor_id]
            foot_linvel_sensor_adr.append(
                list(range(sensor_adr, sensor_adr + sensor_dim))
            )

        self._foot_linvel_sensor_adr = np.array(foot_linvel_sensor_adr)

        self._feet_site_id = np.array([self.robot_model.model.site(name).id for name in self.robot_model.FEET_SITES])
        self._left_feet_geom_id = np.array([self.robot_model.model.geom(name).id for name in self.robot_model.LEFT_FEET_GEOMS])
        self._right_feet_geom_id = np.array([self.robot_model.model.geom(name).id for name in self.robot_model.LEFT_FEET_GEOMS])
        self._floor_geom_id = self.robot_model.model.geom("floor").id
        self._site_id = self.robot_model.model.site("imu").id

    @property
    def renderer(self):
        return self.robot_model.mujoco_renderer
    