
from shapely.geometry import Polygon
from pathlib import Path


def field_loader():
    path = Path('research/polygon_points.txt')
    content = path.read_text().strip()
    coordinates = []
    for line in content.splitlines():
        x, y = line.split(',')
        coordinates.append((float(x), float(y)))
    field_polygon = Polygon(coordinates)
    if not field_polygon.is_valid:
        raise ValueError("Polygon is invalid. Check point ordering or intersections.")
    min_x, min_y, max_x, max_y = field_polygon.bounds
    lane_spacing = 40
    field = {
        "polygon": field_polygon,
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "lane_spacing": lane_spacing
    }
    return field