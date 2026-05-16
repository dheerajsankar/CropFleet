from coverage_planner.coverage.generate_lanes import generate_lanes
from coverage_planner.path.traversal_generator import generate_traversal
from coverage_planner.mission.mission_generator import generate_mission
from coverage_planner.metrics.mission_metrics import calculate_all_metrics


def run_pipe(polygon):

    # Vertical solution
    vertical_segments = generate_lanes(polygon,lane_spacing=40,direction="vertical")
    vertical_traversal = generate_traversal(vertical_segments)
    vertical_mission = generate_mission(vertical_traversal)
    vertical_metrics = calculate_all_metrics(vertical_mission,vertical_traversal)

    # Horizontal solution
    horizontal_segments = generate_lanes(polygon,lane_spacing=40,direction="horizontal")
    horizontal_traversal = generate_traversal(horizontal_segments)
    horizontal_mission = generate_mission(horizontal_traversal)
    horizontal_metrics = calculate_all_metrics(horizontal_mission,horizontal_traversal)

    # Compare transition distance
    if (vertical_metrics["transition_distance"]<horizontal_metrics["transition_distance"]):
        return vertical_traversal
    else:
        return horizontal_traversal