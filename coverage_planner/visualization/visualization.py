import numpy as np
from matplotlib import pyplot as plt
from coverage_planner.enviroments.field_loader import field_loader
from coverage_planner.metrics.mission_metrics import calculate_all_metrics
from coverage_planner.mission.mission_generator import generate_smoothed_mission, heading
from coverage_planner.path.traversal_generator import generate_traversal
from coverage_planner.coverage.coverage_pipeline import run_pipe


def visualize_coverage():
    field = field_loader()
    polygon = field["polygon"]
    coverage_segments = run_pipe(polygon)
    traversal_path = generate_traversal(coverage_segments)
    mission_waypoints = generate_smoothed_mission(traversal_path, polygon)
    pose_trajectory = heading(mission_waypoints)
    metrics = calculate_all_metrics(mission_waypoints,traversal_path)
    fig, ax = plt.subplots(figsize=(12, 10))
    # Plot polygon boundary
    x, y = polygon.exterior.xy
    ax.plot(
        x,
        y,
        color='blue',
        linewidth=2,
        label='Field Boundary'
    )
    # Plot mission trajectory
    mission_x = [point[0] for point in mission_waypoints]
    mission_y = [point[1] for point in mission_waypoints]
    ax.plot(
        mission_x,
        mission_y,
        color='red',
        linewidth=2,
        label='Mission Trajectory'
    )
    #Plot heading
    for x, y, yaw in pose_trajectory:

        dx = 50 * np.cos(yaw)
        dy = 50 * np.sin(yaw)

        ax.arrow(
            x,
            y,
            dx,
            dy,
            head_width=10,
            head_length=10,
            fc='green',
            ec='green'
        )
    # Plot metrics
    fig.text(
        0.78,
        0.02,
        (
            f"Total Distance: {metrics['total_distance']:.2f}\n"
            f"Coverage Distance: {metrics['coverage_distance']:.2f}\n"
            f"Transition Distance: {metrics['transition_distance']:.2f}\n"
            f"Coverage Efficiency: {metrics['coverage_efficiency']:.2f}%"
        ),
        fontsize=10,
        bbox=dict(facecolor='white', alpha=0.8)
    )

    ax.set_title('Field Coverage Visualization')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.legend()
    ax.grid()
    ax.axis('equal')
    plt.show()


if __name__ == "__main__":
    visualize_coverage()