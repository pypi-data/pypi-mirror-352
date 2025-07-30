import numpy as np

from .overlay import toggle_overlay


class SAIMujocoBase:
    rescale_bool = False

    def set_rescale_bool(self, rescale_bool):
        self.rescale_bool = rescale_bool

    def _rescale_action(self, action):
        expected_bounds = [-1, 1]
        action_percent = (action - expected_bounds[0]) / (
            expected_bounds[1] - expected_bounds[0]
        )
        bounded_percent = np.minimum(np.maximum(action_percent, 0), 1)
        return (
            self.action_space.low
            + (self.action_space.high - self.action_space.low) * bounded_percent
        )

    def _toggle_overlay(self, show_overlay, render_mode):
        toggle_overlay(
            self.mujoco_renderer, show_overlay, render_mode
        )
