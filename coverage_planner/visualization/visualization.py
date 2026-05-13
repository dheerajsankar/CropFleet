from matplotlib import pyplot as plt
from coverage_planner.enviroments.field_loader import field_loader
from coverage_planner.coverage.generate_lanes import generate_lanes
from coverage_planner.mission.mission_generator import generate_mission
from coverage_planner.path.traversal_generator import generate_traversal


def visualize_coverage():
    field = field_loader()
    coverage_segments = generate_lanes(field)
    traversal_path = generate_traversal(coverage_segments)
    mission_waypoints = generate_mission(traversal_path)

    plt.figure(figsize=(10, 10))

    # Plot polygon boundary
    x, y = field["polygon"].exterior.xy
    plt.plot(x, y, color='blue', linewidth=2, label='Field Boundary')

    # continous mission trajectory
    mission_x = [point[0] for point in mission_waypoints]
    mission_y = [point[1] for point in mission_waypoints]
    plt.plot(mission_x, mission_y, color='red', linewidth=2, label='Mission Trajectory')

    plt.title('Field Coverage Visualization')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()
    plt.grid()
    plt.axis('equal')
    plt.show()

if __name__ == "__main__":
    visualize_coverage()