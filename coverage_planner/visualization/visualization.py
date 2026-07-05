import numpy as np
from matplotlib import pyplot as plt
from coverage_planner.enviroments.field_loader import field_loader
from coverage_planner.metrics.mission_metrics import calculate_all_metrics
from coverage_planner.mission.mission_generator import generate_mission, heading
from coverage_planner.coverage.coverage_pipeline import run_pipe


def visualize_coverage():
    field = field_loader()
    polygon = field["polygon"]
    all_traversals = run_pipe(polygon, 2)
    colours = ['red', 'blue', 'green', 'orange']
    fig, ax = plt.subplots(figsize=(12, 10))

    # Plot polygon boundary once
    x, y = polygon.exterior.xy
    ax.plot(
        x,
        y,
        color='blue',
        linewidth=2,
        label='Field Boundary'
    )

    for i, traversal in enumerate(all_traversals):
        mission_waypoints = generate_mission(traversal)
        pose_trajectory = heading(mission_waypoints)
        metrics = calculate_all_metrics(mission_waypoints, traversal)

        # Plot mission trajectory per drone
        mission_x = [point[0] for point in mission_waypoints]
        mission_y = [point[1] for point in mission_waypoints]
        ax.plot(
            mission_x,
            mission_y,
            color=colours[i],
            linewidth=2,
            label=f'Drone {i+1} Trajectory'
        )

        # Plot heading arrows
        for x, y, yaw, spray in pose_trajectory:
            dx = 5 * np.cos(yaw)
            dy = 5 * np.sin(yaw)
            ax.arrow(
                x,
                y,
                dx,
                dy,
                head_width=1,
                head_length=1,
                fc=colours[i],
                ec=colours[i]
            )

        # Plot metrics per drone
        fig.text(
            0.02 + i * 0.25,
            0.02,
            (
                f"Drone {i+1}\n"
                f"Total Distance: {metrics['total_distance']:.2f}m\n"
                f"Coverage Distance: {metrics['coverage_distance']:.2f}m\n"
                f"Transition Distance: {metrics['transition_distance']:.2f}m\n"
                f"Coverage Efficiency: {metrics['coverage_efficiency']:.2f}%"
            ),
            fontsize=9,
            bbox=dict(facecolor='white', alpha=0.8)
        )

    ax.set_title('Field Coverage Visualization')
    ax.set_xlabel('East (meters)')
    ax.set_ylabel('North (meters)')
    ax.legend()
    ax.grid()
    ax.axis('equal')
    plt.show()


if __name__ == "__main__":
    visualize_coverage()