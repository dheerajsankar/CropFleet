def generate_traversal(coverage_segments,start_reverse=False):
    ordered_segments = []
    reverse_direction = start_reverse
    for segment in coverage_segments:
        coords = list(segment.coords)
        start = coords[0]
        end = coords[-1]
        if reverse_direction:
            ordered_segments.append((end, start))
        else:
            ordered_segments.append((start, end))
        reverse_direction = not reverse_direction
    return ordered_segments



