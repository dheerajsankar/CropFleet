import rclpy
from rclpy.node import Node
from math import atan2,sqrt
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from tf_transformations import quaternion_from_euler
from std_msgs.msg import String, Int32
class Drone(Node):
    def __init__(self):
        super().__init__("drone")
        self.declare_parameter("drone_id", "drone1")
        self.declare_parameter("simulate_failure", False)
        self.drone_id = self.get_parameter("drone_id").get_parameter_value().string_value
        self.simulate_failure = (self.get_parameter("simulate_failure").get_parameter_value().bool_value)
        self.create_subscription(Path, f"/{self.drone_id}/mission",self.mission_callback, 10)
        self.trajectory = [] 
        self.state = "IDLE"
        self.speed = 0.05
        self.drone_x = 0.0
        self.drone_y = 0.0
        self.drone_yaw = 0.0
        self.current_index = 0
        self.mission_completed = False
        self.failed = False
        self.battery = 100.00
        self.home_x = 0.0
        self.home_y = 0.0
        self.timer = self.create_timer(0.05,self.update)
        self.pose_pub = self.create_publisher(PoseStamped,f"/{self.drone_id}/pose", 10)
        self.status_pub = self.create_publisher(String,f"/{self.drone_id}/status", 10) 
        self.index_pub  = self.create_publisher(Int32, f"/{self.drone_id}/progress", 10)
        self.depub_timer = self.create_timer(2.0, self.print_status)
    def mission_callback(self, msg):
        incoming_trajectory = []
        for pose in msg.poses:
            x = pose.pose.position.x
            y = pose.pose.position.y
            incoming_trajectory.append((x, y))
        if len(self.trajectory) == 0:
            if len(incoming_trajectory) == 0:
                return
            self.trajectory = incoming_trajectory
            self.state = "SPRAYING"
            self.drone_x = self.trajectory[0][0]
            self.drone_y = self.trajectory[0][1]
            self.current_index = 0
            self.mission_completed = False
            self.failed = False
            self.get_logger().info(f"{self.drone_id} received mission")
            self.publish_status("ACTIVE")
        elif len(incoming_trajectory) > len(self.trajectory):
            new_section = incoming_trajectory[len(self.trajectory):]
            self.trajectory.extend(new_section)
            self.get_logger().info(f"{self.drone_id} received reassigned mission")


    def publish_status(self, status):
        msg =  String()
        msg.data = status
        self.status_pub.publish(msg)
    
    def state_machine(self):

        if self.state ==  "SPRAYING":
            self.execute_spraying()
        elif self.state ==  "RETURNING":
            self.execute_returning()
        elif self.state == "CHARGING":
            self.execute_charging()
        elif self.state == "FAILED":
            return
        elif self.state == "IDLE":
            return
    
    def execute_returning(self):
        dx = self.home_x - self.drone_x
        dy = self.home_y - self.drone_y
        distance = sqrt((dx**2) + (dy**2))
        threshold = 0.1
        if distance < threshold:
            self.state = "CHARGING"
            self.publish_status("CHARGING")
            self.get_logger().info(
                f"{self.drone_id} started charging")
            return
        if distance > 0:
            unit_x = dx / distance
            unit_y = dy / distance
            vx = unit_x * self.speed
            vy = unit_y * self.speed
            self.drone_x += vx
            self.drone_y += vy
            yaw = atan2(dy, dx)
            self.drone_yaw = yaw
        qx, qy, qz, qw = quaternion_from_euler(0,0,self.drone_yaw)
        pose_msg = PoseStamped()
        pose_msg.header.stamp = (self.get_clock().now().to_msg())
        pose_msg.header.frame_id = "map"
        pose_msg.pose.position.x = self.drone_x
        pose_msg.pose.position.y = self.drone_y
        pose_msg.pose.position.z = 0.2

        pose_msg.pose.orientation.x = qx
        pose_msg.pose.orientation.y = qy
        pose_msg.pose.orientation.z = qz
        pose_msg.pose.orientation.w = qw

        self.pose_pub.publish(pose_msg)
    
    def execute_charging(self):
        self.battery += 0.1
        if self.battery >= 100.0:
            self.battery = 100.0
            self.state = "IDLE"
            self.publish_status("IDLE")
            self.get_logger().info(f"{self.drone_id} fully charged")
    
    def execute_spraying(self):
        self.battery  -= 0.02
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
            index_msg = Int32()
            index_msg.data = self.current_index
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
            self.index_pub.publish(index_msg)
            
        else:
            if not self.mission_completed:
                self.get_logger().info(f"{self.drone_id} completed mission")
                self.mission_completed = True
                self.publish_status("COMPLETED")
                self.state = "IDLE"
    
    def print_status(self):
        self.get_logger().info(f"{self.drone_id} | "f"State: {self.state} | "f"Battery: {self.battery:.1f}")

    def update(self):
        if len(self.trajectory)  == 0:
            return
        self.state_machine()
        

def main(args=None):
    rclpy.init(args=args)
    node = Drone()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__=='__main__':
    main()