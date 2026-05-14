
"""Mission generation and path smoothing module.

This module provides functions to generate mission waypoints from coverage
segments and apply smoothing to create realistic drone flight paths with
smooth turns and transitions.
"""

import numpy as np


def generate_mission(ordered_segments):
    """Generate basic mission waypoints from coverage segments.

    Creates a waypoint list by connecting the start and end points of each
    coverage segment in sequence.

    Args:
        ordered_segments (list): List of (start_point, end_point) tuples
                                representing coverage segments in order

    Returns:
        list: List of (x, y) coordinate tuples representing mission waypoints
    """
    mission_waypoints = []

    for start, end in ordered_segments:
        # Add start point if it's not already the last waypoint
        if not mission_waypoints or mission_waypoints[-1] != start:
            mission_waypoints.append(start)

        # Add end point if it differs from the current last waypoint
        if mission_waypoints[-1] != end:
            mission_waypoints.append(end)

    return mission_waypoints


def generate_turn_arc(start_point, end_point, num_points=10, moving_up=True):
    """Generate a smooth curved arc between two points using Bezier interpolation.

    Creates a quadratic Bezier curve to smoothly transition between waypoints,
    useful for generating realistic drone flight paths.

    Args:
        start_point (tuple): Starting point (x, y) of the arc
        end_point (tuple): Ending point (x, y) of the arc
        num_points (int): Number of intermediate points to generate. Default: 10
        moving_up (bool): Direction of movement (True=up/forward, False=down).
                         Affects control point placement for realistic turns.

    Returns:
        list: List of (x, y) coordinate tuples representing the curved arc
              (excluding start and end points)
    """
    arc_points = []

    # Control point x-coordinate is at the midpoint
    control_x = (start_point[0] + end_point[0]) / 2

    # Control point y-coordinate depends on movement direction
    # This creates curves that loop outward for realistic turns
    if not moving_up:
        control_y = min(start_point[1], end_point[1]) - 20
    else:
        control_y = max(start_point[1], end_point[1]) + 20

    # Generate interpolated points along the Bezier curve
    # Exclude start (t=0) and end (t=1) points as they're already defined
    for t in np.linspace(0, 1, num_points)[1:-1]:
        # Quadratic Bezier formula: B(t) = (1-t)²*P0 + 2(1-t)*t*C + t²*P1
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
    """Generate smoothed mission waypoints with curved transitions.

    Takes coverage segments and generates a continuous path with smooth
    Bezier curves at transitions between segments, creating a realistic
    drone flight path.

    Args:
        ordered_segments (list): List of (start_point, end_point) tuples
                                representing coverage segments in order

    Returns:
        list: List of (x, y) coordinate tuples representing the smoothed
              mission path with curved transitions
    """
    smoothed_waypoints = []

    for i in range(len(ordered_segments) - 1):
        start, end = ordered_segments[i]

        # Determine direction of movement for curve control point placement
        moving_up = end[1] > start[1]
        next_start = ordered_segments[i + 1][0]

        # Add the current segment
        smoothed_waypoints.append(start)
        smoothed_waypoints.append(end)

        # Generate smooth arc if there's a gap between segments
        if end != next_start:
            arc_points = generate_turn_arc(end, next_start, moving_up=moving_up)
            smoothed_waypoints.extend(arc_points)

    # Add the final endpoint from the last segment
    smoothed_waypoints.append(ordered_segments[-1][1])

    return smoothed_waypoints