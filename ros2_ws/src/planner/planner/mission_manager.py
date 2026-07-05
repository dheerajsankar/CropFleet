import rclpy
from rclpy.node import Node
from mission_msg.msg import Mission, MissionWaypoint
from coverage_planner.enviroments.field_loader import field_loader
from coverage_planner.coverage.coverage_pipeline import run_pipe
from coverage_planner.mission.mission_generator import heading, generate_mission
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
from std_msgs.msg import String, Int32
from geometry_msgs.msg import PoseStamped


class MissionManager(Node):
    def __init__(self):
        super().__init__("mission_manager")
        self.declare_parameter("num_drones", 2)
        self.num_drones = self.get_parameter("num_drones").value
        field = field_loader()
        polygon = field["polygon"]
        all_traversals = run_pipe(polygon, self.num_drones, field["lane_spacing"])
        self.mission_publishers = {}
        self.path_messages = {}
        self.drone_status = {}
        self.drone_progress = {}
        self.drone_positions = {}
        self.boundary_pub = self.create_publisher(Marker, "/visualization_marker", 10)
        self.boundary_marker = Marker()
        self.boundary_marker.header.frame_id = "map"
        self.boundary_marker.ns = "field"
        self.boundary_marker.id = 999
        self.boundary_marker.type = Marker.LINE_STRIP
        self.boundary_marker.action = Marker.ADD
        self.boundary_marker.scale.x = 0.5
        self.boundary_marker.color.r = 0.0
        self.boundary_marker.color.g = 0.5
        self.boundary_marker.color.b = 1.0
        self.boundary_marker.color.a = 1.0
        # Field polygon is in local ENU meters (origin = first geojson vertex),
        # which is also the Gazebo world / RViz map frame — publish 1:1.
        for x, y in polygon.exterior.coords:
            point = Point()
            point.x = x
            point.y = y
            point.z = 0.1
            self.boundary_marker.points.append(point)
        for i, traversal in enumerate(all_traversals):
            drone_id = f"drone{i+1}"
            self.create_subscription(
                String,
                f"/{drone_id}/status",
                lambda msg, d=drone_id: self.status_callback(msg, d),
                10,
            )
            self.create_subscription(
                Int32,
                f"/{drone_id}/progress",
                lambda msg, d=drone_id: self.progress_callback(msg, d),
                10,
            )
            self.create_subscription(
                PoseStamped,
                f"/{drone_id}/pose",
                lambda msg, d=drone_id: self.pose_callback(msg, d),
                10,
            )
            self.mission_publishers[drone_id] = self.create_publisher(
                Mission, f"/{drone_id}/mission", 10
            )
            mission_waypoints = generate_mission(traversal)
            trajectory = heading(mission_waypoints)
            path_msg = Mission()
            path_msg.header.frame_id = "map"
            # Waypoints stay in world ENU meters; each drone_node converts to
            # its own PX4 local NED frame (spawn offset + axis swap).
            for x, y, yaw, spray in trajectory:
                waypoint = MissionWaypoint()
                waypoint.x = x
                waypoint.y = y
                waypoint.z = 0.0
                waypoint.yaw = yaw
                waypoint.spray_enabled = spray
                path_msg.waypoints.append(waypoint)
            self.path_messages[drone_id] = path_msg
        self.timer = self.create_timer(1.0, self.publish_missions)

    def progress_callback(self, msg, drone_id):
        self.drone_progress[drone_id] = msg.data

    def pose_callback(self, msg, drone_id):
        self.drone_positions[drone_id] = (msg.pose.position.x, msg.pose.position.y)

    def status_callback(self, msg, drone_id):
        if msg.data == "COMPLETED":
            self.path_messages[drone_id].waypoints = []
            self.get_logger().info(f"{drone_id} mission cleared")
            return
        self.drone_status[drone_id] = msg.data
        self.get_logger().info(f"{drone_id}: {msg.data}")
        if msg.data == "FAILED":
            if drone_id not in self.drone_progress:
                self.get_logger().warn(f"No progress data for {drone_id}")
                return
            failed_index = self.drone_progress[drone_id]
            failed_path = self.path_messages[drone_id]
            remaining_mission = failed_path.waypoints[failed_index:]
            failed_drone = drone_id
            reassigned = False
            for other_drone, status in self.drone_status.items():
                if status in ["SPRAYING", "TRANSIT"] and other_drone != failed_drone:
                    if len(remaining_mission) == 0:
                        self.get_logger().warn("No remaining mission to reassign")
                        return
                    target_waypoint = remaining_mission[0]
                    transit_waypoint = MissionWaypoint()
                    transit_waypoint.x = target_waypoint.x
                    transit_waypoint.y = target_waypoint.y
                    transit_waypoint.z = target_waypoint.z
                    transit_waypoint.yaw = target_waypoint.yaw
                    transit_waypoint.spray_enabled = False
                    self.path_messages[other_drone].waypoints.append(transit_waypoint)
                    self.path_messages[other_drone].waypoints.extend(remaining_mission)
                    self.path_messages[failed_drone].waypoints = []
                    self.get_logger().info(
                        f"Reassigned mission from " f"{failed_drone} to {other_drone}"
                    )
                    reassigned = True
                    break
            if not reassigned:
                self.get_logger().warn("No active drone available for reassignment")

    def publish_missions(self):
        now = self.get_clock().now().to_msg()
        for drone_id, publisher in self.mission_publishers.items():
            path_msg = self.path_messages[drone_id]
            path_msg.header.stamp = now
            publisher.publish(path_msg)
        self.boundary_marker.header.stamp = now
        self.boundary_pub.publish(self.boundary_marker)


def main(args=None):
    rclpy.init(args=args)
    node = MissionManager()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
