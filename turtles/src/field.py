#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from turtles.srv import GenerateMap
import numpy as np
from rclpy.qos import QoSProfile, DurabilityPolicy


class GridGenerator(Node):
    def __init__(self):
        super().__init__('grid_generator')

        qos = QoSProfile(depth=100)
        qos.durability = DurabilityPolicy.TRANSIENT_LOCAL

        self.map_pub = self.create_publisher(OccupancyGrid, '/map', qos)
        self.srv = self.create_service(GenerateMap, 'generate_map', self.generate_map_callback)

    def build_field(self, target_percent):
        field = np.zeros((128, 128), dtype=np.int8)
        rng = np.random.default_rng()

        tetL = [(0,0), (1,0), (2,0), (2,1)]
        tetI = [(0,0), (1,0), (2,0), (3,0)]
        tetT = [(0,0), (1,0), (2,0), (1,1)]
        tetS = [(0,0), (1,0), (1,1), (2,1)]
        tets = [tetL, tetI, tetS, tetT]

        target = float(target_percent)

        while True:
            coverage = np.count_nonzero(field > 0) / field.size * 100.0
            if coverage >= target:
                break

            tet = rng.choice(tets)
            max_x = max(x for x, _ in tet)
            max_y = max(y for _, y in tet)

            x0 = rng.integers(0, field.shape[1] - max_x)
            y0 = rng.integers(0, field.shape[0] - max_y)

            for dx, dy in tet:
                field[y0 + dy, x0 + dx] = 100

        return field

    def generate_map_callback(self, request, response):
        field = self.build_field(request.coverage)

        map_msg = OccupancyGrid()
        map_msg.header.stamp = self.get_clock().now().to_msg()
        map_msg.header.frame_id = 'map'
        map_msg.info.resolution = 0.1
        map_msg.info.width = field.shape[1]
        map_msg.info.height = field.shape[0]
        map_msg.info.origin.position.x = -(field.shape[1] * map_msg.info.resolution) / 2.0
        map_msg.info.origin.position.y = -(field.shape[0] * map_msg.info.resolution) / 2.0
        map_msg.info.origin.position.z = 0.0
        map_msg.info.origin.orientation.w = 1.0
        map_msg.data = field.astype(np.int8).ravel().tolist()

        response.map = map_msg
        self.map_pub.publish(map_msg)

        self.get_logger().info(f"published map with {request.coverage}% coverage")
        return response


def main(args=None):
    rclpy.init(args=args)
    node = GridGenerator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()