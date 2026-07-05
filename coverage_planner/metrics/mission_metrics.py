
def calculate_all_metrics(mission_waypoints, ordered_segments):

    total_distance = 0.0

    # Calculate total distance traveled
    for i in range(1, len(mission_waypoints)):
        x1, y1, _ = mission_waypoints[i - 1]
        x2, y2, _ = mission_waypoints[i]
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        total_distance += distance
    coverage_distance=0.0
    for start, end in ordered_segments:
        x1, y1 = start
        x2, y2 = end
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        coverage_distance += distance

    transition_distance = total_distance - coverage_distance

    if total_distance > 0:
        coverage_efficiency = (coverage_distance / total_distance) * 100
    else:        
        coverage_efficiency = 0.0  

    return {
        "total_distance": total_distance,
        "coverage_distance": coverage_distance,
        "transition_distance": transition_distance,
        "coverage_efficiency": coverage_efficiency
    }




    
