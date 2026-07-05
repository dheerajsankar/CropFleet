from shapely.geometry import LineString
from shapely.ops import split
from math import sqrt

def split_generator(polygon,concave_points):
    hor_split_lines = []
    ver_split_lines=  []
    size = polygon.length
    percentage_size = size * 0.01
    for i in concave_points:
        x = i[0]
        y = i[1]
        horizondal_line = LineString([(-1000, y), (1000, y)])
        vertical_line  = LineString([(x, -1000), (x, 1000)])
        hor_intersection = polygon.boundary.intersection(horizondal_line)
        ver_intersection = polygon.boundary.intersection(vertical_line)
        epsilon = 1e-6
        best_distance = float("inf")
        best_distance_vr = float("inf")
        best_point = None
        best_point_vr =  None

        if hor_intersection.geom_type == "Point":
            points = [hor_intersection]
        elif hor_intersection.geom_type == "MultiPoint":
            points = hor_intersection.geoms
        else:
            points = []

        for point in points:
            x1= point.x
            y1= point.y
            distance = sqrt((x-x1)**2 + (y-y1)**2)
            if distance < epsilon:
                continue
            if distance  < best_distance:
                best_distance = distance
                best_point =  (x1,y1)

        if ver_intersection.geom_type == "Point":
            ver_points = [ver_intersection]
        elif ver_intersection.geom_type == "MultiPoint":
            ver_points = ver_intersection.geoms
        else:
            ver_points = []

        for point in ver_points:
            x2 = point.x
            y2 = point.y
            distance_vr = sqrt((x-x2)**2 + (y-y2)**2)
            if distance_vr < epsilon:
                continue
            if distance_vr  < best_distance_vr:
                best_distance_vr = distance_vr
                best_point_vr =  (x2,y2)

        if best_point is not None:
            horizontal_split = LineString([(x, y),best_point])
            if horizontal_split.length >= percentage_size:
                hor_split_lines.append(horizontal_split)
        if best_point_vr is not None:
            vertical_split = LineString([(x, y),best_point_vr])
            if vertical_split.length >= percentage_size:
                ver_split_lines.append(vertical_split)

    return hor_split_lines, ver_split_lines


def split_validation(polygon, hor_split_lines,ver_split_lines):
    valid_hor_splits= []
    valid_ver_splits= []

    for i in hor_split_lines:
        hor_test = split(polygon, i)
        geoms = getattr(hor_test, "geoms", [])
        if len(geoms) >= 2:
            valid_hor_splits.append(i)

    for j in ver_split_lines:
        ver_test = split(polygon, j)
        ver_geoms = getattr(ver_test, "geoms", [])
        if len(ver_geoms) >= 2:
            valid_ver_splits.append(j)

    return valid_hor_splits, valid_ver_splits




        











     


