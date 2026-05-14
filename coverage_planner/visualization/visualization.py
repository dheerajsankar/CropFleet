"""Module for visualizing field coverage planning results.

This module provides visualization of the complete coverage planning pipeline,
including field boundary, concave vertices, decomposition lines, coverage lanes,
traversal path, and performance metrics.
"""

from matplotlib import pyplot as plt
from coverage_planner.environments.field_loader import field_loader
from coverage_planner.coverage.generate_lanes import generate_lanes
from coverage_planner.metrics.mission_metrics import calculate_all_metrics
from coverage_planner.mission.mission_generator import generate_smoothed_mission
from coverage_planner.path.traversal_generator import generate_traversal
from coverage_planner.coverage.decomposition.concavity_detector import detect_concave_vertices
from coverage_planner.coverage.decomposition.split_generator import split_generator


def visualize_coverage():
    """Visualize the complete field coverage planning solution.

    Orchestrates the entire coverage planning pipeline and displays results
    in an interactive matplotlib figure:
    - Field boundary (blue)
    - Concave vertices detected for decomposition (green)
    - Horizontal and vertical split lines (orange and purple)
    - Smoothed mission trajectory (red)
    - Mission metrics (distance, efficiency) displayed on plot

    The function loads a field, performs decomposition, generates coverage
    lanes, creates an efficient traversal path, smooths the waypoints, and
    calculates performance metrics.

    Returns:
        None: Displays the visualization using matplotlib's interactive mode.
    """
    # Step 1: Load field geometry
    field = field_loader()
    polygon = field["polygon"]
    
    # Step 2: Detect concave vertices for polygon decomposition
    concave_points = detect_concave_vertices(polygon)
    
    # Step 3: Generate decomposition lines at concave points
    hor_split_lines, ver_split_lines = split_generator(polygon, concave_points)
    
    # Step 4: Generate coverage lanes
    coverage_segments = generate_lanes(field)
    
    # Step 5: Create traversal path with alternating directions
    traversal_path = generate_traversal(coverage_segments)
    
    # Step 6: Smooth the traversal path into continuous waypoints
    smoothed_waypoints = generate_smoothed_mission(traversal_path)
    
    # Step 7: Calculate mission performance metrics
    metrics = calculate_all_metrics(smoothed_waypoints, ordered_segments=traversal_path)

    # Create figure for visualization
    fig, ax = plt.subplots(figsize=(12, 10))

    # Plot field boundary
    x, y = field["polygon"].exterior.xy
    ax.plot(x, y, color='blue', linewidth=2, label='Field Boundary')
    
    # Plot concave vertices (if any)
    if concave_points:
        concave_x = [point[0] for point in concave_points]
        concave_y = [point[1] for point in concave_points]
        ax.scatter(concave_x, concave_y, color='green', s=50, label='Concave Vertices', zorder=5)

    # Plot horizontal and vertical decomposition split lines
    for line in hor_split_lines:
        x, y = line.xy
        ax.plot(x, y, color='orange', linewidth=2)

    for line in ver_split_lines:
        x, y = line.xy
        ax.plot(x, y, color='purple', linewidth=2)

    # Plot the continuous mission trajectory
    mission_x = [point[0] for point in smoothed_waypoints]
    mission_y = [point[1] for point in smoothed_waypoints]
    ax.plot(mission_x, mission_y, color='red', linewidth=2, label='Mission Trajectory')

    # Display mission metrics on the plot 
    # Format and display mission metrics box
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

    # Configure plot appearance
    ax.set_title('Field Coverage Visualization')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.legend()
    ax.grid()
    ax.axis('equal')
    
    # Display the visualization
    plt.show()

if __name__ == "__main__":
    visualize_coverage()