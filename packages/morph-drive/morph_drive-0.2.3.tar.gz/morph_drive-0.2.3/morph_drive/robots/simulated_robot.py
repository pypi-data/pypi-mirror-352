import logging
import os
from abc import abstractmethod
from typing import Any

import gymnasium
import numpy as np
from gymnasium import utils
from gymnasium.envs.mujoco import MujocoEnv  # type: ignore

from . import RobotInterface


class SimRobot(RobotInterface, MujocoEnv, utils.EzPickle):
    """
    Implementation of RobotInterface for a MuJoCo-based simulation.
    This wraps a Gymnasium MuJoCo environment (e.g., OrigamiTriangularRobotEnv) to simulate the robot.
    """

    observation_space: gymnasium.spaces.Space
    action_space: gymnasium.spaces.Space

    def __init__(
        self,
        robot_name: str = "SimRobot",
        observation_space: gymnasium.spaces.Space | None = None,
        action_space: gymnasium.spaces.Space | None = None,
        configs: dict[str, Any] | None = None,
    ):
        """
        Initialize the simulated robot environment.
        """

        # Initialize RobotInterface base
        RobotInterface.__init__(self)

        if configs is None:
            configs = {}

        xml_file_config = configs.get("xml_file")
        if xml_file_config is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            xml_file = os.path.join(base_dir, "env.xml")
        else:
            xml_file = str(xml_file_config)

        if not os.path.isfile(xml_file):
            raise FileNotFoundError(
                f"MuJoCo model XML file not found at: {xml_file}",
            )

        self.robot_name = robot_name
        self.logger = logging.getLogger(__name__)

        if observation_space is None:
            raise ValueError("Observation space must be provided for SimRobot.")
        if action_space is None:
            raise ValueError("Action space must be provided for SimRobot.")

        self.observation_space = observation_space
        self.action_space = action_space

        self.render_width = int(configs.get("width", 1280))
        self.render_height = int(configs.get("height", 720))
        current_frame_skip = int(
            configs.get("frame_skip", 15)
        )  # Renamed to avoid clash with self.frame_skip from MujocoEnv
        self.render_mode = str(configs.get("render_mode", "human"))

        self.joint_qpos_indices = [7, 8, 9]

        utils.EzPickle.__init__(
            self,
            robot_name=robot_name,
            observation_space=observation_space,
            action_space=action_space,
            configs=configs,
            model_path=xml_file,
            frame_skip=current_frame_skip,
            width=self.render_width,
            height=self.render_height,
            render_mode=self.render_mode,
        )

        MujocoEnv.__init__(
            self,
            model_path=xml_file,
            frame_skip=current_frame_skip,
            observation_space=observation_space,
            render_mode=self.render_mode,
            width=self.render_width,
            height=self.render_height,
        )

        self.metadata = {
            "render_modes": [self.render_mode, "rgb_array"],
            "render_fps": int(np.round(1.0 / self.dt)),
        }

        self.position: list[int] = []
        init_pos_config = configs.get("init_position")
        if init_pos_config:
            if isinstance(init_pos_config, (list, tuple)):
                self.position = [int(v) for v in init_pos_config]
            else:
                raise ValueError(
                    "Invalid type for 'init_position'. Expected list or tuple."
                )
        else:
            if self.action_space:
                if isinstance(self.action_space, gymnasium.spaces.MultiDiscrete):
                    self.position = [0] * len(self.action_space.nvec)
                elif isinstance(self.action_space, gymnasium.spaces.Box) or isinstance(
                    self.action_space, gymnasium.spaces.Discrete
                ):
                    if (
                        self.action_space.shape is not None
                        and len(self.action_space.shape) > 0
                    ):
                        self.position = [0] * self.action_space.shape[0]
                    elif not self.action_space.shape:
                        self.position = [0]
                    else:
                        self.logger.warning(
                            "Could not determine action space shape for default init_position."
                        )
                else:
                    self.logger.warning(
                        "Unsupported action space type for default init_position."
                    )
            else:
                self.logger.warning(
                    "Action space not available for default init_position."
                )

    def get_observation_space(self) -> gymnasium.spaces.Space:
        """
        Return the observation space defined by the simulation
        """
        return self.observation_space

    def get_action_space(self) -> gymnasium.spaces.Space:
        """
        Return the action space defined by the simulation
        """
        return self.action_space

    def get_observation(self):
        """
        Use the observation space defined by the simulation (e.g., continuous Box for [yaw, pitch, roll])
        """
        accel, gyro, mag = self.get_sensor_readings()  # type: ignore
        a_x, a_y, a_z = accel
        g_x, g_y, g_z = gyro
        m_x, m_y, m_z = mag

        # Calculate pitch, roll, and yaw
        pitch = np.arctan2(-a_x, np.sqrt(a_y**2 + a_z**2))
        roll = np.arctan2(a_y, a_z)

        m_x_comp = m_x * np.cos(pitch) + m_z * np.sin(pitch)
        m_y_comp = (
            m_x * np.sin(roll) * np.sin(pitch)
            + m_y * np.cos(roll)
            - m_z * np.sin(roll) * np.cos(pitch)
        )
        yaw = np.arctan2(m_y_comp, m_x_comp)

        yaw_deg = np.degrees(yaw)
        pitch_deg = np.degrees(pitch)
        roll_deg = np.degrees(roll)

        obs = np.array([yaw_deg, pitch_deg, roll_deg], dtype=np.float32)

        # Store the last observation
        self._last_obs = obs

        return obs

    def apply_action(self, action: Any) -> None:
        """
        Apply an action in the simulation by advancing the simulation with the given control input.
        """

        actuator_values = self.set_action_values(action)

        if hasattr(self, "model") and self.model:
            try:
                # Ensure joint names match your XML. These are examples.
                joint1_qposadr = self.model.joint("joint1").qposadr[0]
                joint2_qposadr = self.model.joint("joint2").qposadr[0]
                joint3_qposadr = self.model.joint("joint3").qposadr[0]
                self.joint_qpos_indices = [
                    joint1_qposadr,
                    joint2_qposadr,
                    joint3_qposadr,
                ]
            except Exception as e:
                self.logger.error(
                    f"Could not get joint qpos addresses dynamically in apply_action: {e}. Using fallback {self.joint_qpos_indices}."
                )

        target_positions = np.array(actuator_values, dtype=np.float64)

        max_iterations = 300
        tolerance = 1.5  # Degrees

        for _i in range(max_iterations):
            self.do_simulation(ctrl=target_positions, n_frames=1)
            current_positions = self.data.qpos[self.joint_qpos_indices]

            if np.allclose(current_positions, target_positions, atol=tolerance):
                break

        self.render()

    def render(self) -> None:
        """
        Render the simulation using MuJoCo's render method.
        """
        self.mujoco_renderer.render(self.render_mode)

    def close(self) -> None:
        """
        Close the MuJoCo simulation environment.
        """
        MujocoEnv.close(self)

    def reset(self, *, seed=None, options=None):
        """
        Reset the simulation to its desired initial state.
        """
        actuator_values = self.reset_action_values()

        if hasattr(self, "model") and self.model:
            try:
                joint1_qposadr = self.model.joint("joint1").qposadr[0]
                joint2_qposadr = self.model.joint("joint2").qposadr[0]
                joint3_qposadr = self.model.joint("joint3").qposadr[0]
                self.joint_qpos_indices = [
                    joint1_qposadr,
                    joint2_qposadr,
                    joint3_qposadr,
                ]
            except Exception as e:
                self.logger.error(
                    f"Could not get joint qpos addresses dynamically in reset: {e}. Using fallback {self.joint_qpos_indices}."
                )

        target_positions = np.array(actuator_values, dtype=np.float64)

        max_iterations = 300
        tolerance = 1.5  # Degrees

        MujocoEnv.reset(self, seed=seed, options=options)  # Standard reset

        for _i in range(max_iterations):  # Use _i if i is not used
            self.do_simulation(ctrl=target_positions, n_frames=1)
            current_positions = self.data.qpos[self.joint_qpos_indices]

            if np.allclose(current_positions, target_positions, atol=tolerance):
                break

        self.render()
        return self.get_observation(), {}

    # ------------------------------------

    @abstractmethod
    def get_actuator_values(self):
        """
        Helper function to read the current actuator values in servo angles
        """

    @abstractmethod
    def set_action_values(self, servo_angles):
        """
        Helper function to set the action values based on servo angles.
        """

    def reset_action_values(self):
        """
        Helper function to define the action values into expected position.
        Generates random values within the action space by default
        """
        return self.action_space.sample()

    @abstractmethod
    def get_sensor_readings(self):
        """
        Helper function to read the sensor values
        """
