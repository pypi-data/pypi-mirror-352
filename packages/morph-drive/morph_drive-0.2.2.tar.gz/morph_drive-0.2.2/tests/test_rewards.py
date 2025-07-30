import unittest

import numpy as np

from morph_drive.rewards.BasicRewardCalculator import BasicRewardCalculator


class TestBasicRewardCalculator(unittest.TestCase):
    def test_calculate_reward_simple(self):
        target_yaw = 10.0
        target_pitch = 10.0
        target_roll = 10.0

        calculator = BasicRewardCalculator(
            target_orientation=np.array([target_yaw, target_pitch, target_roll])
        )

        yaw = 120.0
        pitch = 12.5
        roll = -1.5

        observation = np.array([yaw, pitch, roll])
        action = np.array([0, 0, 0])

        reward = calculator.calculate_reward(observation, action)
        expected_reward = (
            -abs(yaw - target_yaw),
            -abs(pitch - target_pitch),
            -abs(roll - target_roll),
        )
        self.assertEqual(reward, expected_reward)

    def test_calculate_reward_simple_when_no_target(self):
        calculator = BasicRewardCalculator()

        yaw = 120.0
        pitch = 12.5
        roll = -1.5

        observation = np.array([yaw, pitch, roll])
        action = np.array([0, 0, 0])

        reward = calculator.calculate_reward(observation, action)
        expected_reward = (
            yaw,
            -abs(pitch),
            -abs(roll),
        )
        self.assertEqual(reward, expected_reward)


if __name__ == "__main__":
    unittest.main()
