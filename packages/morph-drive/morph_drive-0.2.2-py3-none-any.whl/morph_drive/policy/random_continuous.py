import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .policy_base import PolicyBase


class RandomContinuousPolicy(PolicyBase):
    def __init__(self, action_space: gym.Space):
        """
        Initialize with a continuous action space.
        """
        if not isinstance(action_space, spaces.Box):
            raise TypeError(
                "RandomContinuousPolicy requires a continuous Box action space."
            )
        self.action_space = action_space

    def select_action(self, observation: np.ndarray) -> np.ndarray:
        """
        Select a random action by sampling from the continuous action space.
        """
        return self.action_space.sample()

    def train(self, *args, **kwargs) -> None:
        """
        No training needed for a random continuous policy.
        """

    def plot(self, *args, **kwargs) -> None:
        """
        No visualization available for random continuous policy.
        """
