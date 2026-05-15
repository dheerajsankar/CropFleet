"""Split line generation for polygon decomposition.

This module generates candidate split lines from concave vertices that can
be used to decompose complex polygons into simpler regions.
"""

from shapely.geometry import LineString
from shapely.ops import split
from math import sqrt


def split_generator(polygon, concave_points):
    """Generate candidate split lines from concave vertices.

    For each concave vertex, generates both horizontal and vertical split line
    candidates that extend from the vertex to the polygon boundary. These lines
    can be used to partition the polygon into simpler regions.

    Args:
        polygon: Shapely Polygon object to decompose
        concave_points: List of (x, y) tuples representing concave vertices

    Returns:
        tuple: (horizontal_splits, vertical_splits) where each is a list of
               Shapely LineString objects representing potential split lines.
               Only splits of sufficient length (≥1% of perimeter) are returned.

    Algorithm:
        1. For each concave vertex, create horizontal and vertical test lines
        2. Find intersections with polygon boundary
        3. Identify nearest intersection point (that's not the vertex itself)
        4. Create split line from vertex to boundary intersection
        5. Filter splits by minimum length threshold

    Notes:
        - Minimum split length is 1% of polygon perimeter (prevents trivial splits)
        - Only splits that can actually partition the polygon are returned
        - Handles edge cases: collinear intersections, multiple boundary points

    Example:
        >>> from shapely.geometry import Polygon
        >>> polygon = Polygon([(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4)])
        >>> concave = [(2, 2)]  # L-shaped polygon, concave at (2,2)
        >>> hor, ver = split_generator(polygon, concave)
    """
    hor_split_lines = []
    ver_split_lines = []
    
    # Calculate minimum split length threshold (1% of perimeter)
    # This prevents generating trivial split lines
    size = polygon.length
    percentage_size = size * 0.01
    
    # Process each concave vertex
    for i in concave_points:
        x = i[0]
        y = i[1]
        
        # Generate extended test lines (both horizontal and vertical)
        # Extended far beyond the polygon to ensure boundary intersection
        horizondal_line = LineString([(-1000, y), (1000, y)])
        vertical_line = LineString([(x, -1000), (x, 1000)])
        
        # Find intersections with polygon boundary
        hor_intersection = polygon.boundary.intersection(horizondal_line)
        ver_intersection = polygon.boundary.intersection(vertical_line)
        
        # Initialize tracking for best intersection points
        epsilon = 1e-6  # Tolerance for floating point comparison
        best_distance = float("inf")
        best_distance_vr = float("inf")
        best_point = None
        best_point_vr = None

        # Process horizontal line intersections
        # Convert single Point to list for uniform processing
        if hor_intersection.geom_type == "Point":
            points = [hor_intersection]
        elif hor_intersection.geom_type == "MultiPoint":
            points = hor_intersection.geoms
        else:
            points = []

        # Find nearest boundary intersection that's not the vertex itself
        for point in points:
            x1 = point.x
            y1 = point.y
            distance = sqrt((x - x1) ** 2 + (y - y1) ** 2)
            
            # Skip the vertex itself (distance near zero)
            if distance < epsilon:
                continue
            
            # Track the closest intersection point
            if distance < best_distance:
                best_distance = distance
                best_point = (x1, y1)

        # Process vertical line intersections (same logic)
        if ver_intersection.geom_type == "Point":
            ver_points = [ver_intersection]
        elif ver_intersection.geom_type == "MultiPoint":
            ver_points = ver_intersection.geoms
        else:
            ver_points = []

        for point in ver_points:
            x2 = point.x
            y2 = point.y
            distance_vr = sqrt((x - x2) ** 2 + (y - y2) ** 2)
            
            if distance_vr < epsilon:
                continue
            
            if distance_vr < best_distance_vr:
                best_distance_vr = distance_vr
                best_point_vr = (x2, y2)

        # Create and validate split lines based on length
        if best_point is not None:
            horizontal_split = LineString([(x, y), best_point])
            # Only include splits that are substantial enough
            if horizontal_split.length >= percentage_size:
                hor_split_lines.append(horizontal_split)
        
        if best_point_vr is not None:
            vertical_split = LineString([(x, y), best_point_vr])
            if vertical_split.length >= percentage_size:
                ver_split_lines.append(vertical_split)

    return hor_split_lines, ver_split_lines


def split_validation(polygon, hor_split_lines, ver_split_lines):
    """Validate split lines by checking if they actually partition the polygon.

    A valid split line must actually divide the polygon into two separate regions.
    This function tests each candidate split to ensure it's geometrically valid.

    Args:
        polygon: Shapely Polygon object
        hor_split_lines: List of horizontal candidate split lines (LineString)
        ver_split_lines: List of vertical candidate split lines (LineString)

    Returns:
        tuple: (valid_hor_splits, valid_ver_splits) containing only the split lines
               that successfully partition the polygon into two or more pieces.

    Algorithm:
        1. For each candidate split line, attempt to split the polygon
        2. Check if the result has 2 or more geometries
        3. Keep only splits that successfully partition the polygon
    """
    valid_hor_splits = []
    valid_ver_splits = []

    # Validate horizontal splits
    for i in hor_split_lines:
        # Attempt to split polygon with this line
        hor_test = split(polygon, i)
        # Use getattr to safely handle both GeometryCollection and other types
        geoms = getattr(hor_test, "geoms", [])
        
        # Valid split must create 2 or more separate pieces
        if len(geoms) >= 2:
            valid_hor_splits.append(i)

    # Validate vertical splits (same logic)
    for j in ver_split_lines:
        ver_test = split(polygon, j)
        ver_geoms = getattr(ver_test, "geoms", [])
        
        if len(ver_geoms) >= 2:
            valid_ver_splits.append(j)

    return valid_hor_splits, valid_ver_splits




        











     


