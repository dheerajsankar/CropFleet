
import numpy as np
def detect_concave_vertices(polygon):
    points  = list(polygon.exterior.coords)
    orientation_sum = 0
    concave_points = []
    for i in range(len(points)):
        current_point = points[i]
        next_point = points[(i + 1) % len(points)]

        orientation_sum += (
            (next_point[0] - current_point[0]) *
            (next_point[1] + current_point[1])
        )

    if orientation_sum > 0:
        polygon_winding = "CW"
    else:
        polygon_winding = "CCW"

    for i in range(len(points)):
        prev_point =  points[i-1]
        current_point = points[i]
        next_point = points[(i+1) % len(points)]
        v1  =  np.array(prev_point)
        v2 = np.array(current_point)
        v3  = np.array(next_point)
        v4 = np.array(v2-v1)
        v5 = np.array(v3-v2)
        # 2D cross product done manually: np.cross on 2D vectors is
        # deprecated in NumPy 2.x and scheduled for removal
        cross_product = v4[0] * v5[1] - v4[1] * v5[0]
        if cross_product < 0 and polygon_winding == "CW":
            concave_points.append(current_point)

        elif cross_product > 0 and polygon_winding == "CCW":
            concave_points.append(current_point)

    return concave_points


            



        




    











