import numpy as np
import gymnasium as gym
import xml.etree.ElementTree as ET

class RewardTerm:
    """
    A class representing a single reward term in the reward configuration.

    A `RewardTerm` represents an individual reward component in the reward function,
    which is calculated by applying a function (e.g., based on the environment state)
    and scaling it by a specified weight. The term can have associated parameters that
    are passed to the function during the calculation.

    Attributes:
        func (callable): The function that calculates the reward based on the environment.
        weight (float): The weight by which the reward is scaled.
        params (dict): A dictionary of parameters to be passed to the reward function.

    Methods:
        calculate(env): Computes the weighted reward using the function and environment state.
    """

    def __init__(self, func, weight: float = 1.0, params: dict = {}):
        self.func = func
        self.weight = weight
        self.params = params

    def calculate(self, env: gym.Env) -> float:
        """
        Calculates the reward for the current environment state.

        Args:
            env: The environment object that holds the current state.

        Returns:
            float: The computed reward, scaled by the weight.
        """
        reward = self.weight * self.func(env, **self.params)
        return reward

class SceneTerm:

    def __init__(self, xml_name: str, params: dict = {}):

        self.xml_name = xml_name
        self.params = params

    def update_position(self, position: list, orientation: list, body_name: str):

        # Find <body name="robot">
        for body in self.root.iter("body"):
            if body.attrib.get("name") == body_name:
                body.set("pos", " ".join(map(str, position)))
                body.set("quat", " ".join(map(str, orientation)))
                break
        else:
            print("No <body name='robot'> found in the XML.")
            return

    def calculate(self):

        tree = ET.parse(self.xml_name)
        self.root = tree.getroot()
        if self.params:
            self.update_position(**self.params)

        return self.root

class ObsTerm:
    """
    A class representing a single observation term in the observation configuration.

    An `ObsTerm` is responsible for extracting a specific observation from the environment
    based on a function. It may also have associated parameters that are passed to the function
    to adjust the observation computation.

    Attributes:
        func (callable): The function that extracts an observation based on the environment.
        params (dict): A dictionary of parameters to be passed to the observation function.

    Methods:
        calculate(env): Computes the observation based on the function and environment state.
    """

    def __init__(self, func, params: dict = {}):
        self.func = func
        self.params = params

    def calculate(self, env: gym.Env) -> np.ndarray:
        """
        Calculates the observation for the current environment state.

        Args:
            env: The environment object that holds the current state.

        Returns:
            np.ndarray: The computed observation.
        """
        observation = self.func(env, **self.params)
        return observation


class DoneTerm:
    """
    A class representing a single termination condition term in the termination configuration.

    A `DoneTerm` checks if a certain condition is met to terminate the episode. The condition
    is determined by applying a function to the environment state, with optional parameters.

    Attributes:
        func (callable): The function that checks the termination condition based on the environment.
        params (dict): A dictionary of parameters to be passed to the termination function.

    Methods:
        calculate(env): Computes whether the episode is done based on the function and environment state.
    """

    def __init__(self, func, params: dict = {}):
        self.func = func
        self.params = params

    def calculate(self, env: np.ndarray) -> bool:
        """
        Checks if the episode is done based on the environment state.

        Args:
            env: The environment object that holds the current state.

        Returns:
            bool: True if the episode should terminate, False otherwise.
        """
        done = self.func(env, **self.params)
        return done
