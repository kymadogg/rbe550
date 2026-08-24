#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import math

class VictorSierra(Node):
    def __init__(self):
        super().__init__('victor_sierra')

        # init position globals
        self.px = 5.544445
        self.py = 5.544445
        self.pth = 0.0
       
        cb_group = ReentrantCallbackGroup()
        self.turtle_move = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.create_subscription(Pose, '/turtle1/pose', self.pose_cb, 10, callback_group=cb_group)
        self.rate = self.create_rate(30) # Hz
        self.timer = self.create_timer(1.0, self.start_pattern)

    def pose_cb(self, msg:Pose):
        self.px = msg.x
        self.py = msg.y
        self.pth = msg.theta

    def send_speed(self, linear_speed:float, angular_speed:float):
        twist_msg = Twist()
        twist_msg.linear.x = float(linear_speed)
        twist_msg.angular.z = float(angular_speed)
        self.turtle_move.publish(twist_msg)

    def move(self, distance:float):
        # drive a specific distance
        init_x = self.px
        init_y = self.py
        error = 100

        while abs(error) > 0.01 and rclpy.ok():
            travelled = math.sqrt((self.px - init_x)**2 + (self.py - init_y)**2)
            self.send_speed(0.8, 0) 
            error = distance - travelled
            self.rate.sleep()

        self.send_speed(0.0, 0.0)

    def turn(self, angle:float):
        # rotate a certain amount

        angle = math.radians(angle)
        init_th = self.pth # in rad
        error = 100

        while abs(error) > 0.01 and rclpy.ok():
            turned = self.pth - init_th
            turned = math.atan2(math.sin(turned), math.cos(turned))
            error = angle - turned

            if abs(error) < 0.02:
                break

            self.send_speed(0.0, 0.5 if error > 0 else -0.5)
            self.rate.sleep()

        self.send_speed(0.0, 0.0)

    def start_pattern(self):
        self.timer.cancel()
        self.pattern()

    def pattern(self):
        # the victor sierra search pattern just like figure 1a

        self.turn(90) # initial turn
        self.move(3.0) # radius
        for i in range(2):
            self.turn(-120) # 120 b/c outside turn, 0 if no turn
            self.move(3.0)
            self.turn(-120)
            self.move(6.0)
        for i in range(2):
            self.turn(-120)
            self.move(3.0)
        
def main(args=None):
    rclpy.init(args=args)
    node = VictorSierra()
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()