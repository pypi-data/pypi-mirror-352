import importlib
import yaml
from typing import Any, Tuple, Union
import numpy as np

def load_yaml(yaml_file_path: str) -> dict:
    try:
        with open(yaml_file_path) as stream:
            return yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        raise ValueError(f"Error parsing YAML file: {exc}")
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Environment configuration file not found at {yaml_file_path}"
        )
    except Exception as e:
        raise e
    
def import_class_from_string(class_path: str):
    module_path, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)

def get_collision_info(contact: Any, geom1: int, geom2: int) -> Tuple[np.ndarray, np.ndarray]:
  """Get the distance and normal of the collision between two geoms."""
  mask = (np.array([geom1, geom2]) == contact.geom).all(axis=1)
  mask |= (np.array([geom2, geom1]) == contact.geom).all(axis=1)
  idx = np.where(mask, contact.dist, 1e4).argmin()
  dist = contact.dist[idx] * mask[idx]
  # normal = (dist < 0) * contact.frame[idx, 0, :3]
  return dist

def geoms_colliding(state, geom1: int, geom2: int) -> np.ndarray:
  """Return True if the two geoms are colliding."""

  try:
    val = get_collision_info(state.contact, geom1, geom2)
    return val < 0
  except:
    #  print(state.contact)
     return 0

def get_rz(
    phi: Union[np.ndarray, float], swing_height: Union[np.ndarray, float] = 0.08
) -> np.ndarray:
  def cubic_bezier_interpolation(y_start, y_end, x):
    y_diff = y_end - y_start
    bezier = x**3 + 3 * (x**2 * (1 - x))
    return y_start + y_diff * bezier

  x = (phi + np.pi) / (2 * np.pi)
  stance = cubic_bezier_interpolation(0, swing_height, 2 * x)
  swing = cubic_bezier_interpolation(swing_height, 0, 2 * x - 1)
  return np.where(x <= 0.5, stance, swing)
