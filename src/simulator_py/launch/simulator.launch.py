#!/usr/bin/env python3
"""
simulator.launch.py
===================
Main ROS 2 launch file for BFMC Simulator.

Launches:
1. Gazebo Sim with the BFMC track world.
2. Spawns the rcCar_assembly model.
3. ROS-Gazebo Bridge (ros_gz_bridge) bridging camera, clock, cmd_vel, and odometry.
4. simulator_node (bridges command JSON and monitors sensors).
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    models_pkg_share = get_package_share_directory('models_pkg')
    sim_pkg_share = get_package_share_directory('sim_pkg')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')

    models_path = os.path.join(models_pkg_share, 'models')
    default_world = os.path.join(sim_pkg_share, 'worlds', 'world.world')
    car_sdf = os.path.join(models_path, 'rcCar_assembly', 'model.sdf')

    # Arguments
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='Path to the world SDF file'
    )

    spawn_x_arg = DeclareLaunchArgument('x', default_value='0.82', description='Car spawn X')
    spawn_y_arg = DeclareLaunchArgument('y', default_value='-14.91', description='Car spawn Y')
    spawn_z_arg = DeclareLaunchArgument('z', default_value='0.05', description='Car spawn Z')
    spawn_yaw_arg = DeclareLaunchArgument('yaw', default_value='1.5707963', description='Car spawn Yaw')
    headless_arg = DeclareLaunchArgument('headless', default_value='false', description='Run headless without GUI')
    spawn_car_arg = DeclareLaunchArgument('spawn_car', default_value='false', description='Spawn car dynamically via ros_gz_sim')

    # Set resource path for Gazebo Sim
    existing_resource_path = os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '')
    resource_path = f"{models_path}:{existing_resource_path}" if existing_resource_path else models_path

    set_ign_resource_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=resource_path
    )
    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=resource_path
    )
    set_ign_render_engine = SetEnvironmentVariable(
        name='IGN_RENDERING_ENGINE_GUESS',
        value='ogre'
    )
    set_gz_render_engine = SetEnvironmentVariable(
        name='GZ_RENDERING_ENGINE_GUESS',
        value='ogre'
    )
    set_ign_ip = SetEnvironmentVariable(
        name='IGN_IP',
        value='127.0.0.1'
    )
    set_gz_ip = SetEnvironmentVariable(
        name='GZ_IP',
        value='127.0.0.1'
    )
    set_qt_plugin_path = SetEnvironmentVariable(
        name='QT_PLUGIN_PATH',
        value='/usr/lib/x86_64-linux-gnu/qt5/plugins'
    )
    set_qt_qpa_platform = SetEnvironmentVariable(
        name='QT_QPA_PLATFORM_PLUGIN_PATH',
        value='/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms'
    )

    # 1. Gazebo Sim (GUI or Headless)
    gz_sim_gui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': ['-r ', LaunchConfiguration('world')],
            'gz_version': '8',
        }.items(),
        condition=UnlessCondition(LaunchConfiguration('headless'))
    )

    gz_sim_headless = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': ['-r -s ', LaunchConfiguration('world')],
            'gz_version': '8',
        }.items(),
        condition=IfCondition(LaunchConfiguration('headless'))
    )

    # 2. Spawn the car
    spawn_car = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-world', 'bfmc_official',
            '-file', car_sdf,
            '-name', 'automobile',
            '-x', LaunchConfiguration('x'),
            '-y', LaunchConfiguration('y'),
            '-z', LaunchConfiguration('z'),
            '-Y', LaunchConfiguration('yaw'),
        ],
        condition=IfCondition(LaunchConfiguration('spawn_car'))
    )

    # 3. ROS-Gazebo Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        arguments=[
            # Camera topics
            '/automobile/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/automobile/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            # Simulation clock
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # Velocity control
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            # Odometry & Pose
            '/model/automobile/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/model/automobile/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            # Joint states
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
        ]
    )

    # 4. Python Simulator Node
    sim_node = Node(
        package='simulator_py',
        executable='simulator_node',
        output='screen',
    )

    return LaunchDescription([
        world_arg,
        spawn_x_arg,
        spawn_y_arg,
        spawn_z_arg,
        spawn_yaw_arg,
        headless_arg,
        spawn_car_arg,
        set_ign_resource_path,
        set_gz_resource_path,
        set_ign_render_engine,
        set_gz_render_engine,
        set_ign_ip,
        set_gz_ip,
        set_qt_plugin_path,
        set_qt_qpa_platform,
        gz_sim_gui,
        gz_sim_headless,
        spawn_car,
        bridge,
        sim_node,
    ])
