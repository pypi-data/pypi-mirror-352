import numpy as np
from scipy.spatial.transform import Rotation as R
from typing import Tuple

def predict_position(
    position: Tuple[float, ...], 
    quaternion_orientation: Tuple[float, float, float, float], 
    velocity: float, 
    yaw_rate: float,
    dt: float
) -> np.ndarray:
    """
    Predicts the future position of an object given its current state.

    Args:
        position: Tuple[float, ...] - Current position as (x, y) or (x, y, z)
        quaternion_orientation: Tuple[float, float, float, float] - Orientation as a quaternion
        velocity: float - Speed in the current direction
        yaw_rate: float - Change in yaw per second (rad/s)
        dt: float - Time step for prediction

    Returns:
        np.ndarray: Predicted position as [x_new, y_new, z_new] (3D if needed)
    """
    # Convert position to an array and pad with 0 if needed.
    pos_array = np.array(position, dtype=np.float64)
    if pos_array.size == 2:
        pos_array = np.concatenate([pos_array, np.array([0.0])])  # Add z=0 for 2D position
    
    # Ensure dt is a valid value (not NaN)
    if np.isnan(dt) or dt <= 0:
        raise ValueError("Time step (dt) must be a positive number")
    
    # Normalize the quaternion if it's not normalized
    norm = np.linalg.norm(quaternion_orientation)
    if norm != 1.0:
        quaternion_orientation = tuple(np.array(quaternion_orientation) / norm)
    
    # Convert quaternion to Euler angles (yaw, pitch, roll)
    r = R.from_quat(quaternion_orientation)
    yaw, _, _ = r.as_euler('zyx', degrees=False)  # yaw is the first Euler angle
    
    # Update yaw based on yaw_rate and dt
    yaw_new = yaw + yaw_rate * dt
    
    # Compute displacement in the XY plane
    dx = velocity * np.cos(yaw_new) * dt
    dy = velocity * np.sin(yaw_new) * dt
    
    # Update position (assuming no change in z for 2D)
    new_position = pos_array + np.array([dx, dy, 0.0])
    
    return new_position
