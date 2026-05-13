

def generate_mission(ordered_segments):
    mission_waypoints = []

    for start, end in ordered_segments:

        if not mission_waypoints or mission_waypoints[-1] != start:
            mission_waypoints.append(start)
        
        if mission_waypoints[-1] != end:
            mission_waypoints.append(end)
    return mission_waypoints
    


    
    
