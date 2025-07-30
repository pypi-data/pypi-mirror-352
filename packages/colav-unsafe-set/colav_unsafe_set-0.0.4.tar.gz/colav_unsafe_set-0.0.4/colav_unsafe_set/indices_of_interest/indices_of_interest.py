from colav_unsafe_set.objects import (
    Agent,
    DynamicObstacle,
    DynamicObstacleWithMetrics
)
from scipy.spatial.distance import euclidean
from typing import List

def compute_agent_obstacle_distance(agent: Agent, obstacle: DynamicObstacleWithMetrics) -> float:
    """
    Compute the adjusted Euclidean distance between an agent and a dynamic obstacle,
    subtracting both their safety radii.
    """
    return euclidean(agent.position, obstacle.dynamic_obstacle.position) - (
        agent.safety_radius + obstacle.dynamic_obstacle.safety_radius
    )

def compute_obstacle_distance(
    obstacle1: DynamicObstacleWithMetrics, obstacle2: DynamicObstacleWithMetrics
) -> float:
    """
    Compute the adjusted Euclidean distance between two dynamic obstacles,
    subtracting their safety radii.
    """
    return euclidean(obstacle1.dynamic_obstacle.position, obstacle2.dynamic_obstacle.position) - (
        obstacle1.dynamic_obstacle.safety_radius + obstacle2.dynamic_obstacle.safety_radius
    )

def calc_I1(
    agent: Agent,
    dynamic_obstacles_with_metrics: List[DynamicObstacleWithMetrics],
    dsf: float,
) -> List[DynamicObstacleWithMetrics]:
    """Calculate the set of obstacles that are within the distance safety threshold (dsf) from the agent."""
    return [
        obstacle
        for obstacle in dynamic_obstacles_with_metrics
        if compute_agent_obstacle_distance(agent, obstacle) <= dsf
    ]

def calc_I2(
    I1: List[DynamicObstacleWithMetrics],
    dynamic_obstacles_with_metrics: List[DynamicObstacleWithMetrics],
    dsf: float,
) -> List[DynamicObstacleWithMetrics]:
    """
    Calculate the set of obstacles from I1 that have at least one other dynamic obstacle
    (from dynamic_obstacles_with_metrics) within the distance safety threshold.
    """
    I2 = []
    for operand in I1:
        for arg in dynamic_obstacles_with_metrics:
            if operand == arg:
                continue
            if compute_obstacle_distance(operand, arg) <= dsf:
                I2.append(operand)
                break  # add each operand only once and move to the next
    return I2

def calc_I3(
    dynamic_obstacles_with_metrics: List[DynamicObstacleWithMetrics],
    dsf: float,
    time_of_interest: float
) -> List[DynamicObstacleWithMetrics]:
    """Calculate the set of obstacles whose DCPA at the time of TCPA is within the distance safety threshold."""
    return [
        dob for dob in dynamic_obstacles_with_metrics 
        if dob.dcpa <= dsf and dob.tcpa <= time_of_interest
    ]