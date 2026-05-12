
from pathlib import Path
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, MultiLineString


def generate_lanes(field_polygon, min_x, max_x, min_y, max_y, lane_spacing):
    """
    Generate coverage lanes by intersecting vertical lines with the field polygon.
    
    Args:
        field_polygon: Shapely Polygon representing the field boundary
        min_x, max_x: X-axis bounds for lane generation
        min_y, max_y: Y-axis bounds for lane generation
        lane_spacing: Distance between adjacent lanes
    
    Returns:
        list: Coverage segments (LineString objects) representing the lanes
    """
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


polygon_file = Path('research/polygon_points.txt')
content = polygon_file.read_text().strip()

points = []

for line in content.splitlines():
    x, y = line.split(',')
    points.append((float(x), float(y)))

# Create polygon
field_polygon = Polygon(points)
if not field_polygon.is_valid:
    raise ValueError("Polygon is invalid. Check point ordering or intersections.")
min_x, min_y, max_x, max_y = field_polygon.bounds
print(f"Min X: {min_x}, Max X: {max_x}")
print(f"Min Y: {min_y}, Max Y: {max_y}")



lane_spacing = 10

coverage_segments = generate_lanes(field_polygon, min_x, max_x, min_y, max_y, lane_spacing)


ordered_segments = []

reverse_direction = False

for segment in coverage_segments:

    coords = list(segment.coords)

    start = coords[0]
    end = coords[-1]

    # Alternate traversal direction
    if reverse_direction:
        ordered_segments.append((end, start))
    else:
        ordered_segments.append((start, end))

    reverse_direction = not reverse_direction

plt.figure(figsize=(10, 10))

# Plot polygon boundary
x, y = field_polygon.exterior.xy
plt.plot(x, y, color='blue', linewidth=2, label='Field Boundary')

# Plot clipped coverage lanes
for idx, segment in enumerate(ordered_segments):

    start, end = segment

    plt.plot(
        [start[0], end[0]],
        [start[1], end[1]],
        color='red',
        linewidth=2
    )

    # Optional: draw traversal direction
    plt.arrow(
        start[0],
        start[1],
        (end[0] - start[0]) * 0.05,
        (end[1] - start[1]) * 0.05,
        head_width=3,
        length_includes_head=True,
        color='green'
    )

plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.title('CropFleet Coverage Lane Generation')
plt.grid(True)
plt.axis('equal')
plt.legend()

plt.show()