#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    # launch turtlesim
    turtlesim = Node(
        package="turtlesim",
        executable="turtlesim_node",
        output="screen"
    )    

    # launch path driver node
    pattern = Node(
        package="turtles",
        executable="victor_sierra.py",
        output="screen"
    )    

    return LaunchDescription([
        turtlesim,
        pattern
    ])