import numpy as np


def termination_condition(data):
    """
    Termination condition for the environment.
    """
    observation = data.get("observation", np.array([-90, 0.0, 0.0], dtype=np.float32))
    target_observation = np.array([-90, 0.0, 0.0], dtype=np.float32)
    status = np.all(np.abs(observation - target_observation) <= 5)
    return status


def truncate_condition(data):
    """
    Truncation condition for the environment.
    """
    step_count = data.get("step_count")
    max_steps = data.get("max_steps", 200)
    return step_count is None or step_count >= max_steps
