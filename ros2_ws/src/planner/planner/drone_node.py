import rclpy
from rclpy.node import Node
from math import pi, sqrt, sin, cos
from geometry_msgs.msg import PoseStamped
from mission_msg.msg import Mission
from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    DurabilityPolicy,
    HistoryPolicy,
)
from std_msgs.msg import String, Int32, Float32
from px4_msgs.msg import (
    OffboardControlMode,
    TrajectorySetpoint,
    VehicleCommand,
    VehicleLocalPosition,
    VehicleStatus,
    BatteryStatus,
)


def wrap_pi(angle):
    while angle > pi:
        angle -= 2.0 * pi
    while angle < -pi:
        angle += 2.0 * pi
    return angle


class Drone(Node):
    def __init__(self):
        super().__init__("drone")
        self.declare_parameter("drone_id", "drone1")
        self.declare_parameter("simulate_failure", False)
        # PX4 uXRCE-DDS namespace: instance N started with `px4 -i N` publishes
        # under /px4_N/fmu/... and has MAV_SYS_ID = N + 1 (its target_system).
        self.declare_parameter("px4_ns", "")
        self.declare_parameter("target_system", 1)
        # Where this vehicle spawned in the Gazebo/field ENU world frame.
        # PX4's local NED origin is the spawn point, so world-frame missions
        # must be shifted by this offset before being sent as setpoints.
        self.declare_parameter("spawn_east", 0.0)
        self.declare_parameter("spawn_north", 0.0)
        self.declare_parameter("mission_altitude", -5.0)
        self.declare_parameter("waypoint_threshold", 1.0)
        # PX4 message versioning appends _v<N> to versioned topics; adjust these
        # if `ros2 topic list` shows different suffixes for your PX4 version.
        self.declare_parameter("local_position_topic", "fmu/out/vehicle_local_position_v1")
        self.declare_parameter("vehicle_status_topic", "fmu/out/vehicle_status_v4")
        self.declare_parameter("battery_status_topic", "fmu/out/battery_status_v1")

        self.drone_id = self.get_parameter("drone_id").value
        self.simulate_failure = self.get_parameter("simulate_failure").value
        self.px4_ns = self.get_parameter("px4_ns").value
        self.target_system = self.get_parameter("target_system").value
        self.spawn_east = self.get_parameter("spawn_east").value
        self.spawn_north = self.get_parameter("spawn_north").value
        self.mission_altitude = self.get_parameter("mission_altitude").value
        self.waypoint_threshold = self.get_parameter("waypoint_threshold").value

        prefix = f"/{self.px4_ns}" if self.px4_ns else ""

        # PX4 publishes /fmu/out/* as best-effort; a default (reliable)
        # subscription never matches and silently receives nothing.
        px4_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
        )
        self.create_subscription(
            Mission, f"/{self.drone_id}/mission", self.mission_callback, 10
        )
        self.create_subscription(
            VehicleLocalPosition,
            f"{prefix}/{self.get_parameter('local_position_topic').value}",
            self.vehicle_local_pos_callback,
            px4_qos,
        )
        self.create_subscription(
            VehicleStatus,
            f"{prefix}/{self.get_parameter('vehicle_status_topic').value}",
            self.vehicle_stat_callback,
            px4_qos,
        )
        self.create_subscription(
            BatteryStatus,
            f"{prefix}/{self.get_parameter('battery_status_topic').value}",
            self.battery_callback,
            px4_qos,
        )
        self.trajectory = []
        self.state = "IDLE"
        self.drone_x = 0.0  # local NED north
        self.drone_y = 0.0  # local NED east
        self.drone_z = 0.0  # local NED down
        self.arming_state = 0
        self.accept_offboard = False
        self.target_x = 0.0
        self.target_y = 0.0
        self.target_z = self.mission_altitude
        self.target_yaw = 0.0
        self.current_index = 0
        self.mission_completed = False
        self.failed = False
        self.battery = 100.00
        self.home_x = 0.0
        self.home_y = 0.0
        self.status_received = False
        self.position_received = False
        self.last_status = None
        self.timer = self.create_timer(0.05, self.update)
        self.pose_pub = self.create_publisher(PoseStamped, f"/{self.drone_id}/pose", 10)
        self.status_pub = self.create_publisher(String, f"/{self.drone_id}/status", 10)
        self.index_pub = self.create_publisher(Int32, f"/{self.drone_id}/progress", 10)
        self.ofm_pub = self.create_publisher(
            OffboardControlMode, f"{prefix}/fmu/in/offboard_control_mode", 10
        )
        self.tsp_pub = self.create_publisher(
            TrajectorySetpoint, f"{prefix}/fmu/in/trajectory_setpoint", 10
        )
        self.vc_pub = self.create_publisher(
            VehicleCommand, f"{prefix}/fmu/in/vehicle_command", 10
        )
        self.battery_pub = self.create_publisher(
            Float32, f"/{self.drone_id}/battery", 10
        )
        self.offboard_timer = self.create_timer(0.1, self.offboard_loop)
        self.telemetry_timer = self.create_timer(1.0, self.telemetry)

    def enu_to_local_ned(self, east, north, yaw_enu):
        """World ENU waypoint -> this vehicle's local NED (origin = spawn)."""
        ned_x = north - self.spawn_north
        ned_y = east - self.spawn_east
        ned_yaw = wrap_pi(pi / 2.0 - yaw_enu)
        return ned_x, ned_y, ned_yaw

    def mission_callback(self, msg):
        incoming_trajectory = []
        for waypoint in msg.waypoints:
            x, y, yaw = self.enu_to_local_ned(waypoint.x, waypoint.y, waypoint.yaw)
            incoming_trajectory.append((x, y, yaw, waypoint.spray_enabled))
        if self.state == "IDLE" and len(self.trajectory) == 0:
            if len(incoming_trajectory) == 0:
                return
            self.trajectory = incoming_trajectory
            self.state = "REQUESTING_OFFBOARD"
            self.current_index = 0
            self.mission_completed = False
            self.failed = False
            self.last_status = None
            self.get_logger().info(f"{self.drone_id} received mission")
        elif self.state in ("MISSION", "REQUESTING_OFFBOARD", "ARMING", "TAKING_OFF") \
                and len(incoming_trajectory) > len(self.trajectory):
            new_section = incoming_trajectory[len(self.trajectory):]
            self.trajectory.extend(new_section)
            self.get_logger().info(f"{self.drone_id} received reassigned mission")

    def publish_status(self, status):
        # Only publish transitions; execute_mission calls this at 20 Hz
        if status == self.last_status:
            return
        self.last_status = status
        msg = String()
        msg.data = status
        self.status_pub.publish(msg)

    def state_machine(self):
        if self.state == "REQUESTING_OFFBOARD":
            self.execute_requesting_offboard()
        elif self.state == "ARMING":
            self.execute_arming()
        elif self.state == "TAKING_OFF":
            self.execute_taking_off()
        elif self.state == "MISSION":
            self.execute_mission()
        elif self.state == "RETURNING":
            self.send_trajectory_setpoint(
                self.home_x, self.home_y, self.mission_altitude, self.target_yaw
            )
            if sqrt((self.drone_x - self.home_x) ** 2 + (self.drone_y - self.home_y) ** 2) < 0.5:
                self.state = "LANDING"
        elif self.state == "LANDING":
            self.execute_landing()

    def vehicle_local_pos_callback(self, msg):
        self.position_received = True
        self.drone_x = msg.x
        self.drone_y = msg.y
        self.drone_z = msg.z

    def vehicle_stat_callback(self, msg):
        self.status_received = True
        self.arming_state = msg.arming_state
        self.accept_offboard = msg.nav_state == 14  # NAVIGATION_STATE_OFFBOARD

    def battery_callback(self, msg):
        self.battery = msg.remaining * 100.0

    def execute_mission(self):
        if self.simulate_failure and self.current_index > 10:
            if not self.failed:
                self.state = "FAILED"
                self.publish_status("FAILED")
                self.failed = True
            return
        if self.battery <= 20.0:
            self.state = "RETURNING"
            self.publish_status("RETURNING")
            self.get_logger().info(f"{self.drone_id} returning home")
            return
        if self.current_index < len(self.trajectory):
            x, y, yaw_target, spray = self.trajectory[self.current_index]
            if spray:
                self.publish_status("SPRAYING")
            else:
                self.publish_status("TRANSIT")
            dx = x - self.drone_x
            dy = y - self.drone_y
            distance = sqrt((dx**2) + (dy**2))
            self.send_trajectory_setpoint(x, y, self.mission_altitude, yaw_target)
            if distance < self.waypoint_threshold:
                self.current_index += 1
            index_msg = Int32()
            index_msg.data = self.current_index
            self.index_pub.publish(index_msg)
        else:
            if not self.mission_completed:
                self.get_logger().info(
                    f"{self.drone_id} completed mission, returning home"
                )
                self.mission_completed = True
                self.publish_status("COMPLETED")
                self.state = "RETURNING"

    def publish_pose(self):
        """Publish the drone pose in the world ENU (map) frame for RViz."""
        pose_msg = PoseStamped()
        pose_msg.header.stamp = self.get_clock().now().to_msg()
        pose_msg.header.frame_id = "map"
        pose_msg.pose.position.x = self.drone_y + self.spawn_east
        pose_msg.pose.position.y = self.drone_x + self.spawn_north
        pose_msg.pose.position.z = -self.drone_z
        enu_yaw = wrap_pi(pi / 2.0 - self.target_yaw)
        pose_msg.pose.orientation.x = 0.0
        pose_msg.pose.orientation.y = 0.0
        pose_msg.pose.orientation.z = sin(enu_yaw / 2.0)
        pose_msg.pose.orientation.w = cos(enu_yaw / 2.0)
        self.pose_pub.publish(pose_msg)

    def send_trajectory_setpoint(self, x, y, z, yaw):
        # Remember the last commanded setpoint so offboard_loop re-streams the
        # same target instead of fighting the state machine with a stale one.
        self.target_x = float(x)
        self.target_y = float(y)
        self.target_z = float(z)
        self.target_yaw = float(yaw)
        msg = TrajectorySetpoint()
        msg.position = [self.target_x, self.target_y, self.target_z]
        msg.yaw = self.target_yaw
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.tsp_pub.publish(msg)

    def send_offboard_control_mode(self):
        msg = OffboardControlMode()
        msg.position = True
        msg.velocity = False
        msg.acceleration = False
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.ofm_pub.publish(msg)

    def make_vehicle_command(self, command):
        msg = VehicleCommand()
        msg.command = command
        msg.target_system = self.target_system
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        return msg

    def send_arm_commands(self):
        msg = self.make_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM)
        msg.param1 = 1.0
        msg.param2 = 21196.0
        self.vc_pub.publish(msg)

    def send_land_commands(self):
        msg = self.make_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)
        self.vc_pub.publish(msg)

    def offboard_loop(self):
        if self.state not in ("IDLE", "FAILED", "LANDING"):
            self.send_offboard_control_mode()
            msg = TrajectorySetpoint()
            msg.position = [self.target_x, self.target_y, self.target_z]
            msg.yaw = self.target_yaw
            msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
            self.tsp_pub.publish(msg)

    def execute_requesting_offboard(self):
        msg = self.make_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE)
        msg.param1 = 1.0
        msg.param2 = 6.0  # PX4_CUSTOM_MAIN_MODE_OFFBOARD
        self.vc_pub.publish(msg)
        if self.accept_offboard:
            self.state = "ARMING"

    def execute_arming(self):
        self.send_arm_commands()
        if self.arming_state == 2:  # ARMING_STATE_ARMED
            self.home_x = self.drone_x
            self.home_y = self.drone_y
            self.send_trajectory_setpoint(
                self.drone_x, self.drone_y, self.mission_altitude, self.target_yaw
            )
            self.state = "TAKING_OFF"

    def execute_taking_off(self):
        self.send_trajectory_setpoint(
            self.home_x, self.home_y, self.mission_altitude, self.target_yaw
        )
        if abs(self.drone_z - self.mission_altitude) < 0.5:
            self.state = "MISSION"

    def execute_landing(self):
        self.send_land_commands()
        if abs(self.drone_z) < 0.3 and self.arming_state != 2:
            self.state = "IDLE"
            self.trajectory = []
            self.current_index = 0

    def update(self):
        if self.state == "IDLE":
            return
        self.state_machine()
        self.publish_pose()

    def telemetry(self):
        msg = Float32()
        msg.data = self.battery
        self.battery_pub.publish(msg)
        if self.state == "REQUESTING_OFFBOARD" and not self.status_received:
            self.get_logger().warn(
                f"{self.drone_id}: no VehicleStatus received yet on "
                f"'{self.get_parameter('vehicle_status_topic').value}' "
                f"(px4_ns='{self.px4_ns}'). Check that the MicroXRCEAgent is "
                "running and that the topic suffix matches `ros2 topic list` "
                "(PX4 message versioning, e.g. _v1/_v4)."
            )


def main(args=None):
    rclpy.init(args=args)
    node = Drone()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
