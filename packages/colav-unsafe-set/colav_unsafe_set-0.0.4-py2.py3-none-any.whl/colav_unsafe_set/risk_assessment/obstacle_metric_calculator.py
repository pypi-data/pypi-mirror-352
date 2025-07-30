from colav_unsafe_set.objects import (
    Agent, 
    DynamicObstacle,
    DynamicObstacleWithMetrics
)
from .risk_assessment import calc_cpa
from typing import List


def calculate_obstacle_metrics_for_agent(agent_vessel: Agent, dynamic_obstacles: List[DynamicObstacle]) -> List[DynamicObstacleWithMetrics]:
    """Iterates through DynamicObstacles calculating DCPA and TCPA relative to agent configuration"""
    dynamic_obstacles_with_metrics = []
    for dynamic_obstacle in dynamic_obstacles:
        [dcpa, tcpa] = calc_cpa(agent_vessel, dynamic_obstacle)
        dynamic_obstacles_with_metrics.append(
            DynamicObstacleWithMetrics(
                dynamic_obstacle=dynamic_obstacle, dcpa=dcpa, tcpa=tcpa
            )
        )
    return dynamic_obstacles_with_metrics
