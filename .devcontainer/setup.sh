#!/bin/bash
# Wires the live mounted source into the image's pre-built ROS workspace,
# then rebuilds so Python symlink-installs point to the mounted files.
set -e

REPO=/workspaces/CropFleet-Core
WS=/ros2_ws

echo "[devcontainer] Linking project packages into ROS workspace..."
for pkg in planner mission_msg drone_des; do
    rm -rf "$WS/src/$pkg"
    ln -sf "$REPO/ros2_ws/src/$pkg" "$WS/src/$pkg"
done

echo "[devcontainer] Installing coverage_planner in editable mode..."
pip3 install --no-cache-dir --no-deps -e "$REPO"

echo "[devcontainer] Building ROS workspace with symlink-install..."
cd "$WS"
source "/opt/ros/${ROS_DISTRO}/setup.bash"
colcon build --symlink-install \
    --cmake-args -DCMAKE_BUILD_TYPE=Release \
    --event-handlers console_cohesion+

# Persist ROS sourcing for every new terminal session
echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /root/.bashrc
echo "source ${WS}/install/setup.bash" >> /root/.bashrc
echo "export ROS_DOMAIN_ID=0" >> /root/.bashrc

echo "[devcontainer] Setup complete."
