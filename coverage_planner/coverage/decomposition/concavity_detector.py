
"""Module for detecting concave vertices in polygons.

This module provides functions to identify concave (reflex) vertices in a polygon,
which are points where the interior angle exceeds 180 degrees. This is useful for
decomposing complex field shapes into simpler regions for coverage planning.
"""

import numpy as np


def detect_concave_vertices(polygon):
    """Detect concave vertices in a polygon.

    Uses the cross product method to identify concave vertices by analyzing
    the orientation of consecutive edge vectors. For each vertex, computes
    the cross product of incoming and outgoing edges; a sign change indicates
    a concavity (relative to polygon winding direction).

    Args:
        polygon: A Shapely polygon object with an exterior ring.

    Returns:
        list: List of (x, y) tuples representing concave vertices.
              Empty list if polygon is convex.

    Algorithm:
        1. Determines polygon winding order (CW/CCW) using shoelace formula
        2. For each vertex, computes cross product of consecutive edge vectors
        3. Identifies concave points where cross product sign mismatches winding
    """
    # Extract polygon vertices
    points = list(polygon.exterior.coords)
    
    # Calculate polygon winding order using shoelace formula
    orientation_sum = 0
    concave_points = []
    for i in range(len(points)):
        current_point = points[i]
        next_point = points[(i + 1) % len(points)]

        # Shoelace formula component for orientation calculation
        orientation_sum += (
            (next_point[0] - current_point[0]) *
            (next_point[1] + current_point[1])
        )

    # Determine if polygon is clockwise (CW) or counterclockwise (CCW)
    if orientation_sum > 0:
        polygon_winding = "CW"
    else:
        polygon_winding = "CCW"

    # Iterate through each vertex and check for concavity
    for i in range(len(points)):
        prev_point = points[i - 1]
        current_point = points[i]
        next_point = points[(i + 1) % len(points)]
        
        # Create vectors for edge detection
        v1 = np.array(prev_point)  # Previous vertex
        v2 = np.array(current_point)  # Current vertex
        v3 = np.array(next_point)  # Next vertex
        
        # Compute edge vectors
        v4 = np.array(v2 - v1)  # Incoming edge vector
        v5 = np.array(v3 - v2)  # Outgoing edge vector
        
        # Cross product determines if vertex is concave
        # Negative cross product with CW or positive with CCW indicates concavity
        cross_product = np.cross(v4, v5)
        
        if cross_product < 0 and polygon_winding == "CW":
            concave_points.append(current_point)
        elif cross_product > 0 and polygon_winding == "CCW":
            concave_points.append(current_point)

    return concave_points


            



        




    











