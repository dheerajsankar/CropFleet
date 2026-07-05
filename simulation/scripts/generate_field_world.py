#!/usr/bin/env python3
"""Generate the Gazebo crop-field mesh from research/field.geojson.

Produces simulation/gazebo/models/crop_field/meshes/field.obj — a flat,
triangulated mesh of the field polygon in local ENU meters (x=east, y=north),
using the same origin (first polygon vertex) as
coverage_planner.enviroments.field_loader, so the Gazebo field lines up 1:1
with the planner's mission coordinates.

Pure stdlib on purpose: the equirectangular local projection used here differs
from field_loader's aeqd projection by well under a millimeter at field scale
(<100 m), and this keeps the script runnable outside the dev container.
"""

import json
import math
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GEOJSON = REPO_ROOT / "research" / "field.geojson"
MESH_DIR = REPO_ROOT / "simulation" / "gazebo" / "models" / "crop_field" / "meshes"

EARTH_RADIUS = 6378137.0


def load_polygon_enu():
    content = json.loads(GEOJSON.read_text(encoding="utf-8"))
    raw_points = content["features"][0]["geometry"]["coordinates"][0][0]
    origin_lon, origin_lat = raw_points[0][0], raw_points[0][1]
    cos_lat = math.cos(math.radians(origin_lat))
    points = []
    for lon, lat in (p[:2] for p in raw_points[:-1]):  # last point repeats the first
        east = math.radians(lon - origin_lon) * EARTH_RADIUS * cos_lat
        north = math.radians(lat - origin_lat) * EARTH_RADIUS
        points.append((east, north))
    return points, origin_lat, origin_lon


def signed_area(points):
    area = 0.0
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        area += x1 * y2 - x2 * y1
    return area / 2.0


def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def point_in_triangle(p, a, b, c):
    d1 = cross(a, b, p)
    d2 = cross(b, c, p)
    d3 = cross(c, a, p)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)


def ear_clip(points):
    """Triangulate a simple polygon (CCW) via ear clipping."""
    indices = list(range(len(points)))
    triangles = []
    while len(indices) > 3:
        clipped = False
        for k in range(len(indices)):
            i_prev = indices[k - 1]
            i_curr = indices[k]
            i_next = indices[(k + 1) % len(indices)]
            a, b, c = points[i_prev], points[i_curr], points[i_next]
            if cross(a, b, c) <= 0:  # reflex vertex, not an ear
                continue
            if any(
                point_in_triangle(points[j], a, b, c)
                for j in indices
                if j not in (i_prev, i_curr, i_next)
            ):
                continue
            triangles.append((i_prev, i_curr, i_next))
            indices.pop(k)
            clipped = True
            break
        if not clipped:
            raise RuntimeError("Ear clipping failed: polygon may be non-simple")
    triangles.append(tuple(indices))
    return triangles


def write_obj(points, triangles):
    MESH_DIR.mkdir(parents=True, exist_ok=True)
    mtl_path = MESH_DIR / "field.mtl"
    mtl_path.write_text(
        "newmtl crop_green\n"
        "Ka 0.05 0.20 0.03\n"
        "Kd 0.13 0.45 0.10\n"
        "Ks 0.0 0.0 0.0\n"
        "d 1.0\n",
        encoding="utf-8",
    )
    lines = ["# CropFleet field mesh (local ENU meters, origin = first geojson vertex)"]
    lines.append("mtllib field.mtl")
    for x, y in points:
        lines.append(f"v {x:.3f} {y:.3f} 0.000")
    lines.append("vn 0 0 1")
    lines.append("usemtl crop_green")
    for i, j, k in triangles:
        lines.append(f"f {i+1}//1 {j+1}//1 {k+1}//1")
    obj_path = MESH_DIR / "field.obj"
    obj_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return obj_path


def main():
    points, origin_lat, origin_lon = load_polygon_enu()
    if signed_area(points) < 0:
        points.reverse()
    triangles = ear_clip(points)
    obj_path = write_obj(points, triangles)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    print(f"Wrote {obj_path}")
    print(f"Origin lat/lon: {origin_lat}, {origin_lon}")
    print(f"East span : {min(xs):.1f} .. {max(xs):.1f} m")
    print(f"North span: {min(ys):.1f} .. {max(ys):.1f} m")
    print(f"Area      : {abs(signed_area(points)):.1f} m^2, {len(triangles)} triangles")


if __name__ == "__main__":
    main()
