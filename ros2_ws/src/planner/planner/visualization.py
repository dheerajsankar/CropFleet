import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Point
from mission_msg.msg import Mission
from visualization_msgs.msg import Marker


class Visualization(Node):
    def __init__(self):
        super().__init__("visualization")
        self.num_drones = 2
        self.drone_markers = {}
        self.path_markers = {}
        self.marker_pub = self.create_publisher(Marker, "/visualization_marker", 10)
        self.colors = {
            "drone1": (1.0, 0.0, 0.0),
            "drone2": (0.0, 1.0, 0.0),
            "drone3": (0.0, 0.0, 1.0),
            "drone4": (1.0, 1.0, 0.0),
        }
        for i in range(self.num_drones):
            drone_id = f"drone{i+1}"
            self.create_subscription(
                PoseStamped,
                f"/{drone_id}/pose",
                lambda msg, d=drone_id: self.pose_callback(msg, d),
                10,
            )
            self.create_subscription(
                Mission,
                f"/{drone_id}/mission",
                lambda msg, d=drone_id: self.mission_callback(msg, d),
                10,
            )

    def pose_callback(self, msg, drone_id):
        marker = Marker()
        marker.header.frame_id = "map"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = drone_id
        marker.id = int(drone_id.replace("drone", ""))
        marker.type = Marker.ARROW
        marker.action = Marker.ADD
        marker.scale.x = 3.0
        marker.scale.y = 1.0
        marker.scale.z = 1.0
        r, g, b = self.colors.get(drone_id, (1.0, 1.0, 1.0))
        marker.color.r = r
        marker.color.g = g
        marker.color.b = b
        marker.color.a = 1.0
        marker.pose = msg.pose
        self.marker_pub.publish(marker)

    def mission_callback(self, msg, drone_id):
        spray_marker = Marker()
        transit_marker = Marker()
        drone_num = int(drone_id.replace("drone", ""))
        r, g, b = self.colors.get(drone_id, (1.0, 1.0, 1.0))
        spray_marker.header.frame_id = "map"
        spray_marker.header.stamp = self.get_clock().now().to_msg()
        spray_marker.ns = f"{drone_id}_spray"
        spray_marker.id = 100 + drone_num
        spray_marker.type = Marker.LINE_STRIP
        spray_marker.action = Marker.ADD
        spray_marker.scale.x = 0.4
        spray_marker.color.r = r
        spray_marker.color.g = g
        spray_marker.color.b = b
        spray_marker.color.a = 1.0
        spray_marker.points = []
        transit_marker.header.frame_id = "map"
        transit_marker.header.stamp = self.get_clock().now().to_msg()
        transit_marker.ns = f"{drone_id}_transit"
        transit_marker.id = 200 + drone_num
        transit_marker.type = Marker.LINE_STRIP
        transit_marker.action = Marker.ADD
        transit_marker.scale.x = 0.4
        transit_marker.color.r = 1.0
        transit_marker.color.g = 1.0
        transit_marker.color.b = 1.0

        transit_marker.color.a = 1.0
        transit_marker.points = []
        for waypoint in msg.waypoints:
            point = Point()
            point.x = waypoint.x
            point.y = waypoint.y
            point.z = 0.0
            if waypoint.spray_enabled:
                spray_marker.points.append(point)
            else:
                transit_marker.points.append(point)

        self.marker_pub.publish(spray_marker)
        self.marker_pub.publish(transit_marker)


def main(args=None):
    rclpy.init(args=args)
    node = Visualization()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
