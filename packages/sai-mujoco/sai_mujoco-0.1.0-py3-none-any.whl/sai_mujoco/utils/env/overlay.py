def toggle_overlay(mujoco_renderer, show_overlay, render_mode):
    if render_mode == "human":
        if mujoco_renderer.viewer is None:
            mujoco_renderer._get_viewer(render_mode=render_mode)
        mujoco_renderer.viewer._hide_menu = not show_overlay
