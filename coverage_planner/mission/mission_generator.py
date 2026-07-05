from shapely.geometry import Point
import numpy as np
from  math import atan2
def generate_mission(ordered_segments):
    mission_waypoints = []


    for start, end in ordered_segments:

        if not mission_waypoints:
            mission_waypoints.append((start[0], start[1], True))

        elif mission_waypoints[-1][:2] != start:
            mission_waypoints.append((start[0], start[1], False))
        else:
            mission_waypoints.append((start[0], start[1],True))

        if mission_waypoints[-1][:2] != end:
            mission_waypoints.append((end[0],end[1], True))
        
    return mission_waypoints



def generate_turn_arc(start_point, end_point, num_points=10,  moving_up=True):
    arc_points = []
    control_x = (start_point[0] + end_point[0]) / 2

    if not moving_up:
        control_y = min(start_point[1], end_point[1]) - 5
    else:
        control_y = max(start_point[1], end_point[1]) + 5

    for t in np.linspace(0, 1, num_points)[1:-1]:  
        x = (
            (1 - t) ** 2 * start_point[0] +
            2 * (1 - t) * t * control_x +
            t ** 2 * end_point[0]
        )
        y = (
            (1 - t) ** 2 * start_point[1] +
            2 * (1 - t) * t * control_y +
            t ** 2 * end_point[1]
        )
        arc_points.append((x, y))
    return arc_points


def generate_smoothed_mission(ordered_segments, polygon):
    if not ordered_segments:
        return []
    smoothed_waypoints = []
    for i in range(len(ordered_segments) - 1):
        start, end = ordered_segments[i]
        moving_up = end[1] > start[1]
        next_start = ordered_segments[i + 1][0]
        smoothed_waypoints.append(start)
        smoothed_waypoints.append(end)

        if end != next_start:
            arc_points = generate_turn_arc(end, next_start, moving_up=moving_up)
            valid_arc_points = []
            for point in arc_points:
                if polygon.contains(Point(point)):
                    valid_arc_points.append(point)
            smoothed_waypoints.extend(valid_arc_points)

    smoothed_waypoints.append(ordered_segments[-1][1])
    return smoothed_waypoints

def heading(smoothed_waypoints):
    pose_trajectory= []
    for index in range(len(smoothed_waypoints)-1):
        current_point =  smoothed_waypoints[index]
        next_point = smoothed_waypoints[index+1]
        x1,y1, spray1  = current_point
        x2,y2, spray2  = next_point
        dx = x2 - x1
        dy = y2 - y1
        yaw = atan2(dy,dx)
        pose_trajectory.append((x1, y1, yaw, spray1))
    last_x, last_y, last_spray =  smoothed_waypoints[-1]
    if pose_trajectory:
        last_yaw =  pose_trajectory[-1][2]
    else:
        last_yaw = 0.0
    pose_trajectory.append((last_x, last_y, last_yaw, last_spray))
    return pose_trajectory







