"""CropFleet: Coverage Planning and Mission Generation for Agricultural Drones.

A computational geometry research project for coverage planning and mission generation
in autonomous agricultural drones. CropFleet generates waypoint-based coverage missions
for irregular field geometries using sweep-line algorithms and geometric path planning.

Key Features:
    - Polygon decomposition for complex field geometries
    - Parallel sweep-line coverage lane generation
    - Boustrophedon traversal ordering
    - Bezier curve path smoothing
    - Mission performance metrics and analysis
    - Interactive field boundary mapping
    - Comprehensive visualization

Modules:
    - coverage: Lane generation and polygon decomposition
    - path: Traversal ordering for coverage segments
    - mission: Waypoint generation and path smoothing
    - metrics: Mission performance analysis
    - environments: Field configuration and loading
    - sketcher: Interactive field boundary mapping
    - visualization: Results visualization and metrics display

Example Usage:
    >>> from shapely.geometry import Polygon
    >>> from coverage_planner.coverage.coverage_pipeline import run_pipe
    >>> from coverage_planner.visualization.visualization import visualize_coverage
    >>> visualize_coverage()  # Interactive visualization of full pipeline

For more information, see: https://github.com/dheerajsankar/CropFleet
"""
