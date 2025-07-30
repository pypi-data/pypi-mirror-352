import numpy as np
import gymnasium as gym
from copy import deepcopy
import xml.etree.ElementTree as ET

class RewardCfg:
    """
    A configuration class for calculating rewards in a reinforcement learning environment.

    This class is responsible for aggregating rewards based on various reward terms defined at the class level.
    Each reward term is expected to have a `calculate` method that returns a numerical reward when called with the environment.

    Methods:
        calculate(env): Aggregates rewards from all reward terms defined at the class level based on the environment state.
    """

    def calculate(self, env: gym.Env) -> float:
        """
        Calculate the total reward for the current state of the environment.

        Iterates over all class-level attributes that have a `calculate` method and computes the sum of their individual rewards.

        Args:
            env: The environment object that holds the current state.

        Returns:
            float: The total reward calculated by summing individual rewards.
        """
        reward = 0

        # Iterate over all class-level attributes (not instance-level)
        for name, attr in vars(self).items():
            if hasattr(attr, "calculate") and callable(attr.calculate):
                reward += attr.calculate(env)

        return reward


class ObservationCfg:
    """
    A configuration class for calculating observations in a reinforcement learning environment.

    This class is responsible for collecting the current state of the environment into a single observation,
    by iterating over class-level attributes that each define how to extract a part of the observation.

    Methods:
        calculate(env): Aggregates observations from all observation terms defined at the class level based on the environment state.
    """

    def calculate(self, env: gym.Env) -> np.ndarray:
        """
        Calculate the full observation for the current state of the environment.

        Iterates over all class-level attributes that have a `calculate` method and concatenates their individual observations.

        Args:
            env: The environment object that holds the current state.

        Returns:
            np.ndarray: The concatenated observation vector for the current environment state.
        """
        observation = []

        # Iterate over all class-level attributes (not instance-level)
        for name, attr in vars(self).items():
            if hasattr(attr, "calculate") and callable(attr.calculate):
                obs = attr.calculate(env)
                observation.append(obs)

        return np.concatenate(observation).astype(np.float32)

class TerminationCfg:
    """
    A configuration class for calculating the termination condition in a reinforcement learning environment.

    This class defines the logic for determining whether the episode has ended, by evaluating multiple termination conditions.

    Methods:
        calculate(env): Checks all termination conditions and returns True if the episode should terminate, False otherwise.
    """

    def calculate(self, env: gym.Env) -> bool:
        """
        Determine if the current episode should terminate.

        Iterates over all class-level attributes that have a `calculate` method and evaluates them.
        If any condition returns `False`, the episode is not terminated.

        Args:
            env: The environment object that holds the current state.

        Returns:
            bool: True if the episode should terminate, False otherwise.
        """
        # Iterate over all class-level attributes (not instance-level)
        for name, attr in vars(self).items():
            if hasattr(attr, "calculate") and callable(attr.calculate):
                done = attr.calculate(env)
                if done:
                    return True

        return False

class SceneCfg:
    """
    A configuration class for calculating the termination condition in a reinforcement learning environment.

    This class defines the logic for determining whether the episode has ended, by evaluating multiple termination conditions.

    Methods:
        calculate(env): Checks all termination conditions and returns True if the episode should terminate, False otherwise.
    """

    scene = None
    robot = None
    env = None
    sensor = None

    merge_order = ["scene", "robot", "env", "sensor"]

    def merge_tag_elements(self,source_root):
        for child in source_root:
            if child.tag in self.tag_map:
                self.tag_map[child.tag].extend(deepcopy(child))
            else:
                # Add other tags directly if not in merge list
                self.merged_root.append(deepcopy(child))

    def compute(self) -> bool:
        """
        Determine if the current episode should terminate.

        Iterates over all class-level attributes that have a `calculate` method and evaluates them.
        If any condition returns `False`, the episode is not terminated.

        Args:
            env: The environment object that holds the current state.

        Returns:
            bool: True if the episode should terminate, False otherwise.
        """

        self.merged_root = ET.Element("mujoco")

        self.merge_tags = ["size", "default", "asset",
                  "worldbody", "actuator", "sensor", "tendon", "contact", "equality"]

        self.tag_map = {tag: ET.Element(tag) for tag in self.merge_tags}

        # Iterate over all class-level attributes (not instance-level)
        for name in self.merge_order:
            attr = getattr(self, name)
            if hasattr(attr, "calculate") and callable(attr.calculate):
                root = attr.calculate()
                self.merge_tag_elements(root)

        for tag in self.merge_tags:
            if len(self.tag_map[tag]) > 0:
                self.merged_root.append(self.tag_map[tag])

        # Create final tree
        merged_tree = ET.ElementTree(self.merged_root)
        file_location = f"{self.dir_path}/assets/combined_model.xml"
        merged_tree.write(file_location)
