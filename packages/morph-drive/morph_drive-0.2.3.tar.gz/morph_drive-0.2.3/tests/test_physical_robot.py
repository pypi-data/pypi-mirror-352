import logging
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
from gymnasium.spaces import Box

from morph_drive.robots.physical_robot import PhyRobot

logging.disable(logging.CRITICAL)


class MockSerialCommunicator:
    def __init__(self, port, baud_rate, timeout, logger):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.logger = logger
        self.is_open_val = False

    def connect(self, retries=3, delay=2):
        self.is_open_val = True
        return True

    def close_connection(self):
        self.is_open_val = False

    def is_open(self):
        return self.is_open_val

    def read_line(self):
        return None

    def write_line(self, L):
        return True

    def wait_for_ready(self, s, t):
        return True


class ConcretePhyRobot(PhyRobot):
    def get_actuator_values(self):
        # This needs to be implemented by a concrete class
        # For tests, we can mock it or provide a dummy implementation
        return [0, 0, 0]

    def set_action_values(self, servo_angles):
        # This needs to be implemented by a concrete class
        return servo_angles  # Dummy

    def get_sensor_readings(self):
        # This needs to be implemented by a concrete class
        # For tests, this will often be mocked.
        return (0.0, 0.0, 0.0)


class TestPhyRobot(unittest.TestCase):
    def setUp(self):
        self.robot_name = "TestPhyBot"
        self.mock_obs_space = Box(low=-180, high=180, shape=(3,), dtype=np.float32)
        self.mock_action_space = Box(low=0, high=180, shape=(3,), dtype=np.float32)
        self.configs = {
            "port": "/dev/ttyFake",
            "baud_rate": 115200,
            "timeout": 1.0,
            "init_position": [90, 90, 90],
        }

    @patch(
        "morph_drive.robots.physical_robot.SerialCommunicator", MockSerialCommunicator
    )
    def create_robot_for_test(self):
        robot = ConcretePhyRobot(
            robot_name=self.robot_name,
            observation_space=self.mock_obs_space,
            action_space=self.mock_action_space,
            configs=self.configs,
        )
        robot.logger = MagicMock(spec=logging.Logger)
        return robot

    def test_reset_success(self):
        robot = self.create_robot_for_test()
        robot.reset_action_values = MagicMock(return_value=[90, 90, 90])
        robot.comm.write_line = MagicMock(return_value=True)

        obs, _ = robot.reset()

        robot.reset_action_values.assert_called_once()
        robot.comm.write_line.assert_called_once_with("W 90 90 90\n")
        np.testing.assert_array_equal(obs, np.array([0.0, 0.0, 0.0], dtype=np.float32))

    def test_get_observation_success(self):
        robot = self.create_robot_for_test()
        # Mock the concrete implementation of get_sensor_readings
        robot.get_sensor_readings = MagicMock(return_value=(10.0, 20.0, 30.0))

        obs = robot.get_observation()
        np.testing.assert_array_equal(
            obs, np.array([10.0, 20.0, 30.0], dtype=np.float32)
        )
        robot.get_sensor_readings.assert_called_once()
        self.assertIs(robot._last_obs, obs)  # Check if _last_obs is updated

    def test_get_observation_sensor_readings_none(self):
        robot = self.create_robot_for_test()
        robot.get_sensor_readings = MagicMock(return_value=None)

        obs = robot.get_observation()
        np.testing.assert_array_equal(obs, np.array([0.0, 0.0, 0.0], dtype=np.float32))
        robot.logger.warning.assert_called_with(
            "Received None from get_sensor_readings(). Defaulting observation."
        )

    def test_get_observation_sensor_readings_malformed_length(self):
        robot = self.create_robot_for_test()
        malformed_data = (10.0, 20.0)  # Tuple of 2, expected 3
        robot.get_sensor_readings = MagicMock(return_value=malformed_data)

        obs = robot.get_observation()
        np.testing.assert_array_equal(obs, np.array([0.0, 0.0, 0.0], dtype=np.float32))
        robot.logger.warning.assert_called_with(
            f"Received malformed sensor_readings (length {len(malformed_data)}): {malformed_data}. Defaulting observation."
        )

    def test_get_observation_sensor_readings_exception(self):
        robot = self.create_robot_for_test()
        test_exception = ValueError("Sensor comms error")
        robot.get_sensor_readings = MagicMock(side_effect=test_exception)

        obs = robot.get_observation()
        np.testing.assert_array_equal(obs, np.array([0.0, 0.0, 0.0], dtype=np.float32))
        robot.logger.error.assert_called_with(
            f"Error getting or parsing sensor readings: {test_exception}. Defaulting observation."
        )

    @patch("builtins.print")
    def test_render_success(self, mock_print):
        robot = self.create_robot_for_test()
        expected_actuator_values = [90, 95, 100]
        robot.get_actuator_values = MagicMock(return_value=expected_actuator_values)

        robot.render()
        mock_print.assert_called_once_with(
            f"[{self.robot_name}] Actuator Values: {expected_actuator_values}"
        )

    @patch("builtins.print")
    def test_render_get_actuator_values_exception(self, mock_print):
        robot = self.create_robot_for_test()
        test_exception = Exception("Failed to get actuators")
        robot.get_actuator_values = MagicMock(side_effect=test_exception)

        robot.render()

        # Check both logger call and print output
        robot.logger.error.assert_called_once_with(
            f"Error getting actuator values for rendering: {test_exception}"
        )
        mock_print.assert_called_once_with(
            f"[{self.robot_name}] Actuator Values: Error retrieving values"
        )


if __name__ == "__main__":
    unittest.main()
