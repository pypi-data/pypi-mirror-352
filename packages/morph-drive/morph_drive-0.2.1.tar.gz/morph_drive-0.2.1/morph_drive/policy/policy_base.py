import pickle
from abc import ABC, abstractmethod
from typing import Any, Optional

import numpy as np


class PolicyBase(ABC):
    """
    Abstract base class for reinforcement learning policies.
    Defines a general interface for both tabular and function-approximation-based policies.
    """

    @abstractmethod
    def select_action(self, observation: np.ndarray) -> Any:
        """
        Selects an action for the given state.
        Should be implemented by all RL policies (deterministic or stochastic).
        """

    @abstractmethod
    def train(self, *args, **kwargs) -> None:
        """
        Update policy parameters from experience.
        For tabular methods: expects (state, action, reward, next_state, done).
        For other methods: override as needed.
        """
        pass

    def save(self, filepath: str, data: Any) -> None:
        """
        Save the policy to a file, including the Q-table and current epsilon.
        """
        with open(filepath, "wb") as f:
            pickle.dump(data, f)

    def load(self, filepath: str) -> Any:
        """
        Load the policy from a file, restoring the Q-table and epsilon.
        """
        with open(filepath, "rb") as f:
            data = pickle.load(f)

        return data

    @abstractmethod
    def plot(self, *args, **kwargs) -> Optional[Any]:
        """
        Optional: Visualize policy or value function. Default is no-op.
        Implement if visualization is useful for your policy.
        """
        pass
