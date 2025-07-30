class BaseSensor:
    name: str = ""

    accelerometer : list = []
    velocimeter: list = []
    gyro : list = []
    force: list = []
    torque: list = []
    magnetometer: list = []
    framezaxis: list = []
    framexaxis: list = []
    framelinvel: list = []
    frameangvel: list = []
    framepos: list = []
    framequat: list = []
    camera: dict[str, str] = {}

    state_sensor_space: list = []
    privileged_sensors: list = []

