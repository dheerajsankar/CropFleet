import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32, Float32
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication,QWidget,QLabel,QVBoxLayout,QHBoxLayout,QFrame
from PyQt5.QtGui import QFont

class GUI(Node):
    def __init__(self):
        super().__init__("gui")
        self.num_drones = 2
        self.window = QWidget()
        self.window.setWindowTitle("CropFleet Command Console")
        self.window.resize(800, 300)
        self.window.setStyleSheet("""

            QWidget {
                background-color: #0d0d0d;
                color: #00ff66;
                font-family: Consolas;
                font-size: 14px;
            }

            QLabel {
                padding: 4px;
            }

            QFrame {
                border: 2px solid #00ff66;
                border-radius: 8px;
                padding: 12px;
                background-color: #151515;
            }

        """)

        self.layout = QHBoxLayout()
        self.drone_battery = {}
        self.drone_progress = {}
        self.drone_states = {}
        self.battery_labels = {}
        self.status_labels = {}
        self.progress_labels = {}
        self.mode_labels = {}



        for i in range(self.num_drones):
            drone_id = f"drone{i+1}"
            frame = QFrame()
            drone_layout = QVBoxLayout()
            frame.setLayout(drone_layout)
            title_label = QLabel(drone_id.upper())
            title_label.setFont(QFont("Consolas", 16, QFont.Bold))
            drone_layout.addWidget(title_label)
            battery_label = QLabel("Battery: --")
            self.battery_labels[drone_id] = battery_label
            drone_layout.addWidget(battery_label)
            status_label = QLabel("State: --")
            self.status_labels[drone_id] = status_label
            drone_layout.addWidget(status_label)
            mode_label = QLabel("Mode: --")
            self.mode_labels[drone_id] = mode_label
            drone_layout.addWidget(mode_label)

            progress_label = QLabel("Progress: --")
            self.progress_labels[drone_id] = progress_label
            drone_layout.addWidget(progress_label)
            self.layout.addWidget(frame)
            self.create_subscription(
                Float32,
                f"/{drone_id}/battery",
                lambda msg, d=drone_id: self.battery_callback(msg, d),
                10,
            )
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


        self.window.setLayout(self.layout)
        self.gui_timer = QTimer()
        self.gui_timer.timeout.connect(self.update_gui)
        self.gui_timer.start(100)

        self.window.show()

    def battery_callback(self, msg, drone_id):
        self.drone_battery[drone_id] = msg.data
    def status_callback(self, msg, drone_id):
        self.drone_states[drone_id] = msg.data
    def progress_callback(self, msg, drone_id):
        self.drone_progress[drone_id] = msg.data

    def update_gui(self):
        for i in range(self.num_drones):
            drone_id = f"drone{i+1}"
            battery = self.drone_battery.get(drone_id, 0.0)
            status = self.drone_states.get(drone_id, "UNKNOWN")
            progress = self.drone_progress.get(drone_id, 0)
            if status == "SPRAYING":
                mode = "SPRAY ACTIVE"
            elif status == "TRANSIT":
                mode = "TRANSIT"
            elif status == "RETURNING":
                mode = "RETURN TO HOME"
            elif status == "FAILED":
                mode = "FAILURE"
            elif status == "COMPLETED":
                mode = "MISSION COMPLETE"
            else:
                mode = "IDLE"
            self.battery_labels[drone_id].setText(f"Battery: {battery:.1f}%")
            self.status_labels[drone_id].setText(f"State: {status}")
            self.mode_labels[drone_id].setText(f"Mode: {mode}")
            self.progress_labels[drone_id].setText(f"Progress: {progress}")
            if status == "FAILED":
                self.status_labels[drone_id].setStyleSheet("color: red;")
            elif status == "RETURNING":
                self.status_labels[drone_id].setStyleSheet("color: yellow;")
            elif status == "SPRAYING":
                self.status_labels[drone_id].setStyleSheet("color: #00ff66;")
            else:
                self.status_labels[drone_id].setStyleSheet("color: cyan;")


def main(args=None):

    rclpy.init(args=args)
    app = QApplication([])
    gui = GUI()
    ros_timer = QTimer()
    ros_timer.timeout.connect(lambda: rclpy.spin_once(gui, timeout_sec=0))
    ros_timer.start(10)
    app.exec_()
    gui.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":

    main()
