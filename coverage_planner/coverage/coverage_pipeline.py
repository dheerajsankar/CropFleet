from coverage_planner.coverage.generate_lanes import generate_lanes
from coverage_planner.path.traversal_generator import generate_traversal
from coverage_planner.mission.mission_generator import generate_mission
from coverage_planner.metrics.mission_metrics import calculate_all_metrics

def evaluate_direction(polygon,direction,num_drones,lane_spacing=5):
    segments = generate_lanes(polygon,lane_spacing=lane_spacing,direction=direction)
    if direction == "vertical":
        segments = sorted(segments,key=lambda seg: seg.centroid.x)
    else:
        segments = sorted(segments,key=lambda seg: seg.centroid.y)
    chunk_size = len(segments) // num_drones
    all_traversals = []
    all_metrics = []
    all_missions = []
    for i in range(num_drones):
        start_index = i * chunk_size
        if i == num_drones - 1:
            end_index = len(segments)
        else:
            end_index = (i + 1) * chunk_size
        drone_segments = segments[start_index:end_index]
        start_reverse = (i % 2 == 1)
        traversal = generate_traversal(drone_segments,start_reverse=start_reverse)
        mission = generate_mission(traversal)
        metrics = calculate_all_metrics(mission,traversal)
        all_traversals.append(traversal)
        all_missions.append(mission)
        all_metrics.append(metrics)
    total_transition_distance = sum(metric["transition_distance"]
        for metric in all_metrics)

    return (all_traversals,all_missions,all_metrics,total_transition_distance)

def run_pipe(polygon,num_drones,lane_spacing=5):

    (vertical_traversals,vertical_missions,vertical_metrics,vertical_transition) = evaluate_direction(polygon,"vertical",num_drones,lane_spacing)
    (horizontal_traversals,horizontal_missions,horizontal_metrics,horizontal_transition) = evaluate_direction(polygon,"horizontal",num_drones,lane_spacing)

    if vertical_transition < horizontal_transition:
        selected_orientation = "Vertical"
        selected_traversals = vertical_traversals
        selected_missions = vertical_missions
        selected_metrics = vertical_metrics
    else:
        selected_orientation = "Horizontal"
        selected_traversals = horizontal_traversals
        selected_missions = horizontal_missions
        selected_metrics = horizontal_metrics

    # print("\n========================================")
    # print("         SWARM MISSION SUMMARY")
    # print("========================================")
    # print(f"\nSelected Orientation : "f"{selected_orientation}")
    # total_swarm_distance = 0.0
    # drone_distances = []
    # for i in range(num_drones):
    #     metrics = selected_metrics[i]
    #     mission = selected_missions[i]
    #     traversal = selected_traversals[i]
    #     total_distance = (metrics["coverage_distance"]+metrics["transition_distance"])
    #     drone_distances.append(total_distance)
    #     total_swarm_distance += (total_distance)
    #     print(f"\n------------- "f"Drone {i+1} -------------")
    #     print(f"Lanes                : "f"{len(traversal)}")
    #     print(f"Waypoints            : "f"{len(mission)}")
    #     print(f"Coverage Distance    : "f"{metrics['coverage_distance']:.2f}")
    #     print(f"Transition Distance  : "f"{metrics['transition_distance']:.2f}")
    #     print(f"Total Distance       : "f"{total_distance:.2f}")
    # workload_imbalance = (max(drone_distances)-min(drone_distances))
    # print("\n------------- ""Swarm Summary -------------")
    # print(f"Combined Distance    : "f"{total_swarm_distance:.2f}")
    # print(f"Workload Imbalance   : "f"{workload_imbalance:.2f}")
    # print("========================================\n")

    return selected_traversals