from colav_unsafe_set.objects import DynamicObstacleWithMetrics
from typing import List

def unionise_indices_of_interest(
    I1: List[DynamicObstacleWithMetrics],
    I2: List[DynamicObstacleWithMetrics],
    I3: List[DynamicObstacleWithMetrics],
) -> List[DynamicObstacleWithMetrics]:
    """Unionise the indices of interest by removing duplicates using object identity."""
    # Use a dict keyed by the object's id to eliminate duplicates.
    union_dict = {id(item): item for item in (I1 + I2 + I3)}
    return list(union_dict.values())
