from abc import ABC, abstractmethod

import numpy as np


class RewardCalculatorBase(ABC):
    """Abstract base class for reward calculation modules."""

    @abstractmethod
    def calculate_reward(self, observation: np.ndarray, action: np.ndarray) -> tuple[float, ...]:
        """
        Calculate the reward components based on the current observation (and optionally the goal or state).
        """
        pass
