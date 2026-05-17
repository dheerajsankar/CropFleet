# CropFleet

Autonomous multi-drone coverage planning framework for precision agriculture and large-scale field operations.

CropFleet focuses on coverage path planning, mission generation, and swarm-oriented agricultural spraying workflows for autonomous UAV systems operating in irregular farm geometries.

The system generates efficient sweep-based coverage trajectories inside arbitrary polygonal field boundaries using computational geometry, adaptive lane generation, and ROS2-integrated mission publishing.

---

# Core Features

- Polygon-based agricultural field representation
- Adaptive horizontal/vertical sweep selection
- Boundary-aware lane clipping
- Boustrophedon-style coverage traversal
- Smooth transition generation between spray lanes
- Mission waypoint synthesis with heading generation
- Coverage efficiency metrics and transition analysis
- ROS2 Path publishing for robotics integration
- RViz visualization pipeline
- Swarm-oriented architecture for future multi-UAV coordination

---

# Current System Pipeline

```text
Field Boundary
      ↓
Coverage Direction Selection
      ↓
Lane Generation
      ↓
Boundary Clipping
      ↓
Traversal Ordering
      ↓
Transition Smoothing
      ↓
Waypoint + Heading Generation
      ↓
ROS2 Path Publishing
      ↓
RViz Visualization
```

---

# Coverage Planning

CropFleet generates agricultural spraying trajectories inside irregular polygonal farm boundaries.

The planner:
- clips sweep lanes to field boundaries
- minimizes unnecessary transition movement
- alternates traversal direction for efficient coverage
- supports adaptive sweep orientation selection
- generates smooth mission trajectories for autonomous drones

Coverage trajectories are designed for:
- bio-pesticide spraying
- precision agriculture
- autonomous field scanning
- future multi-UAV swarm coverage

---

# ROS2 Integration

CropFleet now includes ROS2 integration for robotics workflows.

Current integration includes:
- `nav_msgs/Path` publishing
- `PoseStamped` trajectory generation
- heading/yaw synthesis
- quaternion orientation conversion
- RViz mission visualization

This enables transition from offline geometric planning toward:
- autonomous drone execution
- PX4 integration
- swarm coordination
- real-world deployment pipelines

---

# Visualization

## Coverage Mission

- Blue: field boundary
- Red: generated coverage trajectory
- Green arrows: heading direction

## RViz Integration

CropFleet trajectories can be streamed directly into RViz through ROS2 topics for live mission inspection and debugging.

---

# Current Capabilities

## Implemented

- Polygon field loading
- Adaptive sweep generation
- Boundary-aware clipping
- Lane traversal ordering
- Mission waypoint generation
- Transition smoothing
- Heading/yaw generation
- ROS2 Path publishing
- RViz visualization
- Coverage metrics

---

# In Progress

- Multi-drone field decomposition
- Swarm task allocation
- Obstacle-aware planning
- Constraint-aware smoothing
- Curvature-limited trajectory generation
- PX4 offboard integration
- Real-time replanning
- Coverage continuity optimization

---

# Planned Architecture

```text
                CropFleet
                     │
     ┌───────────────┼───────────────┐
     │                               │
Coverage Planning              Swarm Coordination
     │                               │
Lane Generation              Multi-UAV Allocation
Traversal Logic              Task Distribution
Mission Smoothing            Cooperative Coverage
     │                               │
     └───────────────┬───────────────┘
                     │
               ROS2 Middleware
                     │
          PX4 / Simulation / UAVs
```

---

# Technology Stack

## Current

- Python
- ROS2 Humble
- Shapely
- NumPy
- Matplotlib
- OpenCV

## Planned

- PX4
- Gazebo
- C++
- MAVROS / microRTPS
- Multi-agent coordination frameworks

---

# Example ROS2 Usage

```bash
ros2 run planner planner
```

Then visualize:

```bash
rviz2
```

Topic:

```text
/coverage_path
```

---

# Future Vision

CropFleet is evolving toward a full autonomous agricultural drone framework capable of:

- cooperative swarm spraying
- autonomous field coverage
- adaptive multi-UAV mission allocation
- large-scale agricultural automation
- decentralized coverage execution

---

# Repository Structure

```text
coverage_planner/
├── coverage/
├── mission/
├── path/
├── metrics/
├── visualization/
├── environments/
└── ros2_ws/
```

---

# Status

Active development.

Current focus:
- swarm-ready mission planning
- ROS2 ecosystem integration
- autonomous agricultural coverage workflows

---

# Author

Dheeraj Sankar Narayana Mangalath

Robotics Engineer | Autonomous Systems | Drone Swarms | Agricultural Robotics
