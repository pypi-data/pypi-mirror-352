import unittest

import numpy as np
from gymnasium.spaces import Box

from morph_drive.policy.do_nothing import DoNothingPolicy


class TestDoNothingPolicy(unittest.TestCase):
    def test_get_action_returns_zero_array_for_discrete(self):
        action_space = Box(low=-1.0, high=1.0, shape=(3,))
        policy = DoNothingPolicy(action_space)
        observation = np.array([1, 2, 3])
        action = policy.select_action(observation)
        self.assertTrue(np.array_equal(action, np.zeros(3)))

    def test_get_action_returns_zero_array_for_continuous(self):
        action_space = Box(low=-1.0, high=1.0, shape=(3,), dtype=np.float32)
        policy = DoNothingPolicy(action_space)
        observation = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        action = policy.select_action(observation)
        self.assertTrue(np.array_equal(action, np.zeros(3, dtype=np.float32)))


if __name__ == "__main__":
    unittest.main()
