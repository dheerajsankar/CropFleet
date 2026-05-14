"""Module for generating decomposition lines at concave vertices.

This module creates horizontal and vertical split lines from concave vertices
to the polygon boundary. These lines are used to decompose complex field polygons
into simpler convex or near-convex regions for efficient coverage planning.
"""

from shapely.geometry import LineString
from math import sqrt


def split_generator(polygon, concave_points):
    """Generate horizontal and vertical split lines from concave vertices.

    For each concave vertex, creates a horizontal and vertical line extending
    to the polygon boundary. Lines shorter than 1% of polygon perimeter are
    filtered out to avoid creating very short decomposition segments.

    Args:
        polygon: A Shapely polygon object representing the field.
        concave_points: List of (x, y) tuples representing concave vertices.

    Returns:
        tuple: Two lists containing:
            - hor_split_lines: LineString objects representing horizontal splits
            - ver_split_lines: LineString objects representing vertical splits

    Algorithm:
        1. For each concave point, create horizontal and vertical lines
        2. Find intersection points with polygon boundary
        3. Select closest intersection point (avoiding the concave point itself)
        4. Keep splits exceeding minimum length (1% of perimeter)
    """
    hor_split_lines = []
    ver_split_lines = []
    
    # Calculate minimum split line length (1% of polygon perimeter)
    size = polygon.length
    percentage_size = size * 0.01
    
    # Process each concave vertex
    for i in concave_points:
        x = i[0]
        y = i[1]
        
        # Create extended horizontal and vertical lines through the concave point
        # Lines are extended far beyond polygon to ensure intersection
        horizontal_line = LineString([(-1000, y), (1000, y)])
        vertical_line = LineString([(x, -1000), (x, 1000)])
        
        # Find intersection points with polygon boundary
        hor_intersection = polygon.boundary.intersection(horizontal_line)
        ver_intersection = polygon.boundary.intersection(vertical_line)
        
        # Tolerance for identifying concave point itself
        epsilon = 1e-6
        best_distance = float("inf")
        best_distance_vr = float("inf")
        best_point = None
        best_point_vr = None

        # Extract horizontal intersection points
        if hor_intersection.geom_type == "Point":
            points = [hor_intersection]
        elif hor_intersection.geom_type == "MultiPoint":
            points = hor_intersection.geoms
        else:
            points = []

        # Find the closest intersection point (excluding the concave point itself)
        for point in points:
            x1 = point.x
            y1 = point.y
            distance = sqrt((x - x1) ** 2 + (y - y1) ** 2)
            
            # Skip if this is the concave point itself
            if distance < epsilon:
                continue
            
            if distance < best_distance:
                best_distance = distance
                best_point = (x1, y1)

        # Extract vertical intersection points
        if ver_intersection.geom_type == "Point":
            ver_points = [ver_intersection]
        elif ver_intersection.geom_type == "MultiPoint":
            ver_points = ver_intersection.geoms
        else:
            ver_points = []

        # Find the closest intersection point (excluding the concave point itself)
        for point in ver_points:
            x2 = point.x
            y2 = point.y
            distance_vr = sqrt((x - x2) ** 2 + (y - y2) ** 2)
            
            # Skip if this is the concave point itself
            if distance_vr < epsilon:
                continue
            
            if distance_vr < best_distance_vr:
                best_distance_vr = distance_vr
                best_point_vr = (x2, y2)

        # Create and add horizontal split line if it meets minimum length requirement
        if best_point is not None:
            horizontal_split = LineString([(x, y), best_point])
            if horizontal_split.length >= percentage_size:
                hor_split_lines.append(horizontal_split)
        
        # Create and add vertical split line if it meets minimum length requirement
        if best_point_vr is not None:
            vertical_split = LineString([(x, y), best_point_vr])
            if vertical_split.length >= percentage_size:
                ver_split_lines.append(vertical_split)

    return hor_split_lines, ver_split_lines



        











     


