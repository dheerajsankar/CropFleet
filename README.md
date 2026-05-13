# CropFleet

CropFleet is an autonomous agricultural drone planning project focused on field coverage generation, traversal planning, mission trajectory synthesis, and future research toward decentralized multi-UAV agricultural operations.

The project explores how autonomous drones can efficiently cover, monitor, and navigate irregular agricultural environments such as rice paddies, plantations, and fragmented farmlands using computational geometry and motion-planning techniques.

---

# Overview

CropFleet currently focuses on:

- Polygon-based field representation
- Sweep-based coverage lane generation
- Boustrophedon-style traversal generation
- Mission waypoint generation
- Coverage mission evaluation metrics
- Heading-aware transition smoothing
- Coverage visualization and analysis
- Simulation-oriented planning workflows

The project is being developed as part of a broader long-term agricultural robotics ecosystem intended to support autonomous field operations, mission coordination, and drone deployment infrastructure.

---

# Current Planning Pipeline

The current planning workflow is structured as:

```text
Field Polygon
    ↓
Coverage Lane Generation
    ↓
Traversal Ordering
    ↓
Mission Generation
    ↓
Transition Smoothing
    ↓
Mission Metrics
    ↓
Visualization
```

---

# Current Features

## Field Boundary Processing

CropFleet supports polygon-based field modeling for irregular agricultural environments.

Current capabilities include:

- Polygon field representation
- Boundary extraction and loading
- Polygon clipping
- Structured geometric processing

---

## Coverage Lane Generation

The current implementation uses sweep-based coverage generation across polygonal fields.

Current capabilities:

- Parallel lane generation
- Polygon-clipped sweep lines
- Adjustable lane spacing
- Zig-zag boustrophedon traversal generation
- Coverage trajectory visualization

---

## Mission Generation

CropFleet converts ordered coverage segments into continuous waypoint trajectories for field coverage missions.

Current capabilities:

- Continuous waypoint generation
- Ordered traversal stitching
- Transition generation between coverage lanes
- Heading-aware transition smoothing
- Bezier-based transition interpolation
- Continuous mission visualization

---

## Coverage Metrics

The planner currently evaluates generated missions using several geometric metrics.

Implemented metrics include:

- Total mission distance
- Coverage distance
- Transition distance
- Coverage efficiency

These metrics are used to evaluate mission quality and future optimization strategies.

---

# Repository Structure

```text
CropFleet/
├── coverage_planner/
│   ├── coverage/
│   │   ├── generate_lanes.py
│   │   └── __init__.py
│   │
│   ├── environments/
│   │   ├── field_loader.py
│   │   └── __init__.py
│   │
│   ├── mission/
│   │   ├── mission_generator.py
│   │   └── __init__.py
│   │
│   ├── metrics/
│   │   ├── mission_metrics.py
│   │   └── __init__.py
│   │
│   ├── path/
│   │   ├── traversal_generator.py
│   │   └── __init__.py
│   │
│   └── visualization/
│       ├── visualization.py
│       └── __init__.py
│
├── docs/
│   └── roadmap.md
│
├── media/
│   ├── field_reference.png
│   ├── lane_generation_v2.png
│   ├── lane_generation_v3.png
│   ├── mission_trajectory.png
│   └── smoothed_mission.png
│
├── research/
│   └── polygon_points.txt
│
└── README.md
```

---

# Example Outputs

The repository currently includes generated visualizations for:

- Coverage lane generation
- Traversal paths
- Mission trajectories
- Smoothed lane transitions
- Lane-spacing comparisons
- Coverage metric evaluation

---

# Current Research Directions

Current active development areas include:

- Coverage decomposition
- Concave polygon handling
- Boundary-aware transition generation
- Curvature-aware maneuver planning
- Coverage efficiency optimization
- Obstacle-aware traversal generation
- Multi-region field decomposition

---

# Future Goals

Long-term project goals include:

- Boustrophedon cellular decomposition
- Multi-drone field partitioning
- Decentralized mission planning
- Battery-aware coverage optimization
- Dubins and curvature-constrained trajectory generation
- ROS2 integration
- PX4 simulation workflows
- Autonomous docking and deployment infrastructure
- Precision agriculture mission planning

---

# Technology Stack

Current and planned technologies include:

- Python
- C++
- NumPy
- Matplotlib
- Shapely
- ROS2
- PX4
- Gazebo
- OpenCV

---

# Project Status

CropFleet is currently in active early-stage research and development.

This repository serves as a public engineering and research showcase documenting the evolution of:

- Coverage-planning algorithms
- Mission trajectory generation
- Geometric field decomposition
- Motion-planning concepts
- Autonomous agricultural robotics workflows

The project is currently focused on foundational planning architecture before future expansion toward multi-agent autonomous agricultural systems.