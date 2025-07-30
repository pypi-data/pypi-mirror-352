from abc import ABC, abstractmethod
from typing import Any

import gymnasium as gym

# TODO fix this with modifying the import structure

# # Attempt to import the provided Robot (for real hardware) and MuJoCo environment classes
# try:
#     from scripts.robot import Robot  # Real robot control class (serial communication)
# except ImportError:
#     Robot = None
# try:
#     from env import (
#         OrigamiTriangularRobotEnv,  # MuJoCo Gymnasium environment for simulation
#     )
# except ImportError:
#     OrigamiTriangularRobotEnv = None


class RobotInterface(ABC):
    """Interface for robot control in various environments (real or simulated)."""

    metadata: dict = {
        "render_modes": [
            "human",
        ],
    }

    def __init__(self):
        """Initialize default attributes."""
        self._last_obs = None
        self._reward = None
        self._done = False
        self._truncated = False
        self._info = {}

    @abstractmethod
    def get_action_space(self) -> gym.Space:
        """Return the Gym action space for this robot (discrete or continuous)."""
        pass

    @abstractmethod
    def get_observation_space(self) -> gym.Space:
        """Return the Gym observation space for this robot."""
        pass

    @abstractmethod
    def render(self):
        """
        Render the robot or simulation.
        """
        pass

    @abstractmethod
    def reset(self, *, seed=None, options=None) -> None:
        """
        Reset the robot to an initial state.
        This may involve resetting positions or simulation state.
        """
        pass

    @abstractmethod
    def apply_action(self, action: Any) -> None:
        """
        Apply the given action to the robot or simulation.
        For a real robot, send the command to actuators.
        For simulation, step the simulation with the action.
        """
        pass

    @abstractmethod
    def get_observation(self) -> Any:
        """
        Get the latest pre-processed sensor data mapped into observation space from the robot or simulation.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Clean up resources (e.g., close connections or shut down simulation)."""
        pass

    def get_reward(self) -> float | None:
        """
        Get the reward from the last simulation step.
        """
        return self._reward

    def is_done(self) -> bool:
        """
        Check if the simulation has reached a terminal state.
        """
        return self._done

    def is_truncated(self) -> bool:
        """
        Check if the simulation was truncated.
        """
        return self._truncated

    def get_info(self) -> dict | None:
        """
        Get additional information from the last simulation step.
        """
        return self._info if self._info else {}
