#!/usr/bin/env python3
import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    # config file path
    rviz_config_dir = os.path.join(
        get_package_share_directory('turtles'),
        'rviz',
        'map_gen.rviz'
    )

    # map gen node
    map_gen = Node(
        package="turtles",
        executable="field.py",
        output="screen"
    )    

    # rviz
    rviz2 =  Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_dir],
        output='screen'
    )

    return LaunchDescription([
        map_gen,
        rviz2
    ])