# CropFleet

CropFleet is an early-stage autonomous agricultural drone coordination project focused on field coverage planning, traversal generation, and future decentralized multi-UAV operations for agricultural environments.

The project explores how autonomous drones can efficiently map, cover, monitor, and eventually coordinate operations across irregular agricultural fields such as rice paddies and plantation environments.

---

# Overview

Current development focuses on:

- Polygon-based field boundary handling
- Coverage lane generation
- Traversal path generation
- Coverage visualization
- ROS2-oriented system architecture
- Simulation-oriented development workflow

CropFleet is being developed as part of a broader autonomous agricultural ecosystem that will later integrate with DroneHouse — a drone maintenance, deployment, and charging infrastructure system.

---

# Current Development Progress

## Field Boundary Processing

CropFleet currently supports polygon-based field boundary handling for irregular agricultural environments.

Current workflow:

1. Extract or define field boundaries
2. Convert boundaries into polygon representations
3. Generate structured coverage lanes
4. Generate traversal paths for field coverage
5. Visualize coverage outputs

---

# Coverage Lane Generation

The current implementation focuses on sweep-based coverage generation within irregular polygon boundaries.

Current capabilities:

- Polygon clipping
- Structured lane generation
- Coverage visualization
- Traversal direction generation
- Iterative lane refinement

Future goals include:

- Boustrophedon decomposition
- Multi-drone coverage partitioning
- Turn-cost minimization
- Battery-aware planning
- Obstacle-aware traversal
- Adaptive field decomposition

# Mission Generation

CropFleet currently generates continuous field-coverage missions by converting ordered coverage segments into connected waypoint trajectories.

The current mission pipeline supports:

- Continuous waypoint generation
- Zig-zag boustrophedon traversal
- Polygon-clipped coverage lanes
- Transition path generation between lanes
- Mission trajectory visualization

---

# Repository Structure

```text
CropFleet/
├── README.md
├── coverage_planner
│   ├── coverage
│   │   ├── generate_lanes.py
│   │   └── __init__.py
│   ├── environments
│   │   ├── field_loader.py
│   │   └── __init__.py
│   ├── mission
│   │   ├── __init__.py
│   │   └── mission_generator.py
│   ├── path
│   │   ├── __init__.py
│   │   └── traversal_generator.py
│   └── visualization
│       ├── __init__.py
│       └── visualization.py
├── docs
│   └── roadmap.md
├── media
│   ├── field_reference.png
│   ├── lane_generation_v2.png
│   ├── lane_generation_v3.png
│   └── mission_trajectory.png
├── README.md
└── research
    └── polygon_points.txt

```

---

# Project Goals

The long-term objective of CropFleet is to develop a modular agricultural drone ecosystem capable of:

- Autonomous field coverage
- Multi-drone coordination
- Decentralized mission planning
- Agricultural monitoring
- Precision agriculture workflows
- Autonomous deployment and docking
- Integration with charging and maintenance infrastructure

---

# Technology Stack

Current and planned technologies include:

- Python
- C++
- ROS2
- PX4
- Gazebo
- OpenCV
- NumPy
- Matplotlib

---

# Project Status

CropFleet is currently in active early-stage development.

This repository serves as a public engineering and research showcase documenting the evolution of the system architecture, coverage-planning pipeline, and future autonomous agricultural drone coordination framework.
