import mujoco
import numpy as np
from typing import List, Union
from sai_mujoco.utils import mujoco_utils, rotations


def get_robot_obs(env) -> np.ndarray:
    """
    Extracts the robot's joint positions and velocities as an observation.

    This function retrieves the robot's joint positions and velocities from the environment's
    robot model and returns them as a concatenated numpy array.

    Args:
        env: The environment object that holds the current robot state.

    Returns:
        np.ndarray: A concatenated array of robot joint positions and velocities.
    """

    # Retrieve the robot's joint positions and velocities
    robot_qpos, robot_qvel = mujoco_utils.robot_get_obs(
        env.robot_model.model,
        env.robot_model.data,
        env.robot_model.model_names.joint_names,
    )

    return np.concatenate((robot_qpos.copy(), robot_qvel.copy()))


def get_position_in_world_frame(env, object_name: Union[str, List[str]]) -> np.ndarray:
    """
    Gets the position of a specified object in the world frame.

    This function retrieves the position of one or more objects from the environment
    in the world coordinate system. It returns the positions concatenated into a single array.

    Args:
        env: The environment object that holds the current simulation state.
        object_name: The name(s) of the object(s) whose position(s) are to be retrieved.

    Returns:
        np.ndarray: The concatenated positions of the specified objects in the world frame.
    """

    # Check if a single object name is provided or a list of object names
    if isinstance(object_name, str):
        return mujoco_utils.get_site_xpos(
            env.robot_model.model, env.robot_model.data, object_name
        )

    # For a list of object names, return positions for each object
    state = []
    for name in object_name:
        val = mujoco_utils.get_site_xpos(
            env.robot_model.model, env.robot_model.data, name
        )
        state.append(val)

    return np.concatenate(state)


def get_rotation_in_world_frame(env, object_name: Union[str, List[str]]) -> np.ndarray:
    """
    Gets the rotation (Euler angles) of a specified object in the world frame.

    This function retrieves the rotation of one or more objects from the environment
    in the world coordinate system and returns their rotations as Euler angles in a concatenated array.

    Args:
        env: The environment object that holds the current simulation state.
        object_name: The name(s) of the object(s) whose rotation(s) are to be retrieved.

    Returns:
        np.ndarray: The concatenated rotations (Euler angles) of the specified objects in the world frame.
    """

    # Check if a single object name is provided or a list of object names
    if isinstance(object_name, str):
        return rotations.mat2euler(
            mujoco_utils.get_site_xmat(
                env.robot_model.model, env.robot_model.data, object_name
            )
        )

    # For a list of object names, return positions for each object
    state = []
    for name in object_name:
        val = rotations.mat2euler(
            mujoco_utils.get_site_xmat(
                env.robot_model.model, env.robot_model.data, name
            )
        )
        state.append(val)

    return np.concatenate(state)


def get_object_quat(env, object_name: str):
    """
    Retrieves the quaternion representing the orientation of a specified object.

    Args:
        env: The environment object that holds the current simulation state.
        object_name: The name of the object whose orientation is to be retrieved.

    Returns:
        np.ndarray: The quaternion representing the object's orientation.
    """

    # Get the object ID and return its orientation as a quaternion
    object_id = env.robot_model.model_names.body_name2id[object_name]
    return env.robot_model.data.xquat[object_id]


def get_object_position(env, object_name: str):
    """
    Retrieves the position of a specified object in the world frame.

    Args:
        env: The environment object that holds the current simulation state.
        object_name: The name of the object whose position is to be retrieved.

    Returns:
        np.ndarray: The position of the object in the world frame.
    """

    # Get the object ID and return its position in the world frame
    object_id = env.robot_model.model_names.body_name2id[object_name]
    return env.robot_model.data.xpos[object_id]


def get_object_velp(env, object_name: Union[str, List[str]]):
    """
    Retrieves the linear velocity (position velocity) of a specified object.

    This function returns the velocity of a single object or a list of objects. The velocity is scaled by
    the environment's timestep (`dt`).

    Args:
        env: The environment object that holds the current simulation state.
        object_name: The name(s) of the object(s) whose linear velocity is to be retrieved.

    Returns:
        np.ndarray: The linear velocities of the specified objects.
    """

    # Check if a single object name is provided or a list of object names
    if isinstance(object_name, str):
        return (
            mujoco_utils.get_site_xvelp(
                env.robot_model.model, env.robot_model.data, object_name
            )
            * env.robot_model.dt
        )

    state = []
    for name in object_name:
        val = (
            mujoco_utils.get_site_xvelp(
                env.robot_model.model, env.robot_model.data, name
            )
            * env.robot_model.dt
        )
        state.append(val)

    return np.concatenate(state)


def get_object_velr(env, object_name: str):
    """
    Retrieves the angular velocity (rotation velocity) of a specified object.

    Args:
        env: The environment object that holds the current simulation state.
        object_name: The name of the object whose angular velocity is to be retrieved.

    Returns:
        np.ndarray: The angular velocity of the object.
    """

    # Get and return the angular velocity of the object
    return (
        mujoco_utils.get_site_xvelr(
            env.robot_model.model, env.robot_model.data, object_name
        )
        * env.robot_model.dt
    )


def get_relative_position(env, object_name: str, target_name: Union[str, List[str]]):
    """
    Computes the relative position between a specified object and multiple target objects.

    This function calculates the relative position of an object with respect to a list of target objects
    and returns the results as a concatenated array.

    Args:
        env: The environment object that holds the current simulation state.
        object_name: The name of the reference object.
        target_name: Target object(s) names to compute relative positions.

    Returns:
        np.ndarray: The relative positions between the reference object and the target objects.
    """

    # Get the position of the reference object in the world frame
    object_location = mujoco_utils.get_site_xpos(
        env.robot_model.model, env.robot_model.data, object_name
    )

    if isinstance(target_name, str):
        pose = mujoco_utils.get_site_xpos(
            env.robot_model.model, env.robot_model.data, target_name
        )
        relative_pose = object_location - pose
        return relative_pose

    relative_state = []
    # Compute the relative position for each target object
    for name in target_name:
        pose = mujoco_utils.get_site_xpos(
            env.robot_model.model, env.robot_model.data, name
        )
        relative_pose = object_location - pose
        relative_state.append(relative_pose)
    return np.concatenate(relative_state)


def get_relative_velocity(env, object_name: str, target_name: Union[str, List[str]]):
    """
    Computes the relative velocity between a specified object and multiple target objects.

    This function calculates the relative linear velocities between the reference object and a list of target
    objects, and returns the velocities as a concatenated array.

    Args:
        env: The environment object that holds the current simulation state.
        object_name: The name of the reference object.
        target_name: Target object(s) names to compute relative velocities.

    Returns:
        np.ndarray: The relative velocities between the reference object and the target objects.
    """

    # Get the velocity of the reference object in the world frame
    object_velocity = mujoco_utils.get_site_xvelp(
        env.robot_model.model, env.robot_model.data, object_name
    )

    if isinstance(target_name, str):
        vel = mujoco_utils.get_site_xvelp(
            env.robot_model.model, env.robot_model.data, target_name
        )
        relative_vel = object_velocity - vel
        return relative_vel

    relative_state = []
    # Compute the relative velocity for each target object
    for name in target_name:
        vel = mujoco_utils.get_site_xvelp(
            env.robot_model.model, env.robot_model.data, name
        )
        relative_vel = (object_velocity - vel) * env.robot_model.dt
        relative_state.append(relative_vel)
    return np.concatenate(relative_state)


def get_camera_data(
    env, camera_name: str, render_mode: str = "rgb_array"
) -> np.ndarray:
    """
    Fetches a rendered camera frame and returns it as a flattened numpy array.

    Args:
        camera_name (str): Name of the camera.
        env: the environment class object.
        render_mode (Optional[str]): Mode to render the image (e.g., "rgb_array", "depth_array", and "rgbd_tuple").

    Returns:
        np.ndarray: Flattened image data as a float32 array.
    """

    cam_id = mujoco.mj_name2id(
        env.robot_model.model, mujoco.mjtObj.mjOBJ_CAMERA, camera_name
    )

    if cam_id == -1:
        raise ValueError(f"Camera '{camera_name}' not found.")

    viewer_func = env.robot_model.viewer(render_mode=render_mode)
    img = viewer_func.render(render_mode=render_mode, camera_id=cam_id)

    # If tuple (e.g., RGB and depth), reshape and concatenate
    if type(img) == tuple:
        img = list(img)
        img[1] = img[1].reshape((img[1].shape[0], -1, 1))
        img = np.concatenate(img, axis=-1)

    return img.flatten().astype(np.float32)


def get_sensor_data(env, sensor_name: str):
    """
    Fetches data from a sensor defined in the MuJoCo model.

    Args:
        sensor_name (str): Name of the sensor.
        model (mujoco.MjModel): The MuJoCo model.
        data (mujoco.MjData): The MuJoCo data.
        viewer (Callable): Not used for sensor, included for interface consistency.

    Returns:
        np.ndarray: Sensor data (assumed to be 3D).
    """

    try:
        sensor_id = mujoco.mj_name2id(
            env.robot_model.model, mujoco.mjtObj.mjOBJ_SENSOR, sensor_name
        )
        sensor_data = env.robot_model.data.sensordata[
            sensor_id : sensor_id + 3
        ]  # 3D vector

        return sensor_data

    except Exception as e:
        ImportError(f"sensor {sensor_name} is not defined in the robot XML")
