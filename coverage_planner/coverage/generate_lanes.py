
"""Module for generating coverage lanes for field traversal.

This module provides functionality to generate parallel lanes that cover
a given field polygon using a spacing-based approach.
"""

from shapely.geometry import LineString, MultiLineString
from coverage_planner.environments.field_loader import field_loader


def generate_lanes(field):
    """Generate parallel coverage lanes for a given field.

    Creates vertical lanes spaced at regular intervals across the field,
    clipping each lane to the field polygon boundary.

    Args:
        field (dict): Field configuration containing:
            - polygon: Shapely Polygon object representing field boundary
            - min_x, max_x: X-coordinate bounds of the field
            - min_y, max_y: Y-coordinate bounds of the field
            - lane_spacing (float): Distance between parallel lanes

    Returns:
        list: List of Shapely LineString objects representing coverage lanes
              clipped to the field boundary
    """
    field_polygon = field["polygon"]
    min_x = field["min_x"]
    max_x = field["max_x"]
    min_y = field["min_y"]
    max_y = field["max_y"]
    lane_spacing = field["lane_spacing"]
    coverage_segments = []

    # Start from half lane-spacing offset for even distribution
    current_x = min_x + lane_spacing / 2

    # Generate lanes from left to right across the field
    while current_x < max_x:
        # Create full-height candidate line (extended beyond field bounds)
        candidate_line = LineString([
            (current_x, min_y - 100),
            (current_x, max_y + 100)
        ])

        # Clip the line to the field polygon boundary
        clipped = candidate_line.intersection(field_polygon)

        # Handle both single and multiple intersections
        if isinstance(clipped, LineString):
            coverage_segments.append(clipped)
        elif isinstance(clipped, MultiLineString):
            for segment in clipped.geoms:
                coverage_segments.append(segment)

        current_x += lane_spacing

    return coverage_segments
