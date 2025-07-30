from dataclasses import dataclass
from typing import Tuple

@dataclass
class Agent:
    """Represents an agent with position, orientation, velocity, yaw rate, and safety radius."""
    position: Tuple[float, float, float]         # Cartesian position (x, y, z)
    orientation: Tuple[float, float, float, float]  # Quaternion orientation (x, y, z, w)
    velocity: float                                # Velocity in m/s
    yaw_rate: float                                # Yaw rate in rad/s
    safety_radius: float                           # Safety radius in meters

@dataclass
class DynamicObstacle:
    """Represents a dynamic obstacle with its kinematic properties and safety radius."""
    tag: str
    position: Tuple[float, float, float]          # Cartesian position (x, y, z)
    orientation: Tuple[float, float, float, float]  # Quaternion orientation (x, y, z, w)
    velocity: float                               # Velocity in m/s
    yaw_rate: float                               # Yaw rate in rad/s
    safety_radius: float                          # Safety radius in meters

@dataclass
class DynamicObstacleWithMetrics:
    """Associates a dynamic obstacle with additional metrics like TCPA and DCPA."""
    dynamic_obstacle: DynamicObstacle
    tcpa: float                                   # Time to Closest Point of Approach
    dcpa: float                                   # Distance at Closest Point of Approach
