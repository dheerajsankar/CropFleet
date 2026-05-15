"""Interactive visualization of coverage planning results.

This module provides visualization of the entire coverage planning pipeline,
including polygon decomposition, coverage lanes, split lines, and the final
mission trajectory with performance metrics.
"""

from matplotlib import pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.colors import hsv_to_rgb
import numpy as np
from coverage_planner.environments.field_loader import field_loader
from coverage_planner.coverage.generate_lanes import generate_lanes
from coverage_planner.metrics.mission_metrics import calculate_all_metrics
from coverage_planner.mission.mission_generator import generate_mission
from coverage_planner.path.traversal_generator import generate_traversal
from coverage_planner.coverage.decomposition.concavity_detector import (
    detect_concave_vertices
)
from coverage_planner.coverage.decomposition.split_generator import (
    split_generator,
    split_validation
)
from coverage_planner.coverage.decomposition.recursive_decomposer import (
    recursive_decompose
)
from coverage_planner.coverage.coverage_pipeline import run_pipe


def visualize_coverage():
    """Execute and visualize the complete coverage planning pipeline.

    Loads a field polygon, runs the full coverage planning pipeline
    (decomposition, lane generation, trajectory planning), and displays
    the results with:
    - Field boundary (blue line)
    - Decomposed cells (colored regions)
    - Concave vertices (green dots)
    - Split lines (orange for horizontal, purple for vertical)
    - Mission trajectory (red line)
    - Mission metrics (distance, efficiency)

    The visualization combines all stages of the coverage planning system
    in a single comprehensive figure.
    """
    # Load field configuration from file
    field = field_loader()
    polygon = field["polygon"]
    
    # Detect concave vertices for decomposition
    concave_points = detect_concave_vertices(polygon)
    
    # Generate split lines from concave vertices
    hor_split_lines, ver_split_lines = split_generator(polygon, concave_points)
    
    # Validate that split lines actually partition the polygon
    valid_hor_splits, valid_ver_splits = split_validation(
        polygon, hor_split_lines, ver_split_lines
    )
    
    # Execute complete coverage planning pipeline
    coverage_segments = run_pipe(field["polygon"])
    
    # Generate traversal order (boustrophedon pattern)
    traversal_path = generate_traversal(coverage_segments)
    
    # Convert to waypoint path
    smoothed_waypoints = generate_mission(traversal_path)
    
    # Decompose polygon for visualization
    decomposed_polygons = recursive_decompose(field["polygon"])
    
    # Calculate performance metrics
    metrics = calculate_all_metrics(smoothed_waypoints, traversal_path)

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(12, 10))

    # Plot field boundary (blue line)
    x, y = field["polygon"].exterior.xy
    ax.plot(x, y, color='blue', linewidth=2, label='Field Boundary')

    # Plot decomposed cells with distinct colors for visual distinction
    num_cells = len(decomposed_polygons)
    for idx, poly in enumerate(decomposed_polygons):
        # Generate distinct color using HSV color space
        # This provides perceptually uniform color spacing
        hue = idx / num_cells if num_cells > 0 else 0
        color = hsv_to_rgb([hue, 0.7, 0.9])
        
        # Create filled polygon patch
        coords = list(poly.exterior.coords)
        patch = Polygon(
            coords, facecolor=color, edgecolor='black',
            linewidth=1, alpha=0.7
        )
        ax.add_patch(patch)

    # Plot concave vertices (green dots) - decomposition points
    if concave_points:
        concave_x = [point[0] for point in concave_points]
        concave_y = [point[1] for point in concave_points]
        ax.scatter(
            concave_x, concave_y, color='green', s=50,
            label='Concave Vertices', zorder=5
        )

    # Plot split lines: orange for horizontal, purple for vertical
    for line in valid_hor_splits:
        x, y = line.xy
        ax.plot(x, y, color='orange', linewidth=2)
    
    for line in valid_ver_splits:
        x, y = line.xy
        ax.plot(x, y, color='purple', linewidth=2)

    # Plot the mission trajectory (red line)
    mission_x = [point[0] for point in smoothed_waypoints]
    mission_y = [point[1] for point in smoothed_waypoints]
    ax.plot(mission_x, mission_y, color='red', linewidth=2, label='Mission Trajectory')

    # Display mission metrics in bottom-right corner
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
    plt.show()



if __name__ == "__main__":
    visualize_coverage()