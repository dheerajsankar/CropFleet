# CropFleet

![CropFleet logo](media/logo.png)

**Multi-drone agricultural coverage planning and simulation stack** plan spray-coverage missions over real field polygons, split them across a drone fleet, and fly them with PX4 SITL in Gazebo, with live RViz visualization and a fleet telemetry dashboard.

The flagship demo: **two PX4 x500 drones swarming over a green crop field** whose size and shape exactly match the real field polygon in `research/field.geojson` (~82 m × 89 m, ~0.5 ha), each spraying its share of the field lane by lane, with automatic mission reassignment if a drone fails.

---

## How It Works

```
research/field.geojson (WGS84 lon/lat)
        │  field_loader: project to local ENU meters (origin = first vertex)
        ▼
coverage_planner (Python library)
   generate_lanes ─► generate_traversal ─► generate_mission ─► metrics
   (evaluates vertical vs horizontal lanes, picks the cheaper orientation,
    splits lanes across N drones)
        ▼
mission_manager (ROS2)                    Gazebo world  (crop_field.sdf)
   publishes /droneN/mission                 green field mesh, same origin
        ▼                                          ▲
drone_node × N (ROS2)  ── ENU→NED per vehicle ── PX4 SITL × N (x500)
   offboard state machine:                   /px4_N/fmu/*  via MicroXRCEAgent
   REQUESTING_OFFBOARD → ARMING → TAKING_OFF → MISSION → RETURNING → LANDING
        ▼
visualization (RViz markers)   +   fleet_gui (PyQt5 dashboard)
```

**One frame convention end to end**: the field polygon origin, PX4's home position (`config/sitl_home.env`), and the Gazebo world's spherical coordinates all coincide, so planner coordinates, Gazebo positions, and RViz markers line up 1:1. Missions travel in world ENU meters; each `drone_node` converts to its own vehicle's local NED frame (axis swap + spawn offset + yaw flip) at the last step before PX4.

---

## Repository Structure

```text
CropFleet/
├── coverage_planner/                 # Python coverage planning library
│   ├── enviroments/field_loader.py   # GeoJSON → local ENU meters (pyproj aeqd)
│   ├── coverage/                     # Lane generation + pipeline
│   │   └── decomposition/            # Concave polygon decomposition (research)
│   ├── path/traversal_generator.py   # Boustrophedon lane ordering
│   ├── mission/mission_generator.py  # Waypoints, headings, turn smoothing
│   ├── metrics/mission_metrics.py    # Coverage/transition distance, efficiency
│   ├── visualization/                # Offline matplotlib mission plots
│   └── map_bound.py                  # Click-to-digitize field polygons (desktop)
├── ros2_ws/src/
│   ├── planner/                      # ROS2 planner package (ament_python)
│   │   ├── planner/mission_manager.py    # Plans + publishes missions, reassigns on failure
│   │   ├── planner/drone_node.py         # PX4 offboard state machine per drone
│   │   ├── planner/visualization.py      # RViz marker publisher
│   │   ├── planner/fleet_gui.py          # PyQt5 telemetry dashboard
│   │   ├── launch/swarm_launch.xml       # Full stack launch
│   │   └── rviz/swarm.rviz               # Preconfigured RViz view
│   ├── mission_msg/                  # Mission / MissionWaypoint message definitions
│   └── drone_des/                    # Drone description package (placeholder)
├── simulation/
│   ├── worlds/crop_field.sdf         # Gazebo world: green field + PX4 plugins
│   ├── gazebo/models/crop_field/     # Field mesh (generated from the geojson)
│   └── scripts/generate_field_world.py   # Regenerates the mesh (stdlib only)
├── config/
│   ├── sitl_home.env                 # PX4 home = field origin
│   └── mission_params.yaml           # Optional parameter overrides
├── research/                         # Field polygon + digitization artifacts
├── launch_sitl.sh                    # One-command two-drone SITL demo (Linux)
├── Dockerfile / docker-compose.yml   # ROS2 Humble planner-stack image
└── .devcontainer/                    # VS Code devcontainer (live-editing setup)
```

---

## Quick Start

### Option A  Full Gazebo swarm demo (Linux)

Prerequisites: Ubuntu 22.04, [ROS2 Humble](https://docs.ros.org/en/humble/Installation.html), a built [PX4-Autopilot](https://github.com/PX4/PX4-Autopilot) checkout, gz sim, and [Micro-XRCE-DDS-Agent](https://github.com/eProsima/Micro-XRCE-DDS-Agent).

```bash
# one-time
git clone https://github.com/PX4/PX4-Autopilot.git ~/PX4-Autopilot --recursive
cd ~/PX4-Autopilot && make px4_sitl

git clone <this-repo> ~/CropFleet
cd ~/CropFleet
pip3 install -e .                       # coverage_planner library
cd ros2_ws && colcon build --symlink-install && source install/setup.bash

# every run
cd ~/CropFleet && ./launch_sitl.sh
```

`launch_sitl.sh` links the crop-field world into the PX4 tree, starts Gazebo with two x500 vehicles (`px4 -i 1` / `px4 -i 2`), one MicroXRCEAgent, and the full planner stack (RViz + fleet GUI included). Set `PX4_DIR` if PX4 lives elsewhere.

### Option B  Planner stack only (Docker, any OS)

```bash
docker compose build
docker compose up -d
docker compose exec cropfleet bash
# inside the container:
ros2 launch planner swarm_launch.xml use_rviz:=false use_gui:=false
```

The image contains ROS2 Humble, `px4_msgs`, MicroXRCEAgent, and the built workspace  but not PX4/Gazebo, so drone nodes will wait for a simulator. For GUI windows on Linux hosts run `xhost +local:docker` first and drop the `use_rviz`/`use_gui` flags; on macOS use XQuartz with `DISPLAY=host.docker.internal:0`.

### Option C  Devcontainer (development)

Open the folder in VS Code → **Reopen in Container**. Source is live-mounted and symlink-installed, so Python edits apply without rebuilding.

### Offline mission preview (no ROS needed)

```bash
python3 -m coverage_planner.visualization.visualization
```

Plots both drones' lanes, headings, and per-drone coverage metrics with matplotlib.

---

## ROS2 Interface

### Topics (per drone, `N` = 1, 2, …)

| Topic | Type | Direction | Purpose |
|---|---|---|---|
| `/droneN/mission` | `mission_msg/Mission` | manager → drone | Waypoints (world ENU meters) |
| `/droneN/status` | `std_msgs/String` | drone → all | `SPRAYING`, `TRANSIT`, `RETURNING`, `FAILED`, `COMPLETED` |
| `/droneN/progress` | `std_msgs/Int32` | drone → manager | Current waypoint index |
| `/droneN/pose` | `geometry_msgs/PoseStamped` | drone → viz | World ENU pose for RViz |
| `/droneN/battery` | `std_msgs/Float32` | drone → GUI | Battery percentage |
| `/px4_N/fmu/in/*`, `/px4_N/fmu/out/*` | `px4_msgs/*` | drone ↔ PX4 | Offboard control + telemetry |
| `/visualization_marker` | `visualization_msgs/Marker` | viz → RViz | Field boundary, paths, drone arrows |

### Key `drone_node` parameters

| Parameter | Default | Meaning |
|---|---|---|
| `drone_id` | `drone1` | Topic namespace for fleet topics |
| `px4_ns` | `""` | PX4 uXRCE namespace (`px4_1` for `px4 -i 1`) |
| `target_system` | `1` | PX4 MAV_SYS_ID (= instance + 1) |
| `spawn_east` / `spawn_north` | `0.0` | Vehicle spawn point in the world frame |
| `mission_altitude` | `-5.0` | Flight altitude (NED down, i.e. 5 m AGL) |
| `waypoint_threshold` | `1.0` | Waypoint acceptance radius (m) |
| `simulate_failure` | `false` | Fail mid-mission to demo reassignment |
| `vehicle_status_topic` etc. | `fmu/out/..._vN` | PX4 versioned topic names (see below) |

### Failure recovery

Set `simulate_failure:=true` on one drone (see `swarm_launch.xml`): it stops mid-mission, publishes `FAILED`, and the mission manager appends its remaining waypoints to an active drone's mission  the survivor finishes both halves of the field.

---

## Troubleshooting

- **Drones sit on the ground, node warns "no VehicleStatus received"**  PX4 message versioning suffixes topics (`/fmu/out/vehicle_status_v4`, `_v1`, …) and the suffix depends on your PX4 commit. Check `ros2 topic list` and set the `vehicle_status_topic` / `local_position_topic` / `battery_status_topic` parameters in `swarm_launch.xml` to match. Also confirm MicroXRCEAgent is running on udp 8888.
- **`ModuleNotFoundError: ament_package` when building in Docker**  your shell isn't sourced (`docker exec` bypasses the entrypoint). `source /opt/ros/humble/setup.bash`, or rebuild the image (sourcing is baked into `.bashrc`).
- **Changed the field?** Replace `research/field.geojson`, then regenerate the Gazebo mesh: `python3 simulation/scripts/generate_field_world.py`. Update `config/sitl_home.env` to the new first vertex.

---

## Tech Stack

ROS2 Humble · PX4 (SITL, offboard mode via uXRCE-DDS) · Gazebo (gz sim) · Python 3 · Shapely / pyproj (geometry & projection) · PyQt5 (fleet GUI) · NumPy / Matplotlib (analysis)

---

## License

MIT © 2026 [Dheeraj Sankar](mailto:dheerajsankar2@gmail.com)  see [LICENSE](LICENSE).
