import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
import sys
sys.path.append("/home/dheeraj/CropFleet-Core")
from geometry_msgs.msg import PoseStamped
from tf_transformations import quaternion_from_euler
from coverage_planner.enviroments.field_loader import field_loader
from coverage_planner.coverage.coverage_pipeline import run_pipe
from coverage_planner.mission.mission_generator import  heading,generate_mission
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
from std_msgs.msg import String,Int32

class MissionManager(Node):
        def __init__(self):
            super().__init__("mission_manager")
            self.num_drones = 2
            field = field_loader() 
            polygon = field["polygon"]
            all_traversals = run_pipe(polygon,self.num_drones)
            self.mission_publishers = {}
            self.path_messages =  {}
            self.drone_status = {}
            self.remaining_mission = []
            self.drone_progress = {}
            self.current_index =  0
            self.drone_progress = {}
            self.drone_status = {}
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
                 self.create_subscription(String, f"/{drone_id}/status", lambda msg, d= drone_id:self.status_callback(msg, d), 10)
                 self.create_subscription(Int32,f"/{drone_id}/progress",lambda msg, d=drone_id:self.progress_callback(msg, d), 10)
                 self.remaining_mission_pub = self.create_publisher(Path, f"/{drone_id}/remaining_waypoints", 10)
                 self.mission_publishers[drone_id] = self.create_publisher(Path, f"/{drone_id}/mission", 10)
                 self.mission_waypoints = generate_mission(traversal)
                 self.trajectory  = heading(self.mission_waypoints)
                 path_msg =  Path()
                 path_msg.header.frame_id = "map"
                 for x,y,yaw in self.trajectory:
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
        
        def progress_callback(self, msg, drone_id):
            self.drone_progress[drone_id]  = msg.data

        def status_callback(self, msg, drone_id):
            self.drone_status[drone_id] =  msg.data
            self.get_logger().info(f"{drone_id}: {msg.data}")
            if msg.data == "FAILED":
                if drone_id not in self.drone_progress:
                    self.get_logger().warn(f"No progress data for {drone_id}")
                    return
                failed_index = self.drone_progress[drone_id]
                failed_path =self.path_messages[drone_id]
                remaining_mission = failed_path.poses[failed_index:]
                failed_drone = drone_id
                reassigned = False
                for other_drone, status in self.drone_status.items():
                    if  status == "ACTIVE" and other_drone != failed_drone:
                        self.path_messages[other_drone].poses.extend(remaining_mission)
                        self.path_messages[failed_drone].poses = []
                        self.get_logger().info(f"Reassigned mission from "f"{failed_drone} to {other_drone}")
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


def  main(args=None):
     rclpy.init(args=args)
     node = MissionManager()
     rclpy.spin(node)
     rclpy.shutdown()


if __name__=='__main__':
    main()