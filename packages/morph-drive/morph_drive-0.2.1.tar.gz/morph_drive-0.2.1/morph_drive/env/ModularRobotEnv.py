from typing import Any, Callable

import gymnasium as gym
import numpy as np

from ..pre_processors import BasicDataPreprocessor as preprocessor
from ..pre_processors import DataPreprocessorBase
from ..rewards import BasicRewardCalculator as rewardCalculator
from ..rewards import RewardCalculatorBase
from ..robots import RobotInterface


class ModularRobotEnv(gym.Env):
    """
    A unified Gymnasium environment that composes modular components for RL.
    It supports both real and simulated robots by using a RobotInterface instance,
    and uses DataPreprocessor and RewardCalculator modules for observation and reward processing.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        robot: RobotInterface,
        data_preprocessor: DataPreprocessorBase | None = None,
        reward_calculator: RewardCalculatorBase | None = None,
        termination_condition: Callable | None = None,
        truncation_condition: Callable | None = None,
        goal: np.ndarray | None = None,
        configs: dict[str, Any] | None = None
    ):
        """
        Initialize the modular environment.
        """
        super().__init__()
        self.robot = robot
        self.observation_space = robot.get_observation_space()
        self.action_space = robot.get_action_space()

        self.metadata = {**robot.metadata}

        # Initialize modules (use defaults if not provided)
        self.preprocessor = data_preprocessor or preprocessor.BasicDataPreprocessor()
        self.reward_calc = reward_calculator or rewardCalculator.BasicRewardCalculator(
            target_orientation=goal
        )
        self.termination_condition = termination_condition or (lambda obs: False)
        self.truncation_condition = truncation_condition or (lambda obs: False)
        self.goal = goal

        # Set the action and observation spaces to match the robot interface
        self.action_space = self.robot.get_action_space()
        self.observation_space = self.robot.get_observation_space()

        self.step_count = 0
        self.configs = configs or {}


    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        """
        Reset the environment to an initial state and return the first observation.
        """

        # Gymnasium's internal seeding if needed
        super().reset(seed=seed)

        # Reset the robot or simulation to its initial configuration
        self.robot.reset()

        self.step_count = 0

        # Obtain initial sensor data and preprocess it to form the initial observation
        observation = self.robot.get_observation()
        return observation, {}

    def step(self, action: Any):
        """
        Run one step of the environment's dynamics.
        """

        # Apply the action to the robot or simulation
        self.robot.apply_action(action)

        # Get raw sensor data after the action and convert to observation
        raw_data = self.robot.get_observation()
        observation = self.preprocessor.process(raw_data)

        # Compute reward components using the reward calculator
        reward_components = self.reward_calc.calculate_reward(observation, action)

        # Sum reward components to get a scalar reward (suitable for single-objective RL)
        if isinstance(reward_components, (tuple, list, np.ndarray)):
            total_reward = float(np.sum(reward_components))
        else:
            total_reward = float(reward_components)
            reward_components = (total_reward,)

        self.step_count += 1

        # Info can include detailed reward components or other diagnostic data
        info = {
            "observation": observation,
            "reward_components": reward_components,
            "step_count": self.step_count,
        }

        # Determine if the episode is terminated (e.g., if goal is achieved).
        # Here, as an example, consider the episode done if pitch and roll are within 5 degrees of 0 (upright).
        terminated = self.termination_condition({**info, **self.configs})
        truncated = self.truncation_condition({**info, **self.configs})
        return observation, total_reward, terminated, truncated, info

    def render(self, mode: str = "human"):
        """
        Render the environment state.
        """
        self.robot.render()

    def close(self):
        """
        Clean up the environment (close connections or simulation).
        """
        self.robot.close()

    def __del__(self):
        """
        Destructor to ensure resources are cleaned up when the object is deleted.
        """
        self.close()