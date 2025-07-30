import os
from abc import abstractmethod
from time import sleep
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

    metadata = {"render_modes": ["human"]}

    observation_space: gymnasium.spaces.Space
    action_space: gymnasium.spaces.Space

    def __init__(
        self,
        robot_name: str = "SimRobot",
        observation_space: gymnasium.spaces.Space | None = None,
        action_space: gymnasium.spaces.Space | None = None,
        configs: dict[str, str | int] | None = None,
        **kwargs,
    ):
        """
        Initialize the simulated robot environment.
        """
        super().__init__()

        if configs is None:
            configs = {}

        # debug = configs.get("debug", False)

        xml_file = str(configs.get("xml_file", None))
        if xml_file is None:
            xml_file = os.path.join(os.path.dirname(__file__), "env.xml")

        if not os.path.isfile(xml_file):
            raise FileNotFoundError(
                f"MuJoCo model XML file not found at: {xml_file}",
            )

        self.robot_name = robot_name

        if observation_space is None:
            raise ValueError("Observation space must be provided.")

        if action_space is None:
            raise ValueError("Action space must be provided.")

        # Rendering configs
        self.render_width = int(configs.get("width", 1280))
        self.render_height = int(configs.get("height", 720))
        self.render_frame_skip = int(configs.get("frame_skip", 15))
        self.render_mode = str(configs.get("render_mode", "human"))

        # Initialize the MujocoEnv with the model.
        utils.EzPickle.__init__(self, xml_file, **kwargs)

        # https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjvoption
        visual_options: dict[int, bool] = {}

        MujocoEnv.__init__(
            self,
            model_path=xml_file,
            frame_skip=self.render_frame_skip,
            width=self.render_width,
            height=self.render_height,
            observation_space=observation_space,
            render_mode=self.render_mode,
            visual_options=visual_options,
            **kwargs,
        )

        self.metadata = {
            "render_modes": [self.render_mode],
            "render_fps": int(np.round(1.0 / self.dt)),
        }

        self.observation_space = observation_space
        self.action_space = action_space

        # (Optionally) one could also configure a reward range or other properties here.
        # self.reward_range = (-float('inf'), float('inf'))

        # # Environment specification, typically set by gymnasium when registered.
        # self.spec = None

        self.position: list[int] = []

        if configs.get("init_position"):
            init_position = configs.get("init_position")
            if isinstance(init_position, (list, tuple)):
                self.position = [int(v) for v in init_position]
            else:
                raise ValueError("Invalid type for 'init_position'. Expected list, or tuple.")
        else:
            if self.action_space and hasattr(self.action_space, 'shape'):
                self.position = [0] * self.action_space.shape[0] # type: ignore
            else:
                raise ValueError("Action space must be properly initialized with a valid shape.")


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

        # Execute the action in the simulation.
        for i in range(10):
            # TODO implement a while loop to reach the desired position rather than using 10 steps
            self.render()
            self.do_simulation(ctrl=actuator_values, n_frames=self.frame_skip)
            self.render()
            sleep(self.dt)

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
        # Gymnasium's base method to handle seeding
        super().reset(seed=None, options=None)

        # Reset robot with its initiate / reset position
        actuator_values = self.reset_action_values()

        # Reach the destination in several steps
        for _ in range(10):
            self.do_simulation(ctrl=actuator_values, n_frames=self.frame_skip)
            self.render()
            sleep(self.dt)

        # Gymnasium reset should return (obs, info)
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
