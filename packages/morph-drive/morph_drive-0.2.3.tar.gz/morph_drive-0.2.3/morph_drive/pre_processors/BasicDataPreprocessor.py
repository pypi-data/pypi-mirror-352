from typing import Any

import numpy as np

from . import DataPreprocessorBase


class BasicDataPreprocessor(DataPreprocessorBase):
    """
    A basic data preprocessor that parses and quantizes raw sensor inputs (e.g., yaw, pitch, roll).
    """

    def __init__(self, quantum: float = 1.0, min_threshold: float = 2.5):
        """
        Initialize the preprocessor.
        """
        self.quantum = quantum
        self.min_threshold = min_threshold

    def process(self, sensor_data: Any, **kwargs) -> np.ndarray:
        """
        Process the raw sensor data by parsing and quantizing.
        """
        n = kwargs.get("n", 3)  # Default to 3 if 'n' is not provided

        # Parse string input (e.g., "yaw,pitch,roll")
        if isinstance(sensor_data, str):
            try:
                parts = sensor_data.split(",")
                selected_parts = parts[:n]
                values = [float(p) for p in selected_parts]
                while len(values) < n:
                    values.append(0.0)
            except ValueError:
                # Default to zero values
                values = [0.0] * n
            except Exception:
                # Default to zero values
                values = [0.0] * n

        elif isinstance(sensor_data, (list, tuple, np.ndarray)):
            values = [float(x) for x in sensor_data]

        else:
            # Unsupported type, return zeros
            values = [0.0] * n

        # Quantize values and apply threshold filtering
        quantized = []
        for v in values:
            qv = round(v / self.quantum) * self.quantum
            if abs(qv) <= self.min_threshold:
                qv = 0.0  # zero-out small values
            quantized.append(qv)

        obs = np.array(quantized, dtype=np.float32)
        return obs
