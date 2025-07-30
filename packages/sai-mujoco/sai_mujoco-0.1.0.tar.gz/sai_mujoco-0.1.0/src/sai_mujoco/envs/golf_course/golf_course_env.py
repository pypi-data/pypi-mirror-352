from typing import Optional, Union

import mujoco
import numpy as np

import gymnasium as gym
from gymnasium import spaces
from gymnasium.utils.ezpickle import EzPickle

from sai_mujoco.base.robot.base_robot import RobotClass
from . import mdp
from os import path

from sai_mujoco.base.mdp_cfg import RewardCfg, SceneCfg, TerminationCfg, ObservationCfg
from sai_mujoco.base.mdp_term import RewardTerm, DoneTerm, ObsTerm, SceneTerm
from sai_mujoco.utils.env import SAIMujocoBase

class GolfCourseSceneCfg(SceneCfg):

    def __init__(self,env_config,robot_model):
        # 1. Move the end effector towards the club
        self.dir_path = path.dirname(path.dirname(path.dirname(path.realpath(__file__))))

        scene_xml = f"{self.dir_path}/assets/scene/base_scene.xml"
        env_xml = f"{self.dir_path}/assets/envs/golf_course/golf_course_env.xml"
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
        
class GolfCourseRewardCfg(RewardCfg):
    """
    Reward configuration for the GolfCourse environment.

    Terms:
    - approach_ee_club_grip: Reward for moving the end-effector toward the club grip.
    - align_ee_handle: Reward for aligning the end-effector with the club handle.
    - approach_gripper_handle: Reward for the gripper approaching the handle (grasp phase).
    - approach_ball_hole: Reward for bringing the ball closer to the hole.
    - joint_vel: Penalty for joint velocity (smoothness/efficiency incentive).
    - club_dropped: Heavy penalty if the club is dropped.
    - ball_passed_hole: Penalty if the ball overshoots the hole.
    - ball_in_hole: Reward for successful task completion (ball enters hole).
    """

    def __init__(self):
        # 1. Move the end effector towards the club
        self.approach_ee_club_grip = RewardTerm(
            func=mdp.approach_ee_club_grip, weight=0.8
        )

        # 2. Align the end effector with club handle
        self.align_ee_handle = RewardTerm(func=mdp.align_ee_handle, weight=0.5)

        # 3. Penalize for smoothness
        self.approach_gripper_handle = RewardTerm(
            func=mdp.approach_gripper_handle, weight=5.0, params={"offset": 0.04}
        )

        # 4. Approach ball to the hole
        self.approach_ball_hole = RewardTerm(func=mdp.approach_ball_hole, weight=3.0)

        # 5. Penalize actions for cosmetic reasons
        self.joint_vel = RewardTerm(func=mdp.joint_vel_l2, weight=-0.0001)

        # 6. Penalize if the club is dropped
        self.club_dropped = RewardTerm(
            func=mdp.club_dropped, params={"minimum_height": 0.25}, weight=-50.0
        )

        # 7. Penalize if the ball passed the hole
        self.ball_passed_hole = RewardTerm(func=mdp.ball_passed_hole, weight=-50.0)

        # 8. Positive Reward if ball is in the hole
        self.ball_in_hole = RewardTerm(func=mdp.ball_in_hole, weight=20.0)


class GolfCourseTerminationCfg(TerminationCfg):
    """
    Termination configuration for the GolfCourse environment.

    Terms:
    - club_dropping: Terminates episode if the club is dropped below a minimum height.
    - ball_passed_hole: Terminates if the ball overshoots the hole.
    - success: Terminates successfully if the ball enters the hole.
    """

    def __init__(self):
        # 1. If the club is dropped
        self.club_dropping = DoneTerm(
            func=mdp.club_dropped, params={"minimum_height": 0.25}
        )

        # 2. If the ball passed the hole
        self.ball_passed_hole = DoneTerm(func=mdp.ball_passed_hole)

        # 3. If the episode was success
        self.success = DoneTerm(func=mdp.ball_in_hole)


class GolfCourseObsCfg(ObservationCfg):
    """
    Observation configuration for the GolfCourse environment.

    Terms:
    - robot_state: General robot joint positions, velocities, etc.
    - ball_xpos: 3D position of the golf ball.
    - hole_xpos: 3D position of the hole (flag assembly).
    - golf_club_xpos: 3D position of the club’s grip link.
    - golf_club_quat: Orientation (quaternion) of the club’s head.
    """

    def __init__(self, robot_model: RobotClass):
        # 1. Robot state
        self.robot_state = ObsTerm(func=mdp.get_robot_obs)

        # 2. Ball Position
        self.ball_xpos = ObsTerm(
            func=mdp.get_object_position, params={"object_name": "golf_ball"}
        )

        # 3. Hole Position
        self.hole_xpos = ObsTerm(
            func=mdp.get_object_position, params={"object_name": "flag_assembly"}
        )

        # 4. Golf clubs position
        self.golf_club_xpos = ObsTerm(
            func=mdp.get_object_position, params={"object_name": "grip_link"}
        )

        # 5. Golf clubs orientation
        self.golf_club_quat = ObsTerm(
            func=mdp.get_object_quat, params={"object_name": "head_link"}
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

class GolfCourseMujocoEnv(gym.Env, EzPickle, SAIMujocoBase):
    """
    A MuJoCo-based robotic manipulation environment where a robot learns to grasp a golf club and putt a ball into a hole.

    This environment is used to simulate a robot learning golf-related tasks, including grasping a golf club and performing a putt
    to a hole. The robot's actions are based on observation space defined by the state of the environment, and rewards are computed
    based on specific golf-related actions.

    Attributes:
        golf_ball_id (int): Body ID for the golf ball.
        golf_hole_id (int): Body ID for the hole/flag assembly.
        golf_club_id (int): Body ID for the club grip.
        club_head_id (int): Body ID for the club head.
        left_finger_id (int): Body ID for the left finger of the gripper.
        right_finger_id (int): Body ID for the right finger of the gripper.
        ee_id (int): Site ID for the robot's end effector.
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
        keyframe: Union[str,dict] = "random",
        xml_file_name: str = "combined_model",
        show_overlay: bool = False,
        **kwargs,
    ):
        """
        Initializes the GolfCourseMujocoEnv.

        Args:
            xml_file_name (str): Name of the combined XML model file.
        """

        # Reward, termination, and observation configurations specific to the golf course task.
        self.scene: GolfCourseSceneCfg = GolfCourseSceneCfg(env_config, robot_class)
        self.scene.compute()

        # Dynamically import the robot class based on the configuration.
        self.robot_model = robot_class(xml_file_name=xml_file_name, **kwargs)

        self.rewards: GolfCourseRewardCfg = GolfCourseRewardCfg()
        self.termination: GolfCourseTerminationCfg = GolfCourseTerminationCfg()
        self.observations: GolfCourseObsCfg = GolfCourseObsCfg(self.robot_model)

        # Set the environment-specific IDs for various objects (e.g., golf ball, golf hole).
        self.set_env_ids()
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

        # Define Base Scene for the Golf environment 

        self.golf_keyframe = {
            "init_qpos" : [0.5, 0, 0.038, 0, 0, 0, 0, 0.7, 0, 0.025, 0.7071, 0, 0, 0.7071],
            "ctr" : [],
            "qvel" : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "mpos" : [],
            "mquat" : [] 
        }

        if self.keyframe != "random":
            self._create_keyframe()

    def compute_reward(self) -> float:
        """Compute the reward for the current state."""
        return self.rewards.calculate(self)

    def step(self, action: np.ndarray):
        """
        Take a step in the environment based on the action and update the state.
        """
        self.robot_model.step(action)
        obs = self.observations.calculate(self)
        reward = self.compute_reward()
        terminated = self.compute_terminated()

        return obs, reward, terminated, False, {}

    def compute_terminated(self) -> bool:
        """
        Compute whether the current episode has terminated based on specific criteria.
        """
        return self.termination.calculate(self)

    def reset(self, *, seed: Optional[int] = None, **kwargs):
        """
        Reset the environment to an initial state.
        """
        self.robot_model.reset(seed=seed)
        self._reset_keyframe(seed)
        obs = self.observations.calculate(self)

        return obs, {}

    def _reset_keyframe(self, seed):

        if self.keyframe == "random":
            self.robot_model._random_keyframe(self.golf_keyframe, seed)
        else:
            self.robot_model._reset_keyframe(self.complete_keyframe)

        for _ in range(self.robot_model.frame_skip):
            mujoco.mj_step(self.robot_model.model, self.robot_model.data)

    def _create_keyframe(self):

        if self.keyframe in self.robot_model.keyframes:
            robot_keyframe = self.robot_model.keyframes[self.keyframe]
        else:
            robot_keyframe = self.keyframe

        self.complete_keyframe = {
            "init_qpos": robot_keyframe["init_qpos"] + self.golf_keyframe["init_qpos"],
            "ctr": robot_keyframe["ctr"] + self.golf_keyframe["ctr"],
            "qvel": robot_keyframe["qvel"] + self.golf_keyframe["qvel"],
            "mpos": robot_keyframe["mpos"] + self.golf_keyframe["mpos"],
            "mquat": robot_keyframe["mquat"] + self.golf_keyframe["mquat"]
        }

    def render(self):
        """
        Render the environment based on the selected render mode.
        """
        return self.robot_model.render()

    def set_env_ids(self):
        """
        Set the environment-specific IDs for the golf ball, hole, club, and gripper components.
        """

        # Set body IDs for various objects like golf ball, golf hole, and the golf club.
        self.golf_ball_id = self.robot_model.model_names.body_name2id["golf_ball"]
        self.golf_hole_id = self.robot_model.model_names.body_name2id["flag_assembly"]
        self.golf_club_id = self.robot_model.model_names.body_name2id["grip_link"]
        self.club_head_id = self.robot_model.model_names.body_name2id["head_link"]
        self.left_finger_id = self.robot_model.model_names.body_name2id[
            self.robot_model.left_finger
        ]
        self.right_finger_id = self.robot_model.model_names.body_name2id[
            self.robot_model.right_finger
        ]
        self.ee_id = self.robot_model.model.site(self.robot_model.gripper_link).id

    def close(self):
        """
        Clean up resources used by the environment.
        """
        self.robot_model.close()

    @property
    def renderer(self):
        return self.robot_model.mujoco_renderer