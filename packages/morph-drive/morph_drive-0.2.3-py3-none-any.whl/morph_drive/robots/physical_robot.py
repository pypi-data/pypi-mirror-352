import logging
from abc import abstractmethod
from time import sleep
from types import TracebackType
from typing import Any, List, Optional, Type

import gymnasium
import numpy as np

from . import RobotInterface
from .serial_communicator import SerialCommunicator


class PhyRobot(RobotInterface):
    """
    Implementation of RobotInterface for a real serial-based robot.
    Uses the SerialCommunicator class to handle serial communication.
    """

    # Only as per required by Gym interface
    metadata = {"render_modes": ["human"], "render_fps": 30}

    observation_space: gymnasium.spaces.Space
    action_space: gymnasium.spaces.Space

    def __init__(
        self,
        robot_name: str = "PhyRobot",
        observation_space: gymnasium.spaces.Space | None = None,
        action_space: gymnasium.spaces.Space | None = None,
        configs: dict[str, Any] | None = None,
    ):
        super().__init__()

        if configs is None:
            configs = {}

        self.logger = logging.getLogger(__name__)
        self.debug = bool(configs.get("debug", False))

        # Create SerialCommunicator instance
        self.comm = SerialCommunicator(
            port=str(configs.get("port", "/dev/ttyUSB0")),
            baud_rate=int(configs.get("baud_rate", 115200)),
            timeout=float(configs.get("timeout", 1.0)),
            logger=self.logger,
        )

        self.robot_name = robot_name

        if observation_space is None:
            raise ValueError("Observation space must be provided.")

        if action_space is None:
            raise ValueError("Action space must be provided.")

        self.observation_space = observation_space
        self.action_space = action_space

        self.position: list[int] = []

        if configs.get("init_position"):
            init_position = configs.get("init_position")
            if isinstance(init_position, (list, tuple)):
                self.position = [int(v) for v in init_position]
            else:
                raise ValueError(
                    "Invalid type for 'init_position'. Expected list, or tuple."
                )
        else:
            if self.action_space and hasattr(self.action_space, "shape"):
                self.position = [0] * self.action_space.shape[0]  # type: ignore
            else:
                raise ValueError(
                    "Action space must be properly initialized with a valid shape."
                )

    def get_observation_space(self) -> gymnasium.spaces.Space:
        return self.observation_space

    def get_action_space(self) -> gymnasium.spaces.Space:
        return self.action_space

    def get_observation(self):
        """
        Get the current observation from the robot's sensors.
        Handles potential errors during sensor reading.
        """
        try:
            sensor_values = self.get_sensor_readings()
            if sensor_values is None:
                self.logger.warning(
                    "Received None from get_sensor_readings(). Defaulting observation."
                )
                yaw_deg, pitch_deg, roll_deg = 0.0, 0.0, 0.0
            else:
                # Assuming get_sensor_readings() returns a tuple/list of 3 numbers
                if len(sensor_values) == 3:
                    yaw_deg, pitch_deg, roll_deg = (
                        float(sensor_values[0]),
                        float(sensor_values[1]),
                        float(sensor_values[2]),
                    )
                else:
                    self.logger.warning(
                        f"Received malformed sensor_readings (length {len(sensor_values)}): {sensor_values}. Defaulting observation."
                    )
                    yaw_deg, pitch_deg, roll_deg = 0.0, 0.0, 0.0
        except Exception as e:
            self.logger.error(
                f"Error getting or parsing sensor readings: {e}. Defaulting observation."
            )
            yaw_deg, pitch_deg, roll_deg = 0.0, 0.0, 0.0

        obs = np.array([yaw_deg, pitch_deg, roll_deg], dtype=np.float32)

        # Store the last observation
        self._last_obs = obs

        return obs

    def apply_action(self, action: Any) -> None:
        actuator_values: List = self.set_action_values(action)  # type: ignore
        actuator_cmd = " ".join(str(v) for v in actuator_values)

        if self.comm.write_line(f"W {actuator_cmd}\n"):
            attempts = 0
            max_attempts = 10
            while self.comm._read_raw_line() == "OK" and attempts < max_attempts:
                sleep(0.1)
                attempts += 1
            if attempts >= max_attempts:
                self.logger.warning(
                    "Exceeded maximum attempts while waiting for response to W %s",
                    actuator_cmd,
                )
        else:
            self.logger.error("Failed to write action command: W %s", actuator_cmd)

        self.render()

    def render(self) -> None:
        """
        Render the robot's current state by printing its name and actuator values.
        """
        try:
            actuator_values = self.get_actuator_values()
            print(f"[{self.robot_name}] Actuator Values: {actuator_values}")
        except Exception as e:
            self.logger.error(f"Error getting actuator values for rendering: {e}")
            print(f"[{self.robot_name}] Actuator Values: Error retrieving values")

    def close(self) -> None:
        self.comm.close_connection()

    def reset(self, *, seed=None, options=None):
        actuator_values: List = self.reset_action_values()  # type: ignore
        actuator_cmd = " ".join(str(v) for v in actuator_values)
        self.comm.write_line(f"W {actuator_cmd}\n")
        return self.get_observation(), {}

    @abstractmethod
    def get_actuator_values(self):
        pass

    @abstractmethod
    def set_action_values(self, servo_angles):
        pass

    def reset_action_values(self):
        return self.action_space.sample()

    @abstractmethod
    def get_sensor_readings(self):
        """
        Get the raw sensor readings from the robot.
        """
        pass

    def __enter__(self):
        self.comm.connect()
        if not self.comm.wait_for_ready("RREADY"):
            self.logger.warning(
                "Robot did not signal ready after connect in __enter__."
            )
        # Call reset after connection and ready.
        self.reset()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        # Use SerialCommunicator
        self.comm.close_connection()

    def __del__(self) -> None:
        if hasattr(self, "comm"):
            self.comm.close_connection()
