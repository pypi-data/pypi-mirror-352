from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .policy_base import PolicyBase


class RandomDiscretePolicy(PolicyBase):
    def __init__(self, action_space: gym.Space):
        """
        Initialize the policy with an action space.
        """

        if not isinstance(action_space, (spaces.Discrete, spaces.MultiDiscrete)):
            raise TypeError(
                "RandomDiscretePolicy requires a Discrete or MultiDiscrete action space."
            )
        self.action_space = action_space

    def select_action(self, observation: np.ndarray) -> Any:
        """
        Select a random action from the discrete action space.
        """
        return self.action_space.sample()

    def train(self, *args, **kwargs) -> None:
        """
        No training needed for a random discrete policy.
        """

    def plot(self, *args, **kwargs) -> None:
        """
        No visualization available for random discrete policy.
        """
