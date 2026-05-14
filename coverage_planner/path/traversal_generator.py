"""Module for generating traversal paths from coverage segments.

This module creates an ordered traversal path through coverage segments by
alternating the direction of travel. This approach minimizes turns and improves
efficiency in field coverage missions.
"""


def generate_traversal(coverage_segments):
    """Generate a traversal path through coverage segments with alternating directions.

    Processes coverage segments in order, alternating the direction of traversal
    (forward then backward) to create a continuous mission path. This boustrophedon
    (snake-like) pattern is efficient for lawn/field coverage operations.

    Args:
        coverage_segments: List of Shapely LineString objects representing
                          coverage lanes, ordered from first to last.

    Returns:
        list: List of tuples (start_point, end_point) representing directed
              traversal segments. Start and end are (x, y) coordinate tuples.

    Example:
        >>> segments = [LineString([(0, 0), (10, 0)]), LineString([(10, 1), (0, 1)])]
        >>> traversal = generate_traversal(segments)
        >>> # Results in: [((0, 0), (10, 0)), ((0, 1), (10, 1))]  # Second segment reversed
    """
    ordered_segments = []
    reverse_direction = False
    
    for segment in coverage_segments:
        # Extract start and end coordinates from the coverage segment
        coords = list(segment.coords)
        start = coords[0]
        end = coords[-1]
        
        # Alternate traversal direction for efficient coverage (boustrophedon pattern)
        if reverse_direction:
            # Reverse this segment: traverse from end to start
            ordered_segments.append((end, start))
        else:
            # Normal direction: traverse from start to end
            ordered_segments.append((start, end))
        
        # Toggle direction for next segment
        reverse_direction = not reverse_direction
    
    return ordered_segments
