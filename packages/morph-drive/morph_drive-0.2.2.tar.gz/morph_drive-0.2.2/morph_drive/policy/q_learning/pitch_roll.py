import random
from typing import Any, Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np

from ..policy_base import PolicyBase


class QLearningPolicyPitchRoll(PolicyBase):
    """
    Q-learning policy for a discrete 3D state space and 3D action space.
    - State space: each state is a tuple (x, y, z) with x, y, z in [-18, 18].
    - Action space: each action is a tuple (dx, dy, dz) with dx, dy, dz in [-1, 0, 1].
    """

    # Define all possible actions in the 3D action space (27 possible actions)
    ACTIONS: Tuple[Tuple[int, int, int], ...] = tuple(
        (dx, dy, dz) for dx in [-1, 0, 1] for dy in [-1, 0, 1] for dz in [-1, 0, 1]
    )

    def __init__(self, alpha: float = 0.1, gamma: float = 0.99, epsilon: float = 0.1):
        """
        Initialize the Q-learning policy.
        :param alpha: Learning rate (how much to update Q-values on new information).
        :param gamma: Discount factor (how much future rewards are valued).
        :param epsilon: Exploration rate for epsilon-greedy action selection.
        """
        super().__init__()  # Initialize base class (if PolicyBase has its own init)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

        # Q-table: maps state -> dict of action values.
        # Each state is a tuple (pitch, roll), each action is a tuple (dx,dy,dz).
        self.q_table: Dict[Tuple[int, int], Dict[Tuple[int, int, int], float]] = {}

    def select_action(self, state: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        Select an action for the given state using an epsilon-greedy strategy.
        With probability epsilon, choose a random action; otherwise choose the best action (highest Q-value).
        """
        # Ensure state is a tuple (in case state is given as list or array)
        if (
            not isinstance(state, tuple)
            or len(state) != 3
            or not all(isinstance(x, int) for x in state)
        ):
            raise ValueError("State must be a tuple of three integers (x, y, z).")

        policy_state: Tuple[int, int] = tuple(state[1:3])  # (pitch,roll) # type: ignore

        # If state not seen before, initialize its Q-values to 0 for all actions
        if policy_state not in self.q_table:
            self.q_table[policy_state] = {action: 0.0 for action in self.ACTIONS}

        # Exploration: choose a random action with probability epsilon
        if random.random() < self.epsilon:
            action = random.choice(self.ACTIONS)
            return action

        # Exploitation: choose the action with the highest Q-value for this policy_state
        state_actions = self.q_table[policy_state]

        # Find the maximum Q-value among all actions for this state
        max_q = max(state_actions.values())

        # Collect all actions that have this Q-value (to break ties randomly if needed)
        best_actions = [act for act, q_val in state_actions.items() if q_val == max_q]

        # Choose one of the best actions at random (this handles tie-breaking)
        best_action = random.choice(best_actions)
        return best_action

    def train(
        self,
        state: Tuple[int, int, int],
        action: Tuple[int, int, int],
        reward: float,
        next_state: Tuple[int, int, int],
        done: bool,
    ) -> None:
        """
        Update the Q-table based on a transition: (state, action, reward, next_state, done).
        Applies the Q-learning update rule to adjust Q(state, action).
        """
        # Convert state and action to tuples to ensure they are hashable keys
        action = tuple(action)  # type: ignore
        policy_state: Tuple[int, int] = tuple(state[1:3])  # type: ignore # (pitch,roll)
        policy_next_state: Tuple[int, int] = tuple(next_state[1:3])  # type: ignore # (pitch,roll)

        # Initialize Q-values for policy_state and policy_next_state if not already present
        if policy_state not in self.q_table:
            self.q_table[policy_state] = {act: 0.0 for act in self.ACTIONS}
        if policy_next_state not in self.q_table:
            self.q_table[policy_next_state] = {act: 0.0 for act in self.ACTIONS}

        # Current Q-value for the state-action pair
        current_q = self.q_table[policy_state][action]

        # Compute the target Q-value using the reward and the estimate of optimal future value
        if done:
            # If this transition leads to a terminal state, there is no future reward
            target_q = reward
        else:
            # Estimate of optimal future value: max Q-value for policy_next_state
            next_max = max(self.q_table[policy_next_state].values())
            target_q = reward + self.gamma * next_max

        # Q-learning update: incremental update towards target
        new_q = current_q + self.alpha * (target_q - current_q)
        self.q_table[policy_state][action] = new_q

    def save(
        self,
        filepath: str,
        data: Any = None,
    ) -> None:
        super().save(filepath, (data or self.q_table, self.epsilon))

    def load(self, filepath: str) -> None:
        self.q_table, self.epsilon = super().load(filepath)

    def plot(self, *args, **kwargs):
        """
        Visualize the Q-table slice for states (pitch, roll) in the range [-18, 18].
        - mode='max_q': show max Q-value at each (x, y)
        - mode='best_action': show best action (argmax) at each (x, y) for action_index (0=x, 1=y, 2=z)
        """
        mode = kwargs.get("mode", "max_q")

        if mode == "max_q":
            fig, ax = plt.subplots(figsize=(8, 6))
            axes = [ax]  # Wrap single axis in a list for consistency in the loop
        else:
            fig, axes = plt.subplots(1, 3, figsize=(24, 6))
        x_vals = range(-18, 19)
        y_vals = range(-18, 19)
        data = np.zeros((len(x_vals), len(y_vals)))

        for idx, ax in enumerate(axes):
            data = np.zeros((len(x_vals), len(y_vals)))

            for i, x in enumerate(x_vals):
                for j, y in enumerate(y_vals):
                    state = (x, y)
                    if state in self.q_table:
                        q_dict = self.q_table[state]
                        if mode == "max_q":
                            data[i, j] = max(q_dict.values())
                        elif mode == "best_action":
                            # Get best action tuple, then plot the action component (x, y, or z)
                            best_action = max(q_dict, key=q_dict.get)  # type: ignore
                            data[i, j] = best_action[idx]
                        else:
                            data[i, j] = 0
                    else:
                        data[i, j] = np.nan  # Or np.nan if you prefer blank spots

            if mode == "max_q":
                ax.set_title("Max Q-value Heatmap")
            elif mode == "best_action":
                ax.set_title(f"Best Action[{idx}] Heatmap")

            ax.set_xlabel("Roll")
            ax.set_ylabel("Pitch")
            ax.set_aspect("equal")  # Make the figure square

            im = ax.imshow(
                data,
                origin="lower",
                extent=(-18.0, 18.0, -18.0, 18.0),
                aspect="auto",
                cmap="coolwarm" if mode == "best_action" else None,
            )

            # if mode == "max_q":
            fig.colorbar(im, ax=ax, label="Value")

        plt.tight_layout()
        plt.show()
