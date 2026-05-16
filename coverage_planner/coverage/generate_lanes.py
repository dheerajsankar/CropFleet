
from shapely.geometry import LineString, MultiLineString

def generate_lanes(polygon, lane_spacing,direction = "vertical"):

    min_x, min_y, max_x, max_y = polygon.bounds
    coverage_segments = []

    if  direction  == "vertical":
        current_x = min_x + lane_spacing / 2

        while current_x < max_x:

            # Create full-height candidate line
            candidate_line = LineString([
                (current_x, min_y - 100),
                (current_x, max_y + 100)
            ])

            # Clip line with polygon
            clipped = candidate_line.intersection(polygon)

            if isinstance(clipped, LineString):
                coverage_segments.append(clipped)
            elif isinstance(clipped, MultiLineString):
                for segment in clipped.geoms:
                    coverage_segments.append(segment)

            current_x += lane_spacing

    elif direction == "horizontal":
        current_y = min_y + lane_spacing / 2

        while current_y < max_y:

            # Create full-height candidate line
            candidate_line = LineString([
                (min_x - 100, current_y),
                (max_x + 100, current_y)
            ])

            # Clip line with polygon
            clipped = candidate_line.intersection(polygon)

            if isinstance(clipped, LineString):
                coverage_segments.append(clipped)
            elif isinstance(clipped, MultiLineString):
                for segment in clipped.geoms:
                    coverage_segments.append(segment)

            current_y += lane_spacing


    return coverage_segments

