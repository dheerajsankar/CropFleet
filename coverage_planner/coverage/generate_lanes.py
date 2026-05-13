
from shapely.geometry import LineString, MultiLineString
from coverage_planner.enviroments.field_loader import field_loader


def generate_lanes(field):
    field_polygon = field["polygon"]
    min_x = field["min_x"]
    max_x = field["max_x"]
    min_y = field["min_y"]
    max_y = field["max_y"]
    lane_spacing = field["lane_spacing"]
    coverage_segments = []
    
    current_x = min_x + lane_spacing / 2

    while current_x < max_x:

        # Create full-height candidate line
        candidate_line = LineString([
            (current_x, min_y - 100),
            (current_x, max_y + 100)
        ])

        # Clip line with polygon
        clipped = candidate_line.intersection(field_polygon)

        if isinstance(clipped, LineString):
            coverage_segments.append(clipped)
        elif isinstance(clipped, MultiLineString):
            for segment in clipped.geoms:
                coverage_segments.append(segment)

        current_x += lane_spacing

    return coverage_segments
