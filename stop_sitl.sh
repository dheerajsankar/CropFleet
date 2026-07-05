#!/bin/bash
# Kill every process started by launch_sitl.sh (PX4 x2, Gazebo server+GUI,
# MicroXRCEAgent, and the whole ros2 launch planner tree: mission_manager,
# drone_node x2, visualization, fleet_gui, rviz2).
#
# Leftover processes from a previous run are not just clutter — a stale
# `gz sim` server silently reattaches on the next launch_sitl.sh instead of
# loading a fresh world, which caused missing sensor data and broken arming
# earlier. Always stop everything before restarting.

PATTERNS=(
    "px4_sitl_default/bin/px4"
    "gz sim"
    "MicroXRCEAgent"
    "ros2 launch planner"
    "install/planner/lib/planner/mission_manager"
    "install/planner/lib/planner/drone_node"
    "install/planner/lib/planner/visualization"
    "install/planner/lib/planner/fleet_gui"
    "lib/rviz2/rviz2"
)

for pattern in "${PATTERNS[@]}"; do
    pkill -9 -f "$pattern" 2>/dev/null || true
done

sleep 1
echo "Stopped. Remaining (should be empty):"
pgrep -af "px4_sitl_default/bin/px4|gz sim|MicroXRCEAgent|ros2 launch planner|mission_manager|drone_node|visualization|fleet_gui|rviz2" 2>/dev/null || echo "(none)"
