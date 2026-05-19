        
import rclpy
from rclpy.node import Node
from math import atan2,sqrt
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from tf_transformations import quaternion_from_euler

class Drone(Node):
    def __init__(self):
        super().__init__("drone")
        self.declare_parameter("drone_id", "drone1")
        self.drone_id = self.get_parameter("drone_id").get_parameter_value().string_value
        self.create_subscription(Path, f"/{self.drone_id}/mission",self.mission_callback, 10)
        self.trajectory = [] 
        self.speed = 0.05
        self.drone_x = 0.0
        self.drone_y = 0.0
        self.drone_yaw = 0.0
        self.current_index = 0
        self.mission_completed = False
        self.timer = self.create_timer(0.05,self.update)
        self.pose_pub = self.create_publisher(PoseStamped,f"/{self.drone_id}/pose", 10) 

    def mission_callback(self, msg):
        if len(self.trajectory)>0:
            return
        self.trajectory = []
        for pose in msg.poses:
            x = pose.pose.position.x
            y = pose.pose.position.y
            self.trajectory.append((x, y))
        if len(self.trajectory) > 0:
            self.drone_x = self.trajectory[0][0]
            self.drone_y = self.trajectory[0][1]
            self.current_index = 0
            self.mission_completed = False
        self.get_logger().info(f"{self.drone_id} received mission")

    def update(self):
        if len(self.trajectory)  == 0:
            return
        
        if self.current_index < len(self.trajectory):

            x, y= self.trajectory[self.current_index]
            dx = x - self.drone_x
            dy = y - self.drone_y
            distance = sqrt((dx**2) + (dy**2))
            threshold = 0.05
            if distance < threshold:
                self.current_index += 1
            else:
                if distance > 0:
                    unit_x = dx / distance
                    unit_y = dy / distance
                    vx = unit_x * self.speed
                    vy = unit_y * self.speed
                    self.drone_x += vx
                    self.drone_y += vy
                    yaw = atan2(dy, dx)
                    self.drone_yaw =  yaw
            qx, qy, qz, qw = quaternion_from_euler(0,0,self.drone_yaw)
            pose_msg = PoseStamped()
            pose_msg.header.stamp =  self.get_clock().now().to_msg()
            pose_msg.header.frame_id = "map"
            pose_msg.pose.position.x = self.drone_x
            pose_msg.pose.position.y = self.drone_y
            pose_msg.pose.position.z = 0.2

            pose_msg.pose.orientation.x = qx
            pose_msg.pose.orientation.y = qy
            pose_msg.pose.orientation.z = qz
            pose_msg.pose.orientation.w = qw
            self.pose_pub.publish(pose_msg)
            
        else:
            if not self.mission_completed:
                self.get_logger().info(f"{self.drone_id} completed mission")
                self.mission_completed = True



def main(args=None):
    rclpy.init(args=args)
    node = Drone()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__=='__main__':
    main()