import json
import os
from pathlib import Path

from pyproj import Transformer, CRS
from shapely.geometry import Polygon


def _find_geojson():
    """Locate research/field.geojson across install layouts.

    Priority: CROPFLEET_FIELD_GEOJSON env var (set in the Docker image, where
    the package is not installed editable), then the repo-relative path (works
    for editable installs and running from a checkout), then the current
    working directory.
    """
    env_path = os.environ.get("CROPFLEET_FIELD_GEOJSON")
    if env_path:
        return Path(env_path)
    candidates = [
        Path(__file__).resolve().parent.parent.parent / "research" / "field.geojson",
        Path.cwd() / "research" / "field.geojson",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "research/field.geojson not found. Run from the repo root or set "
        "CROPFLEET_FIELD_GEOJSON to the geojson path."
    )


def field_loader(path=None):
    path = Path(path) if path else _find_geojson()
    with open(path, 'r', encoding='utf-8') as file:
        content = json.load(file)
    raw_points = content["features"][0]["geometry"]["coordinates"][0][0]
    meter_coordinates = []
    origin_lon = raw_points[0][0]
    origin_lat = raw_points[0][1]
    local_crs = CRS.from_proj4(f"+proj=aeqd +lat_0={origin_lat} +lon_0={origin_lon} +units=m")
    wgs84_crs = CRS.from_epsg(4326)
    transformer = Transformer.from_crs(wgs84_crs, local_crs, always_xy=True)
    for point in raw_points[:-1]:
        lon, lat = point[0], point[1]
        east, north = transformer.transform(lon, lat)
        meter_coordinates.append((east, north))
    field_polygon = Polygon(meter_coordinates)
    if not field_polygon.is_valid:
        raise ValueError("Polygon is invalid. Check point ordering or intersections.")
    min_x, min_y, max_x, max_y = field_polygon.bounds
    lane_spacing = 5
    field = {
        "polygon": field_polygon,
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "lane_spacing": lane_spacing,
        "origin_lat": origin_lat,
        "origin_lon": origin_lon
    }
    return field
