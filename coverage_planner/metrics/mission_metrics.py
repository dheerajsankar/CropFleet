"""Mission metrics calculation module.

This module provides functionality to calculate and analyze mission performance
metrics including distance traveled, coverage efficiency, and transition costs.
"""


def calculate_all_metrics(mission_waypoints, ordered_segments):
    """Calculate comprehensive mission performance metrics.

    Computes the total distance traveled, coverage distance, transition distance,
    and coverage efficiency for a mission plan.

    Args:
        mission_waypoints (list): List of (x, y) coordinate tuples representing
                                  the complete mission path waypoints
        ordered_segments (list): List of (start_point, end_point) tuples
                                representing the coverage segments

    Returns:
        dict: Dictionary containing:
            - 'total_distance' (float): Total distance traveled in the mission
            - 'coverage_distance' (float): Distance spent actively covering
            - 'transition_distance' (float): Distance spent in transitions
            - 'coverage_efficiency' (float): Percentage of mission distance spent
                                             on coverage (0-100)
    """
    total_distance = 0.0

    # Calculate total distance traveled across all waypoints
    for i in range(1, len(mission_waypoints)):
        x1, y1 = mission_waypoints[i - 1]
        x2, y2 = mission_waypoints[i]
        # Euclidean distance calculation
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        total_distance += distance

    # Calculate distance spent on actual coverage segments
    coverage_distance = 0.0
    for start, end in ordered_segments:
        x1, y1 = start
        x2, y2 = end
        # Euclidean distance calculation
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        coverage_distance += distance

    # Calculate the distance spent transitioning between coverage segments
    transition_distance = total_distance - coverage_distance

    # Calculate coverage efficiency as a percentage
    if total_distance > 0:
        coverage_efficiency = (coverage_distance / total_distance) * 100
    else:
        coverage_efficiency = 0.0

    return {
        "total_distance": total_distance,
        "coverage_distance": coverage_distance,
        "transition_distance": transition_distance,
        "coverage_efficiency": coverage_efficiency
    }




    
