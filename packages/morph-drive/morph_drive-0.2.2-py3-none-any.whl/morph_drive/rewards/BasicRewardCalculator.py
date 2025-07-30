import numpy as np

from . import RewardCalculatorBase


class BasicRewardCalculator(RewardCalculatorBase):
    """
    A basic reward calculator that computes reward components based on orientation (yaw, pitch, roll).
    - By default, it returns a 3-component tuple: (yaw, pitch, roll),
      where yaw is rewarded and pitch/roll are penalized for deviation from 0.
    - If a target orientation is provided, each component is rewarded based on closeness to the target.
    """

    def __init__(self, target_orientation: np.ndarray | None = None):
        """
        Initialize the reward calculator.
        """
        if target_orientation is not None:
            target_orientation = np.array(target_orientation, dtype=float)
            if target_orientation.shape != (3,):
                raise ValueError(
                    "target_orientation must be an array-like of shape (3,)."
                )
        self.target = target_orientation

    def calculate_reward(self, observation: np.ndarray, action: np.ndarray) -> tuple[float, float, float]:
        """
        Compute reward components from the observation.
        """
        yaw, pitch, roll = (
            float(observation[0]),
            float(observation[1]),
            float(observation[2]),
        )
        if self.target is not None:
            # Reward based on closeness to target orientation (higher is better when closer to target)
            target_yaw, target_pitch, target_roll = map(float, self.target)
            reward_yaw = -abs(yaw - target_yaw)
            reward_pitch = -abs(pitch - target_pitch)
            reward_roll = -abs(roll - target_roll)
        else:
            # Default: encourage yaw (treat higher yaw as better) and discourage any pitch/roll tilt
            reward_yaw = yaw
            reward_pitch = -abs(pitch)
            reward_roll = -abs(roll)

        return (reward_yaw, reward_pitch, reward_roll)
