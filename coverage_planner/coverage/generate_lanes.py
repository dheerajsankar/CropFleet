"""Coverage lane generation using parallel sweep-line algorithm.

This module generates parallel coverage lanes that span a polygon region.
Lanes are created using a sweep-line algorithm and clipped to the polygon
boundary to ensure complete field coverage.
"""

from shapely.geometry import LineString, MultiLineString


def generate_lanes(polygon, lane_spacing):
    """Generate parallel coverage lanes within a polygon using sweep-line algorithm.

    Creates vertical parallel lines spaced at regular intervals across the polygon
    bounds, then clips them to the polygon boundary. This produces continuous
    coverage lanes that traverse the field.

    Args:
        polygon: Shapely Polygon object representing the field boundary
        lane_spacing (float): Distance between parallel lanes (in coordinate units)

    Returns:
        list: List of Shapely LineString objects representing clipped coverage lanes.
              Each LineString is a segment of a sweep line that intersects the polygon.

    Notes:
        - Lines are extended beyond polygon bounds (±100 units) to ensure complete
          intersection coverage
        - Handles both single-line and multi-line intersections (for complex polygons)
        - Lane spacing should be chosen based on vehicle width and desired coverage

    Example:
        >>> from shapely.geometry import Polygon
        >>> field = Polygon([(0, 0), (100, 0), (100, 50), (0, 50)])
        >>> lanes = generate_lanes(field, lane_spacing=10)
        >>> len(lanes)  # Number of coverage lanes generated
    """
    # Extract bounding box of the polygon
    min_x, min_y, max_x, max_y = polygon.bounds
    coverage_segments = []
    
    # Start from the first lane position (centered between min_x and min_x + lane_spacing)
    current_x = min_x + lane_spacing / 2

    # Generate sweep lines from left to right across the polygon bounds
    while current_x < max_x:
        # Create a vertical candidate line extending well beyond polygon bounds
        # This ensures we capture all intersections with the polygon boundary
        candidate_line = LineString([
            (current_x, min_y - 100),  # Extended below
            (current_x, max_y + 100)   # Extended above
        ])

        # Intersect the candidate line with the polygon boundary
        clipped = candidate_line.intersection(polygon)

        # Handle different intersection types:
        # A single LineString means one continuous coverage segment
        if isinstance(clipped, LineString):
            coverage_segments.append(clipped)
        # MultiLineString occurs with concave polygons (multiple segments per line)
        elif isinstance(clipped, MultiLineString):
            # Add each segment separately
            for segment in clipped.geoms:
                coverage_segments.append(segment)

        # Move to the next lane position
        current_x += lane_spacing

    return coverage_segments

