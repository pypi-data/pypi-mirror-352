import numpy as np
from typing import List, Sequence
from scipy.spatial import ConvexHull
from colav_unsafe_set.objects import DynamicObstacleWithMetrics
from colav_unsafe_set.position_prediction import predict_position

def gen_uIoI_convhull(uIoI: List[DynamicObstacleWithMetrics]) -> List[List[float]]:
    """
    Generate the convex hull points of the union of safety regions from a list of dynamic obstacles.
    
    Each dynamic obstacle's safety region is approximated as a circle (using _generate_circle_vertices). 
    The union of all vertices from these circles is then used to compute the convex hull, and the function 
    returns the coordinates of the hull's vertices.
    
    Args:
        uIoI (List[DynamicObstacleWithMetrics]): A list of dynamic obstacles with associated metrics.
    
    Returns:
        List[List[float]]: A list of coordinate pairs representing the convex hull vertices.
    """
    # Collect vertices for current positions
    unsafe_set_vertices: List[List[float]] = [
        vertex
        for dynamic_obstacle in uIoI
        for vertex in _generate_circle_vertices(
            centroid=[
                dynamic_obstacle.dynamic_obstacle.position[0],
                dynamic_obstacle.dynamic_obstacle.position[1]
            ],
            radius=dynamic_obstacle.dynamic_obstacle.safety_radius
        )
    ]

    # Collect vertices for predicted future positions
    for dynamic_obstacle in uIoI:
        if dynamic_obstacle.tcpa > 0 and not np.isnan(dynamic_obstacle.tcpa):
            future_position = predict_position(
                position=dynamic_obstacle.dynamic_obstacle.position,
                quaternion_orientation=dynamic_obstacle.dynamic_obstacle.orientation,
                velocity=dynamic_obstacle.dynamic_obstacle.velocity,
                yaw_rate=dynamic_obstacle.dynamic_obstacle.yaw_rate,
                dt=dynamic_obstacle.tcpa
            ) 
            # Use extend to avoid nested lists
            unsafe_set_vertices.extend(
                _generate_circle_vertices(
                    centroid=[future_position[0], future_position[1]],
                    radius=dynamic_obstacle.dynamic_obstacle.safety_radius
                )
            )

    if not unsafe_set_vertices:
        return []
    
    unsafe_set_vertices = np.array(unsafe_set_vertices, dtype=np.float64)  # Ensure float type
    hull_indices = ConvexHull(unsafe_set_vertices).vertices
    hull_points = unsafe_set_vertices[hull_indices].tolist()  # Convert back to a list of lists

    return hull_points


def _generate_circle_vertices(centroid: Sequence[float], radius: float, num_points: int = 10) -> List[List[float]]:
    """
    Generate vertices approximating a circle in the XY plane.
    
    The circle is defined by its centroid and radius, and is approximated by 'num_points' evenly spaced vertices.
    
    Args:
        centroid (Sequence[float]): The (x, y) coordinates of the circle's center.
        radius (float): The radius of the circle.
        num_points (int): The number of vertices to generate (default is 10).
        
    Returns:
        List[List[float]]: A list of [x, y] vertices representing the circle.
    """
    x_c, y_c = centroid
    theta = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    x = x_c + radius * np.cos(theta)
    y = y_c + radius * np.sin(theta)
    circle_vertices = np.column_stack((x, y))
    return circle_vertices.tolist()
