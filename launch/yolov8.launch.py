# -*- coding: utf-8 -*-
# Copyright (C) 2023  Miguel Ángel González Santamarta

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    #
    # ARGS
    #
    model = LaunchConfiguration("model")
    model_cmd = DeclareLaunchArgument(
        "model", default_value="yolov8n-face.pt", description="Model name or path"
    )

    tracker = LaunchConfiguration("tracker")
    tracker_cmd = DeclareLaunchArgument(
        "tracker", default_value="bytetrack.yaml", description="Tracker name or path"
    )

    device = LaunchConfiguration("device")
    device_cmd = DeclareLaunchArgument(
        "device", default_value="cuda:0", description="Device to use (GPU/CPU)"
    )

    enable = LaunchConfiguration("enable")
    enable_cmd = DeclareLaunchArgument(
        "enable", default_value="True", description="Whether to start darknet enabled"
    )

    threshold = LaunchConfiguration("threshold")
    threshold_cmd = DeclareLaunchArgument(
        "threshold",
        default_value="0.5",
        description="Minimum probability of a detection to be published",
    )

    input_image_topic = LaunchConfiguration("input_image_topic")
    input_image_topic_cmd = DeclareLaunchArgument(
        "input_image_topic",
        default_value="/camera/color/image_raw",
        description="Name of the input image topic",
    )

    namespace = LaunchConfiguration("namespace")
    namespace_cmd = DeclareLaunchArgument(
        "namespace", default_value="yolo", description="Namespace for the nodes"
    )

    #
    # NODES
    #
    detector_node_cmd = Node(
        package="festival_ur_yolo",
        executable="yolov8_node",
        name="yolov8_node",
        namespace=namespace,
        parameters=[
            {"model": model, "device": device,
                "enable": enable, "threshold": threshold}
        ],
        remappings=[("image_raw", input_image_topic)],
    )

    tracking_node_cmd = Node(
        package="festival_ur_yolo",
        executable="tracking_node",
        name="tracking_node",
        namespace=namespace,
        parameters=[{"tracker": tracker}],
        remappings=[("image_raw", input_image_topic)],
    )

    debug_node_cmd = Node(
        package="festival_ur_yolo",
        executable="debug_node",
        name="debug_node",
        namespace=namespace,
        remappings=[("image_raw", input_image_topic),
                    ("detections", "detections")],
    )
    rs_launch_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution(
                    [FindPackageShare("realsense2_camera"),
                     "launch", "rs_launch.py"]
                )
            ]
        ),
        launch_arguments={
            "align_depth.enable": "false",
            "depth_enable": "false",
            "spatial_filter.enable": "true",
            "temporal_filter.enable": "true",
            "hole_filling.enable": "true",
            "decimation_filter.enable": "true",
            "pointcloud.enable": "True",
            "pointcloud.ordered_pc": "True",
            "depth_module.profile": "640x480x30",
            "pointcloud.stream_index_filter": "1"
            # 'use_provided_red': 'True',
            # 'new_background_r': TextSubstitution(text=str(colors['background_r']))
        }.items(),
    )

    ld = LaunchDescription()

    ld.add_action(model_cmd)
    ld.add_action(tracker_cmd)
    ld.add_action(device_cmd)
    ld.add_action(enable_cmd)
    ld.add_action(threshold_cmd)
    ld.add_action(input_image_topic_cmd)
    ld.add_action(namespace_cmd)

    ld.add_action(detector_node_cmd)
    # ld.add_action(tracking_node_cmd)
    ld.add_action(debug_node_cmd)
    ld.add_action(rs_launch_cmd)
    return ld
