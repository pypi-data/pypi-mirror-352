from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class DataPreprocessorBase(ABC):
    """
    Interface for data preprocessing modules that convert raw sensor inputs into observations.
    """

    @abstractmethod
    def process(self, sensor_data: Any, **kwargs) -> np.ndarray:
        pass
