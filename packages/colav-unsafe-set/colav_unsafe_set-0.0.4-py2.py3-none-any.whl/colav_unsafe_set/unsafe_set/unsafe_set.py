from typing import List
from colav_unsafe_set.objects import Agent, DynamicObstacle
from colav_unsafe_set.indices_of_interest import calc_I1, calc_I2, calc_I3, unionise_indices_of_interest
from colav_unsafe_set.risk_assessment import calculate_obstacle_metrics_for_agent
from colav_unsafe_set.collision_geometry import gen_uIoI_convhull

def create_unsafe_set(
    agent: Agent,
    dynamic_obstacles: List[DynamicObstacle],
    dsf: float,
) -> List[int]:
    """
    Create an unsafe set for an agent by computing obstacle metrics, determining indices 
    of interest, unionizing these indices, and generating a convex hull around the unsafe regions.

    The process involves:
      1. Calculating dynamic obstacle metrics (DCPA and TCPA) relative to the agent.
      2. Determining indices of interest (I1, I2, I3) based on the distance safety threshold (dsf).
      3. Unionizing these indices to form the unionized unsafe indices of interest (uIoI).
      4. Generating the convex hull from the unionized unsafe set.

    Args:
        agent (Agent): The agent for which the unsafe set is to be computed.
        dynamic_obstacles (List[DynamicObstacle]): A list of dynamic obstacles.
        dsf (float): The distance safety threshold.

    Returns:
        List[int]: A list of indices representing the vertices of the convex hull of the unsafe set.
                   Returns an empty list if no unsafe regions are found.
    """
    # Calculate dynamic obstacle metrics (e.g., DCPA, TCPA) relative to the agent.
    dynamic_obstacle_metrics = calculate_obstacle_metrics_for_agent(
        agent_vessel=agent, dynamic_obstacles=dynamic_obstacles
    )

    # Compute indices of interest based on the safety threshold.
    I1 = calc_I1(
        agent=agent,
        dynamic_obstacles_with_metrics=dynamic_obstacle_metrics,
        dsf=dsf,
    )
    I2 = calc_I2(
        I1=I1,
        dynamic_obstacles_with_metrics=dynamic_obstacle_metrics,
        dsf=dsf,
    )
    I3 = calc_I3(
        dynamic_obstacles_with_metrics=dynamic_obstacle_metrics,
        dsf=dsf,
        time_of_interest=15
    )

    # Unionize the indices of interest.
    uIoI = unionise_indices_of_interest(I1, I2, I3)
    if not uIoI:
        return []

    # Generate and return the convex hull of the unsafe set.
    return gen_uIoI_convhull(uIoI)

