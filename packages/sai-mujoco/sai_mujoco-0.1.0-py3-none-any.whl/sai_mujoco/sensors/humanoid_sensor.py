from sai_mujoco.base.sensor import BaseSensor

class HumanoidBodySensor(BaseSensor):
    name = "humanoid_body_sensor"
    xml_file_name = "humanoid_full"

    accelerometer = ["accelerometer"]
    velocimeter = ["local_linvel"]
    gyro = ["gyro"]
    framezaxis = ["upvector"]
    framexaxis = ["forwardvector"]
    framelinvel = ["global_linvel","left_foot_global_linvel","right_foot_global_linvel"]
    frameangvel = ["global_angvel"]
    framepos = ["position", "left_foot_pos", "right_foot_pos"]
    framequat = ["orientation"]

    state_sensor_space = ["gyro", "local_linvel"]
    privileged_sensors = ["accelerometer", "upvector", "forwardvector"] # -1 for all sensors except state_sensor_space


class HumanoidUpperBodySensor(BaseSensor):
    name = "humanoid_upper_body_sensor"
    xml_file_name = "humanoid_upper"

    accelerometer = ["accelerometer"]
    velocimeter = ["local_linvel"]
    gyro = ["gyro"]
    framezaxis = ["upvector"]
    framexaxis = ["forwardvector"]
    framelinvel = ["global_linvel"]
    frameangvel = ["global_angvel"]
    framepos = ["position"]
    framequat = ["orientation"]

    state_sensor_space = ["gyro", "local_linvel"]
    privileged_sensors = ["accelerometer", "upvector", "forwardvector"] # -1 for all sensors except state_sensor_space
