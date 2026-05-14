
"""Field configuration loader module.

This module handles loading field boundary definitions from polygon point files
and generating field configuration objects with geometric bounds and coverage
parameters.
"""

from shapely.geometry import Polygon
from pathlib import Path


def field_loader():
    """Load and configure field data from polygon points file.

    Reads polygon point coordinates from a file, constructs a Shapely Polygon,
    validates it, and generates a field configuration dictionary with bounds
    and coverage parameters.

    The polygon points file should contain one point per line in the format:
        x,y

    Returns:
        dict: Field configuration containing:
            - 'polygon' (Polygon): Shapely Polygon object of field boundary
            - 'min_x' (float): Minimum x-coordinate of field bounds
            - 'min_y' (float): Minimum y-coordinate of field bounds
            - 'max_x' (float): Maximum x-coordinate of field bounds
            - 'max_y' (float): Maximum y-coordinate of field bounds
            - 'lane_spacing' (float): Spacing between coverage lanes (pixels)

    Raises:
        ValueError: If the polygon is invalid (self-intersecting or malformed)
        FileNotFoundError: If the polygon points file is not found
    """
    # Load polygon points from file
    path = Path('research/polygon_points.txt')
    content = path.read_text().strip()

    # Parse coordinates from file
    coordinates = []
    for line in content.splitlines():
        x, y = line.split(',')
        coordinates.append((float(x), float(y)))

    # Create Polygon from coordinates
    field_polygon = Polygon(coordinates)

    # Validate polygon integrity
    if not field_polygon.is_valid:
        raise ValueError("Polygon is invalid. Check point ordering or intersections.")

    # Extract bounding box from polygon
    min_x, min_y, max_x, max_y = field_polygon.bounds

    # Define lane spacing for coverage generation (in pixels)
    lane_spacing = 40

    # Construct field configuration dictionary
    field = {
        "polygon": field_polygon,
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "lane_spacing": lane_spacing
    }

    return field