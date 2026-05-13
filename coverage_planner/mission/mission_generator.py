
import numpy as np
def generate_mission(ordered_segments):
    mission_waypoints = []

    for start, end in ordered_segments:

        if not mission_waypoints or mission_waypoints[-1] != start:
            mission_waypoints.append(start)
        
        if mission_waypoints[-1] != end:
            mission_waypoints.append(end)
    return mission_waypoints



def generate_turn_arc(start_point, end_point, num_points=10,  moving_up=True):
    arc_points = []
    # Control point for curve shaping
    control_x = (start_point[0] + end_point[0]) / 2

    if not moving_up:
        control_y = min(start_point[1], end_point[1]) - 20
    else:
        control_y = max(start_point[1], end_point[1]) + 20

    # Quadratic Bezier interpolation
    for t in np.linspace(0, 1, num_points)[1:-1]:  # Exclude start and end points
        x = (
            (1 - t) ** 2 * start_point[0] +
            2 * (1 - t) * t * control_x +
            t ** 2 * end_point[0]
        )
        y = (
            (1 - t) ** 2 * start_point[1] +
            2 * (1 - t) * t * control_y +
            t ** 2 * end_point[1]
        )
        arc_points.append((x, y))
    return arc_points


def generate_smoothed_mission(ordered_segments):
    smoothed_waypoints = []
    for i in range(len(ordered_segments) - 1):
        start, end = ordered_segments[i]
        moving_up = end[1] > start[1]
        next_start = ordered_segments[i + 1][0]
        smoothed_waypoints.append(start)
        smoothed_waypoints.append(end)

        # Check if there's a direction change
        if end != next_start:
            arc_points = generate_turn_arc(end, next_start, moving_up=moving_up)
            smoothed_waypoints.extend(arc_points)

    smoothed_waypoints.append(ordered_segments[-1][1])  # Add the final endpoint
    return smoothed_waypoints