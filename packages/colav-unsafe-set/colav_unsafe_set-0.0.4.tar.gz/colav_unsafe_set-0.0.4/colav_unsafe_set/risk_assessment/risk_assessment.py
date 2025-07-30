import numpy as np
import math
from typing import Tuple
from colav_unsafe_set.objects import Agent, DynamicObstacle

def quaternion_to_heading(qx, qy, qz, qw) -> float:
    """Convert quaternion to heading angle in radians."""
    norm = math.sqrt(qx**2 + qy**2 + qz**2 + qw**2)
    qx, qy, qz, qw = qx / norm, qy / norm, qz / norm, qw / norm
    siny_cosp = 2.0 * (qw * qz + qx * qy)
    cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
    return math.atan2(siny_cosp, cosy_cosp)

def normalize_angle(angle: float) -> float:
    """Normalize angle to the range [-π, π]."""
    return (angle + np.pi) % (2 * np.pi) - np.pi

def calc_cpa(agent_object: Agent, target_object: DynamicObstacle) -> Tuple[float, float]:
    """Calculate DCPA and TCPA between agent and target."""

    # Positions
    p1 = np.array(agent_object.position[:2])
    p2 = np.array(target_object.position[:2])

    # Headings
    theta1 = normalize_angle(quaternion_to_heading(*agent_object.orientation))
    theta2 = normalize_angle(quaternion_to_heading(*target_object.orientation))

    # Velocity vectors
    v1 = agent_object.velocity * np.array([np.cos(theta1), np.sin(theta1)])
    v2 = target_object.velocity * np.array([np.cos(theta2), np.sin(theta2)])

    # Relative vectors
    p_rel = p1 - p2
    v_rel = v1 - v2
    v_rel_norm_sq = np.dot(v_rel, v_rel)

    if v_rel_norm_sq < 1e-6:
        if np.allclose(p_rel, [0, 0]):
            dcpa = float('nan')
            tcpa = float('inf')
        else:
            distance = np.linalg.norm(p_rel)
            speed = np.linalg.norm(v1)
            dcpa = distance
            tcpa = distance / speed if speed > 0 else float('inf')
    else:
        tcpa = -np.dot(p_rel, v_rel) / v_rel_norm_sq
        if tcpa > 0:
            cpa_vector = p_rel + tcpa * (-v_rel)
            dcpa = np.linalg.norm(cpa_vector)
        else:
            dcpa = float('nan')
            tcpa = float('nan')

    return dcpa, tcpa
