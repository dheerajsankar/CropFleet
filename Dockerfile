# Default to Humble (Ubuntu 22.04). To build for Jazzy (Ubuntu 24.04):
#   docker build --build-arg ROS_DISTRO=jazzy .
ARG ROS_DISTRO=humble
FROM ros:${ROS_DISTRO}

# Re-declare after FROM — ARG scope resets across each FROM
ARG ROS_DISTRO=humble

# Number of parallel compile jobs. Default is intentionally low: building
# Fast-DDS (MicroXRCEAgent) and px4_msgs with one job per core easily exhausts
# the ~4 GB Docker Desktop default and OOM-kills the build. Bump it on machines
# with more RAM: --build-arg BUILD_JOBS=$(nproc)
ARG BUILD_JOBS=2
# Cap make's per-package parallelism too, so colcon's heavy single packages
# (e.g. px4_msgs) don't spawn nproc compilers internally.
ENV MAKEFLAGS="-j${BUILD_JOBS}"

ENV DEBIAN_FRONTEND=noninteractive
# Bake distro into the image so the entrypoint can source the right setup.bash at runtime
ENV ROS_DISTRO=${ROS_DISTRO}
# Allow pip to install into the system environment. Ubuntu 24.04 (Jazzy) ships a
# PEP 668 "externally managed" Python that otherwise rejects `pip install`.
# Older pip (Ubuntu 22.04 / Humble) ignores this var, so it's safe across distros.
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# System deps: build tools + distro-specific ROS packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    git \
    cmake \
    build-essential \
    ros-${ROS_DISTRO}-rviz2 \
    python3-pyqt5 \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies (opencv-python-headless avoids pulling in display libs).
# PyQt5 is installed via apt above — it has no arm64 wheel on PyPI, so pip would
# try to build it from source and fail.
RUN pip3 install --no-cache-dir \
    numpy \
    shapely \
    opencv-python-headless \
    matplotlib \
    pyproj

# Build MicroXRCEAgent from source (snap doesn't work in containers)
RUN git clone --depth 1 https://github.com/eProsima/Micro-XRCE-DDS-Agent.git /tmp/uxrce && \
    cmake -S /tmp/uxrce -B /tmp/uxrce/build && \
    cmake --build /tmp/uxrce/build --parallel "${BUILD_JOBS}" && \
    cmake --install /tmp/uxrce/build && \
    ldconfig && \
    rm -rf /tmp/uxrce

WORKDIR /ros2_ws

# Clone px4_msgs — pin branch to match your PX4 firmware version
# Override at build time: --build-arg PX4_MSGS_BRANCH=release/1.14
ARG PX4_MSGS_BRANCH=main
RUN mkdir -p src && \
    git clone --depth 1 --branch ${PX4_MSGS_BRANCH} \
        https://github.com/PX4/px4_msgs.git src/px4_msgs

# Install coverage-planner (local Python package at repo root).
# --no-deps: its deps are already installed above. Notably it requires
# opencv-python (with display libs); skipping deps keeps the headless build
# we installed earlier instead of pulling the full package in on top of it.
COPY coverage_planner/ /tmp/coverage_pkg/coverage_planner/
COPY setup.py /tmp/coverage_pkg/setup.py
RUN pip3 install --no-cache-dir --no-deps /tmp/coverage_pkg/ && \
    rm -rf /tmp/coverage_pkg

# Copy ROS2 packages and config
COPY ros2_ws/src/ src/
COPY config/ config/

# Field polygon needed by field_loader() at runtime; the env var makes the
# lookup independent of the working directory
COPY research/field.geojson research/field.geojson
ENV CROPFLEET_FIELD_GEOJSON=/ros2_ws/research/field.geojson

# Resolve remaining ROS2 deps via rosdep
# coverage-planner is skipped — it's the local pip package above, not in rosdep db
RUN rosdep update && \
    rosdep install --from-paths src --ignore-src -y \
        --skip-keys "coverage-planner"

# Build the workspace
RUN /bin/bash -c \
    "source /opt/ros/${ROS_DISTRO}/setup.bash && \
     colcon build --symlink-install \
       --parallel-workers ${BUILD_JOBS} \
       --cmake-args -DCMAKE_BUILD_TYPE=Release"

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# `docker exec` bypasses the entrypoint, so source ROS in interactive shells
# too — otherwise colcon/ros2 fail with "No module named 'ament_package'"
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /root/.bashrc && \
    echo "[ -f /ros2_ws/install/setup.bash ] && source /ros2_ws/install/setup.bash" >> /root/.bashrc

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
