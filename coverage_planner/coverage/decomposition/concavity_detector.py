
"""Concave vertex detection for polygon decomposition.

This module identifies concave (reflex) vertices in a polygon. These vertices
are critical for polygon decomposition, as they represent points where split
lines should be generated to simplify complex geometries.
"""

import numpy as np


def detect_concave_vertices(polygon):
    """Detect all concave (reflex) vertices in a polygon.

    A concave vertex is a point where the interior angle exceeds 180 degrees.
    These vertices are important for decomposing complex polygons into simpler
    convex regions.

    Args:
        polygon: Shapely Polygon object to analyze

    Returns:
        list: List of (x, y) coordinate tuples representing concave vertices.
              Returns empty list if polygon is convex.

    Algorithm:
        1. Determine polygon winding order (clockwise or counter-clockwise)
           using the shoelace formula
        2. For each vertex, compute the cross product of edge vectors
        3. Identify vertices where cross product indicates a reflex angle
           (sign depends on winding order)

    Notes:
        - Uses the cross product of consecutive edge vectors to detect reflex angles
        - Takes winding order into account (CW vs CCW)
        - Efficient O(n) algorithm for n vertices

    Example:
        >>> from shapely.geometry import Polygon
        >>> # L-shaped polygon with one concave vertex
        >>> L_shape = Polygon([(0,0), (2,0), (2,1), (1,1), (1,2), (0,2)])
        >>> concave = detect_concave_vertices(L_shape)
        >>> len(concave)  # Should be > 0 for concave polygon
    """
    # Extract all vertices from the polygon boundary
    points = list(polygon.exterior.coords)
    
    # Determine polygon winding order using the shoelace/surveyor's formula
    # This calculates twice the signed area of the polygon
    orientation_sum = 0
    for i in range(len(points)):
        current_point = points[i]
        next_point = points[(i + 1) % len(points)]

        # Accumulate cross product terms
        orientation_sum += (
            (next_point[0] - current_point[0]) *
            (next_point[1] + current_point[1])
        )

    # Determine winding order from orientation_sum sign
    # Positive = clockwise, Negative = counter-clockwise (standard math convention)
    if orientation_sum > 0:
        polygon_winding = "CW"
    else:
        polygon_winding = "CCW"

    # Identify concave vertices by checking cross products
    concave_points = []
    for i in range(len(points)):
        # Get three consecutive vertices
        prev_point = points[i - 1]
        current_point = points[i]
        next_point = points[(i + 1) % len(points)]
        
        # Convert to vectors
        v1 = np.array(prev_point)
        v2 = np.array(current_point)
        v3 = np.array(next_point)
        
        # Compute edge vectors
        v4 = np.array(v2 - v1)  # Vector from prev to current
        v5 = np.array(v3 - v2)  # Vector from current to next
        
        # Cross product indicates turn direction
        # For 2D, this is the z-component of the 3D cross product
        cross_product = np.cross(v4, v5)
        
        # Identify reflex angles based on winding order
        # For CW: negative cross product = left turn = reflex angle
        # For CCW: positive cross product = left turn = reflex angle
        if cross_product < 0 and polygon_winding == "CW":
            concave_points.append(current_point)

        elif cross_product > 0 and polygon_winding == "CCW":
            concave_points.append(current_point)

    return concave_points


            



        




    











