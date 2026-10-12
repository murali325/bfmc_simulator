#!/usr/bin/env python3
"""
simulator_node.py
=================
ROS 2 Python node for the BFMC Simulator.

Responsibilities:
1. Subscribes to camera frames from Gazebo (/automobile/image_raw, /automobile/camera_info).
2. Subscribes to odometry/pose from Gazebo (/model/automobile/odometry).
3. Subscribes to BFMC JSON commands on /automobile/command:
     {"action":"1","speed":<float m/s>}       -> speed
     {"action":"2","steerAngle":<float deg>}  -> steering
     {"action":"3","steerAngle":<float deg>}  -> brake
   and translates them into geometry_msgs/Twist on /cmd_vel for Gazebo.
4. Publishes command acknowledgements to /automobile/feedback.
"""

import json
import math
import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from sensor_msgs.msg import Image, CameraInfo, Imu
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry


class SimulatorNode(Node):

    def __init__(self):
        super().__init__('simulator_node')

        self.get_logger().info('Initializing BFMC Simulator ROS 2 Node...')

        # Internal state
        self.speed_mps = 0.0
        self.steer_deg = 0.0
        self.frame_count = 0
        self.last_img_time = self.get_clock().now()

        # ── Publishers ──
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.feedback_pub = self.create_publisher(String, '/automobile/feedback', 10)

        # ── Subscribers ──
        self.cmd_sub = self.create_subscription(
            String,
            '/automobile/command',
            self.command_callback,
            10
        )

        self.image_sub = self.create_subscription(
            Image,
            '/automobile/image_raw',
            self.image_callback,
            10
        )

        self.cam_info_sub = self.create_subscription(
            CameraInfo,
            '/automobile/camera_info',
            self.camera_info_callback,
            10
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            '/model/automobile/odometry',
            self.odometry_callback,
            10
        )

        # Periodic status heartbeat
        self.timer = self.create_timer(5.0, self.heartbeat_callback)

        self.get_logger().info(
            'Simulator Node ready!\n'
            '  Subscribing to: /automobile/command (BFMC JSON), /automobile/image_raw\n'
            '  Publishing to:  /cmd_vel, /automobile/feedback'
        )

    # ── Command Callback ──
    def command_callback(self, msg: String):
        try:
            doc = json.loads(msg.data)
        except json.JSONDecodeError:
            self.get_logger().warn(f'Invalid JSON command: {msg.data}')
            self.send_feedback('@MESS:err;;')
            return

        action = str(doc.get('action', ''))

        if action == '1':  # Speed command
            if 'speed' in doc:
                self.speed_mps = float(doc['speed'])
                self.apply_cmd_vel()
                self.send_feedback('@1:ack;;')
            else:
                self.send_feedback('@MESS:err;;')

        elif action == '2':  # Steer command
            if 'steerAngle' in doc:
                self.steer_deg = float(doc['steerAngle'])
                self.apply_cmd_vel()
                self.send_feedback('@2:ack;;')
            else:
                self.send_feedback('@MESS:err;;')

        elif action == '3':  # Brake command
            self.speed_mps = 0.0
            if 'steerAngle' in doc:
                self.steer_deg = float(doc['steerAngle'])
            self.apply_cmd_vel()
            self.send_feedback('@3:ack;;')

        else:
            self.get_logger().warn(f'Unknown command action: {action}')
            self.send_feedback('@MESS:err;;')

    def apply_cmd_vel(self):
        """Convert speed and steer angle to Twist message for Ackermann controller."""
        twist = Twist()
        twist.linear.x = self.speed_mps
        # Convert steer angle in degrees to angular z for Ackermann steering in Gazebo
        steer_rad = math.radians(self.steer_deg)
        # Angular velocity = (v / L) * tan(steer_angle) where L = 0.26m wheelbase
        wheelbase = 0.26
        if abs(self.speed_mps) > 1e-4:
            twist.angular.z = (self.speed_mps / wheelbase) * math.tan(steer_rad)
        else:
            twist.angular.z = steer_rad * 1.5

        self.cmd_vel_pub.publish(twist)

    def send_feedback(self, text: str):
        msg = String()
        msg.data = text
        self.feedback_pub.publish(msg)

    # ── Sensor Callbacks ──
    def image_callback(self, msg: Image):
        self.frame_count += 1
        self.last_img_time = self.get_clock().now()

    def camera_info_callback(self, msg: CameraInfo):
        pass

    def odometry_callback(self, msg: Odometry):
        pass

    # ── Heartbeat ──
    def heartbeat_callback(self):
        fps = self.frame_count / 5.0
        self.frame_count = 0
        if fps > 0:
            self.get_logger().info(
                f'[Camera Active] Receiving images at ~{fps:.1f} FPS (640x480) on /automobile/image_raw'
            )


def main(args=None):
    rclpy.init(args=args)
    node = SimulatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
