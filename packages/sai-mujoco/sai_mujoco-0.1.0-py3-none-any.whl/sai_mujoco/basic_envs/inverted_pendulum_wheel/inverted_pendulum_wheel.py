import os
import numpy as np

from gymnasium import utils
from gymnasium.envs.mujoco.mujoco_env import MujocoEnv
from gymnasium.spaces import Box

from sai_mujoco.utils.env import SAIMujocoBase

DEFAULT_CAMERA_CONFIG: dict[str, float | int] = {
    "trackbodyid": 0,
    "distance": 3,
}

FRAMERATE = 60
SCREEN_HEIGHT = 704
SCREEN_WIDTH = 1200


class InvertedPendulumWheelEnv(MujocoEnv, utils.EzPickle, SAIMujocoBase):
    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
        "render_fps": FRAMERATE,
        "width": SCREEN_WIDTH,
        "height": SCREEN_HEIGHT,
        "engine": "mujoco",
    }

    """
    ## Description
    This environment involves a pole balancing on a wheel. The goal is to keep the pole upright by applying torque to the wheel.

    ## Action Space
    The agent takes a 1-element vector for actions.
    The action space is a continuous `(action)` in `[-3, 3]`, where `action` represents
    the numerical torque applied to the wheel.

    | Num | Action                    | Control Min | Control Max | Name (in XML file) | Joint | Unit      |
    |-----|---------------------------|-------------|-------------|-------------------|-------|-----------|
    | 0   | Torque applied to wheel   | -3         | 3          | wheel_joint       | hinge | Torque (N-m) |

    ## Observation Space
    The observation is a `ndarray` with shape `(4,)` with the following elements:

    | Num | Observation                             | Min  | Max | Name (in XML file) | Joint | Unit                     |
    |-----|----------------------------------------|------|-----|-------------------|-------|--------------------------|
    | 0   | Wheel angular position                  | -Inf | Inf | wheel_joint       | hinge | angle (rad)             |
    | 1   | Pole vertical angle                     | -Inf | Inf | pendulum_hinge    | hinge | angle (rad)             |
    | 2   | Wheel angular velocity                  | -Inf | Inf | wheel_joint       | hinge | angular velocity (rad/s) |
    | 3   | Pole angular velocity                   | -Inf | Inf | pendulum_hinge    | hinge | angular velocity (rad/s) |

    ## Rewards
    The goal is to keep the inverted pendulum upright (within a certain angle limit)
    as long as possible. A reward of +1 is awarded for each timestep that the pole
    remains upright.

    ## Starting State
    All observations start in state (0.0, 0.0, 0.0, 0.0) with uniform noise in the
    range [-0.01, 0.01] added for stochasticity.

    ## Episode End
    The episode ends when any of the following occurs:
    1. Truncation: Episode duration reaches 1000 timesteps
    2. Termination: Any state space value is no longer finite
    3. Termination: Absolute value of pole's vertical angle exceeds 0.5 radians
    """

    def __init__(self, show_overlay: bool = False, **kwargs):
        utils.EzPickle.__init__(self, **kwargs)
        observation_space = Box(low=-np.inf, high=np.inf, shape=(4,), dtype=np.float64)
        MujocoEnv.__init__(
            self,
            os.path.join(
                os.path.dirname(__file__), "assets", "inverted_pendulum_wheel.xml"
            ),
            1,
            observation_space=observation_space,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            default_camera_config=DEFAULT_CAMERA_CONFIG,
            **kwargs,
        )
        self._toggle_overlay(show_overlay, kwargs["render_mode"])

    def step(self, action):
        # rescale action
        if self.rescale_bool:
            action = self._rescale_action(action)

        self.do_simulation(action, self.frame_skip)
        ob = self._get_obs()

        # terminate if the angle of the pole is > 0.3 radians
        terminated = bool(not np.isfinite(ob).all() or (np.abs(ob[1]) > 0.5))
        reward = -1 if terminated else 1

        self.iteration += 1

        info = {
            "iteration": self.iteration,
        }

        return ob, reward, terminated, False, info

    def reset(self, **kwargs):
        super().reset(**kwargs)

        self.iteration = 0

        info = {
            "iteration": self.iteration,
        }

        return self._get_obs(), info

    def reset_model(self):
        qpos = self.init_qpos + self.np_random.uniform(
            size=self.model.nq, low=-0.01, high=0.01
        )
        qvel = self.init_qvel + self.np_random.uniform(
            size=self.model.nv, low=-0.01, high=0.01
        )
        self.set_state(qpos, qvel)
        return self._get_obs()

    def _get_obs(self):
        wheel_angular_pos: float = self.data.qpos[1]
        wheel_angular_vel: float = self.data.qvel[1]
        pendulum_angular_pos: float = self.data.qpos[2]
        pendulum_angular_vel: float = self.data.qvel[2]

        return np.array(
            [
                wheel_angular_pos,
                pendulum_angular_pos,
                wheel_angular_vel,
                pendulum_angular_vel,
            ]
        )
