from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .policy_base import PolicyBase


class DoNothingPolicy(PolicyBase):
    """
    A simple heuristic policy that always takes a neutral or 'no-op' action.
    - For MultiDiscrete spaces, it selects the middle value (assumed no-change).
    - For Discrete spaces, it selects a middle index (or 0 if only two values).
    - For continuous (Box) spaces, it selects the midpoint of the action range.
    """

    def __init__(self, action_space: gym.Space):
        """
        Initialize the policy with an action space and precompute the neutral action.
        """
        self.action_space = action_space

        # Determine the neutral action based on space type
        if isinstance(action_space, spaces.MultiDiscrete):
            # Middle value for each discrete dimension
            self.neutral_action = np.array(
                [(n - 1) // 2 for n in action_space.nvec], dtype=action_space.dtype
            )

        elif isinstance(action_space, spaces.Discrete):
            # Middle index for discrete (if even number of actions, floor division gives low-mid index)
            if action_space.n > 1:
                self.neutral_action = (action_space.n - 1) // 2
            else:
                self.neutral_action = 0

        elif isinstance(action_space, spaces.Box):
            # Midpoint of continuous range for each dimension
            mid = (action_space.high + action_space.low) / 2.0
            # Ensure the midpoint adheres to the space's dtype
            self.neutral_action = mid.astype(action_space.dtype)

        else:
            raise TypeError(
                "DoNothingPolicy requires a Discrete, MultiDiscrete, or Box action space."
            )

    def select_action(self, observation: np.ndarray) -> Any:
        """
        Always return the precomputed neutral action.
        """
        return self.neutral_action

    def train(self, *args, **kwargs) -> None:
        """
        No training needed for a do-nothing policy.
        This method is a no-op.
        """

    def plot(self, *args, **kwargs) -> None:
        """
        No visualization needed for a do-nothing policy.
        This method is a no-op.
        """
