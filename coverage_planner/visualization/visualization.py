"""Visualization module for field coverage planning.

This module generates visual representations of the coverage plan,
including field boundaries, mission trajectory, and performance metrics.
"""

from matplotlib import pyplot as plt
from coverage_planner.environments.field_loader import field_loader
from coverage_planner.coverage.generate_lanes import generate_lanes
from coverage_planner.metrics.mission_metrics import calculate_all_metrics
from coverage_planner.mission.mission_generator import generate_smoothed_mission
from coverage_planner.path.traversal_generator import generate_traversal


def visualize_coverage():
    """Generate and display a visualization of the field coverage plan.

    This function orchestrates the complete coverage planning workflow:
    1. Load field configuration
    2. Generate coverage lanes
    3. Create traversal path
    4. Generate smoothed mission waypoints
    5. Calculate mission metrics
    6. Visualize results with overlay of metrics

    The visualization includes:
    - Field boundary (blue line)
    - Mission trajectory (red line)
    - Performance metrics (distance, efficiency, etc.)
    """
    # Load field configuration
    field = field_loader()

    # Generate coverage lanes for the field
    coverage_segments = generate_lanes(field)

    # Create the traversal path connecting all coverage segments
    traversal_path = generate_traversal(coverage_segments)

    # Generate smoothed waypoints for the mission path
    smoothed_waypoints = generate_smoothed_mission(traversal_path)

    # Calculate mission performance metrics
    metrics = calculate_all_metrics(smoothed_waypoints, ordered_segments=traversal_path)

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(12, 10))

    # Plot the field boundary polygon
    x, y = field["polygon"].exterior.xy
    ax.plot(x, y, color='blue', linewidth=2, label='Field Boundary')

    # Plot the continuous mission trajectory
    mission_x = [point[0] for point in smoothed_waypoints]
    mission_y = [point[1] for point in smoothed_waypoints]
    ax.plot(mission_x, mission_y, color='red', linewidth=2, label='Mission Trajectory')

    # Display mission metrics on the plot
    metrics_text = (
        f"Total Distance: {metrics['total_distance']:.2f}\n"
        f"Coverage Distance: {metrics['coverage_distance']:.2f}\n"
        f"Transition Distance: {metrics['transition_distance']:.2f}\n"
        f"Coverage Efficiency: {metrics['coverage_efficiency']:.2f}%"
    )
    fig.text(
        0.78,
        0.02,
        metrics_text,
        fontsize=10,
        bbox=dict(facecolor='white', alpha=0.8)
    )

    # Configure plot appearance
    ax.set_title('Field Coverage Visualization', fontsize=14, fontweight='bold')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.axis('equal')

    # Display the plot
    plt.show()


if __name__ == "__main__":
    visualize_coverage()