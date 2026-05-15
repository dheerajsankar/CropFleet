"""Main coverage planning pipeline.

This module orchestrates the complete coverage planning workflow by combining
polygon decomposition and lane generation to produce coverage segments.
"""

from coverage_planner.coverage.decomposition.recursive_decomposer import recursive_decompose
from coverage_planner.coverage.generate_lanes import generate_lanes


def run_pipe(polygon):
    """Execute the complete coverage planning pipeline.

    Performs polygon decomposition to break down complex field boundaries into
    simpler cells, then generates parallel coverage lanes for each decomposed cell.

    Args:
        polygon: Shapely Polygon object representing the field boundary

    Returns:
        list: List of Shapely LineString objects representing coverage segments
              that span the field with parallel sweep lines

    Example:
        >>> from shapely.geometry import Polygon
        >>> field = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
        >>> coverage_segments = run_pipe(field)
    """
    segments = []
    
    # Step 1: Recursively decompose the polygon into simpler cells
    # This simplifies complex field geometries for efficient coverage
    decompose = recursive_decompose(polygon)
    
    # Step 2: Generate coverage lanes for each decomposed cell
    # Lane spacing is set to 10 units (typically pixels or meters)
    for cells in decompose:
        segments.extend(generate_lanes(cells, lane_spacing=10))
    
    return segments







