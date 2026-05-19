import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
import sys
sys.path.append("/home/dheeraj/CropFleet")
from geometry_msgs.msg import PoseStamped
from tf_transformations import quaternion_from_euler
from coverage_planner.environments.field_loader import field_loader
from coverage_planner.coverage.coverage_pipeline import run_pipe
from coverage_planner.mission.mission_generator import  heading,generate_mission
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point

class MissionManager(Node):
        def __init__(self):
            super().__init__("mission_manager")
            self.num_drones = 2
            field = field_loader() 
            polygon = field["polygon"]
            all_traversals = run_pipe(polygon,self.num_drones)
            self.mission_publishers = {}
            self.path_messages =  {}
            self.boundary_pub = self.create_publisher(Marker,"/visualization_marker",10)
            self.boundary_marker = Marker()
            self.boundary_marker.header.frame_id = "map"
            self.boundary_marker.ns = "field"
            self.boundary_marker.id = 999
            self.boundary_marker.type = Marker.LINE_STRIP
            self.boundary_marker.action = Marker.ADD
            self.boundary_marker.scale.x = 0.08
            self.boundary_marker.color.r = 0.0
            self.boundary_marker.color.g = 0.5
            self.boundary_marker.color.b = 1.0
            self.boundary_marker.color.a = 1.0
            for x, y in polygon.exterior.coords:
                point = Point()
                point.x = x / 100.0
                point.y = y / 100.0
                point.z = 0.0
                self.boundary_marker.points.append(point)
            for i, traversal in enumerate(all_traversals):
                 drone_id = f"drone{i+1}"
                 self.mission_publishers[drone_id] = self.create_publisher(Path, f"/{drone_id}/mission", 10)
                 mission_waypoints = generate_mission(traversal)
                 trajectory  = heading(mission_waypoints)
                 path_msg =  Path()
                 path_msg.header.frame_id = "map"
                 for x,y,yaw in trajectory:
                    pose = PoseStamped()
                    qx, qy, qz, qw = quaternion_from_euler(0,0,yaw)
                    pose.pose.position.x = x / 100.0
                    pose.pose.position.y = y / 100.0
                    pose.pose.position.z = 0.0
                    pose.pose.orientation.x = qx
                    pose.pose.orientation.y = qy
                    pose.pose.orientation.z = qz
                    pose.pose.orientation.w = qw
                    pose.header.frame_id = "map"
                    path_msg.poses.append(pose)
                 self.path_messages[drone_id] = path_msg
            self.timer = self.create_timer(1.0,self.publish_missions)


        def publish_missions(self):
            now = self.get_clock().now().to_msg()
            for drone_id, publisher in self.mission_publishers.items():
                path_msg = self.path_messages[drone_id]
                path_msg.header.stamp = now
                publisher.publish(path_msg)
                self.get_logger().info(f"Publishing mission to {drone_id}")
            self.boundary_marker.header.stamp = now
            self.boundary_pub.publish(self.boundary_marker)



def  main(args=None):
     rclpy.init(args=args)
     node = MissionManager()
     rclpy.spin(node)
     rclpy.shutdown()


if __name__=='__main__':
    main()