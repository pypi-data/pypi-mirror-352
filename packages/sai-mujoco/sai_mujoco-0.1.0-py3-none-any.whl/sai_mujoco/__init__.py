from os import path
from gymnasium import register
from sai_mujoco.utils.extra_utils import load_yaml
from sai_mujoco.robots import get_robot_class_registory

__version__ = "0.1.0"

dir_path = path.dirname(path.realpath(__file__))
env_config = load_yaml(f"{dir_path}/config/registry.yaml")

## Basic Environments
register(
    id="HumanoidObstacle-v0",
    entry_point="sai_mujoco.basic_envs.humanoid_obstacle:HumanoidObstacleEnv",
)

register(
    id="InvertedPendulumWheel-v0",
    entry_point="sai_mujoco.basic_envs.inverted_pendulum_wheel:InvertedPendulumWheelEnv",
)


## Import Future Environments if Available
try:
    import sai_mujoco._future
except:
    pass

for env in env_config['environments']:
    env_name = env['name']
    entry_point = env['entry_point']
    robots = env['robots']

    # Normalize to list of dicts
    if isinstance(robots, dict):  # single robot dict
        robots = [robots]

    for robot_entry in robots:
        for robot_name, robot_config in robot_entry.items():
            robot_model = get_robot_class_registory(robot_name)

            robot_env = "".join(robot_name.title().split("_"))
            env_id = f"{robot_env}{env_name}-v0"
            kwargs = {
                "env_config": robot_config,
                "robot_class": robot_model,
            }

            register(
                id = env_id,
                entry_point=entry_point,
                kwargs=kwargs
            )
