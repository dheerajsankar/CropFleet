import rclpy       
from visualization_msgs.msg import Marker
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point


class Visualization(Node):
        def __init__(self):
            super().__init__("visualization")
            self.num_drones = 2
            self.drone_markers  =  {}
            self.path_markers = {}
            self.marker_pub = self.create_publisher(Marker,"/visualization_marker",10)
            self.colors = {"drone1": (1.0, 0.0, 0.0),"drone2": (0.0, 1.0, 0.0),"drone3": (0.0, 0.0, 1.0),"drone4": (1.0, 1.0, 0.0),}
            for i in range(self.num_drones):
                drone_id = f"drone{i+1}"
                self.create_subscription(PoseStamped,f"/{drone_id}/pose",lambda msg, d=drone_id:self.pose_callback(msg, d),10)
                self.create_subscription(Path,f"/{drone_id}/mission",lambda msg, d=drone_id:self.mission_callback(msg, d),10)
        
        def pose_callback(self, msg, drone_id):
            marker = Marker()
            marker.header.frame_id = "map"
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = drone_id
            marker.id = int(drone_id.replace("drone",""))
            marker.type = Marker.ARROW
            marker.action = Marker.ADD
            marker.scale.x = 0.4
            marker.scale.y = 0.15
            marker.scale.z = 0.15
            r, g, b = self.colors.get(drone_id,(1.0, 1.0, 1.0))
            marker.color.r = r
            marker.color.g = g
            marker.color.b = b
            marker.color.a = 1.0
            marker.pose = msg.pose
            self.marker_pub.publish(marker)

        def mission_callback(self, msg, drone_id):
            marker = Marker()
            marker.header.frame_id = "map"
            marker.header.stamp = (self.get_clock().now().to_msg())
            marker.ns = f"{drone_id}_path"
            marker.id = 100 + int(drone_id.replace("drone", ""))
            marker.type = Marker.LINE_STRIP
            marker.action = Marker.ADD
            marker.scale.x = 0.05
            r, g, b = self.colors.get(drone_id,(1.0, 1.0, 1.0))
            marker.color.r = r
            marker.color.g = g
            marker.color.b = b
            marker.color.a = 1.0

            for pose in msg.poses:

                point = Point()

                point.x = pose.pose.position.x
                point.y = pose.pose.position.y
                point.z = 0.0

                marker.points.append(point)

            self.marker_pub.publish(marker)

                    

        


def main(args=None):
    rclpy.init(args=args)
    node = Visualization()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
     main()