#!/bin/bash
# Launch a two-drone PX4 SITL swarm over the CropFleet crop-field world.
#
#   Gazebo world : simulation/worlds/crop_field.sdf (field mesh matches
#                  research/field.geojson, origin = config/sitl_home.env)
#   Vehicle 1    : px4 -i 1 -> /px4_1/fmu/...  MAV_SYS_ID 2  spawn (0, 0)
#   Vehicle 2    : px4 -i 2 -> /px4_2/fmu/...  MAV_SYS_ID 3  spawn (4, 0)
#
# Requires a built PX4-Autopilot checkout (set PX4_DIR to override the path).
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/config"
WORKSPACE_DIR="$SCRIPT_DIR/ros2_ws"
PX4_DIR="${PX4_DIR:-$HOME/PX4-Autopilot}"
LOG_DIR="$SCRIPT_DIR/.sitl_logs"
mkdir -p "$LOG_DIR"

# Always stop any previous run first. A leftover `gz sim` server in
# particular will silently reattach instead of loading a fresh world,
# which causes hard-to-diagnose breakage (missing sensor topics, stale
# vehicle poses) rather than an obvious error.
"$SCRIPT_DIR/stop_sitl.sh" >/dev/null

if [ ! -d "$PX4_DIR" ]; then
    echo "ERROR: PX4-Autopilot not found at $PX4_DIR (set PX4_DIR to override)" >&2
    exit 1
fi

PX4_BIN="$PX4_DIR/build/px4_sitl_default/bin/px4"
if [ ! -x "$PX4_BIN" ]; then
    echo "PX4 SITL binary not built yet — building (make px4_sitl)..."
    (cd "$PX4_DIR" && make px4_sitl)
fi

# Make the crop-field world and model visible to PX4/gz. PX4 resolves
# PX4_GZ_WORLD against its own worlds folder, so link the world in; the mesh
# model resolves through GZ_SIM_RESOURCE_PATH.
GZ_ASSETS="$PX4_DIR/Tools/simulation/gz"
ln -sfn "$SCRIPT_DIR/simulation/worlds/crop_field.sdf" "$GZ_ASSETS/worlds/crop_field.sdf"
ln -sfn "$SCRIPT_DIR/simulation/gazebo/models/crop_field" "$GZ_ASSETS/models/crop_field"
export GZ_SIM_RESOURCE_PATH="$SCRIPT_DIR/simulation/gazebo/models:$SCRIPT_DIR/simulation/worlds${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"

# PX4 auto-sources <autostart_file>.post after the 4001_gz_x500 airframe boots;
# link ours in so NAV_DLL_ACT gets disabled (see config/4001_gz_x500.post —
# this swarm has no QGroundControl, so the default "GCS connection lost"
# arming check would otherwise block arming forever).
ln -sfn "$CONFIG_DIR/4001_gz_x500.post" \
    "$PX4_DIR/build/px4_sitl_default/etc/init.d-posix/airframes/4001_gz_x500.post"

# Home position = field origin (first vertex of research/field.geojson)
set -a
source "$CONFIG_DIR/sitl_home.env"
set +a

# Run a command in the background, logged to file — no terminal window.
# gnome-terminal is not used: it's unreliable across environments (e.g. snap
# packaging conflicts can make it fail silently or crash), and under `set -e`
# a single failed gnome-terminal call kills this whole script before later
# components ever start. RViz/fleet_gui still open their own real windows on
# the display regardless of whether their parent process has a terminal.
run_bg() {
    local title="$1"; shift
    local cmd="$*"
    echo "[launch_sitl] $title -> $LOG_DIR/$title.log"
    bash -c "$cmd" >"$LOG_DIR/$title.log" 2>&1 &
}

# --- Vehicle 1: starts Gazebo with the crop-field world and spawns x500 #1 ---
# -d = daemon mode: don't start the interactive pxh shell. Without it, PX4
# detects stdin isn't a tty (we have no terminal window) and spins re-printing
# the pxh> prompt in a tight loop instead of booting — it never actually
# starts Gazebo, which is why nothing came up.
# PX4_GZ_NO_FOLLOW=1: without it, PX4 snaps the Gazebo camera into a tight
# (-2,-2,2 m) follow-chase on whichever vehicle just spawned, so the field
# disappears from view the moment a drone comes up. Keep the default free
# camera instead.
run_bg "px4_drone1" "cd '$PX4_DIR' && \
    PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500 \
    PX4_GZ_WORLD=crop_field PX4_GZ_MODEL_POSE='0,0' PX4_GZ_NO_FOLLOW=1 \
    '$PX4_BIN' -i 1 -d"

echo "Waiting for Gazebo and vehicle 1 to come up..."
sleep 15

# --- Vehicle 2: attaches to the running simulation and spawns x500 #2 -------
run_bg "px4_drone2" "cd '$PX4_DIR' && \
    PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500 \
    PX4_GZ_WORLD=crop_field PX4_GZ_MODEL_POSE='4,0' PX4_GZ_NO_FOLLOW=1 \
    '$PX4_BIN' -i 2 -d"

sleep 10

# --- One agent serves both PX4 uXRCE-DDS clients ----------------------------
run_bg "xrce_agent" "MicroXRCEAgent udp4 -p 8888"

sleep 5

# --- Planner stack: mission manager, drone nodes, RViz, fleet GUI -----------
# unset GTK_PATH: when this script runs from a terminal launched inside a
# snap-confined app (e.g. VS Code's snap build), GTK_PATH points into that
# snap's bundled GTK module dir, which drags in an incompatible libpthread
# and crashes any Qt/GTK GUI (rviz2, fleet_gui) with a symbol lookup error.
run_bg "planner" "unset GTK_PATH; source /opt/ros/humble/setup.bash && \
    source '$WORKSPACE_DIR/install/setup.bash' && \
    ros2 launch planner swarm_launch.xml"

echo "All components launched. Logs: $LOG_DIR"
