# BFMC Simulator (ROS 2 Jazzy & Gazebo Harmonic)

A lightweight, modern ROS 2 workspace for the **Bosch Future Mobility Challenge (BFMC)** simulator. Built for **ROS 2 Jazzy** and **Gazebo Harmonic (v8)**, running on **Ubuntu 24.04 LTS**.

This workspace provides:
- The complete competition **Track** model with high-resolution textured quad mesh.
- The **1:10 Autonomous Car** model (`automobile`) equipped with Ackermann steering, camera sensor, and odometry.
- Unified launch system spawning the track, vehicle, ROS-Gazebo bridge, and vehicle controller.
- Standard ROS 2 topic interfaces for camera frames, control commands, and telemetry.

---

## Software Requirements & Versions

All components have been tested and verified under the following software stack:

| Component | Software / Package | Exact Version | Description |
| :--- | :--- | :--- | :--- |
| **Operating System** | Ubuntu Linux | **24.04 LTS (Noble Numbat)** | 64-bit (`x86_64`), Linux Kernel 6.8+ |
| **Robotics Framework** | ROS 2 | **Jazzy Jalisco** | `ros-jazzy-desktop` / `ros-jazzy-desktop-full` |
| **Simulator** | Gazebo Sim | **Harmonic 8.15.0** | `gz sim` (`ros-jazzy-gz-sim-vendor`) |
| **Simulator Bridge** | `ros_gz` | **1.0.24** | `ros_gz_bridge`, `ros_gz_sim`, `ros_gz_image` |
| **Programming Language** | Python | **3.12.3** | Standard Python 3 interpreter |
| **Build Tools** | CMake | **3.28.3** | C++ build system |
| | colcon | **0.21.2+** | ROS 2 workspace build tool (`colcon-core`) |
| | ament_cmake / ament_python | **Jazzy** | ROS 2 build type backends |
| **Graphics & Vision** | OpenCV | **4.9.0** | Image processing library (`python3-opencv` / `cv_bridge`) |
| | NumPy | **1.26.4** | Numerical computing |
| | OGRE Rendering Engine | **OGRE / OGRE-Next** | Native Gazebo Sim render engine |

---

## Required Dependencies Installation

If setting up on a fresh machine running **Ubuntu 24.04 LTS**, install the necessary prerequisites:

```bash
# 1. Update system package index
sudo apt update && sudo apt upgrade -y

# 2. Install ROS 2 Jazzy Desktop
sudo apt install -y ros-jazzy-desktop ros-jazzy-desktop-full

# 3. Install Gazebo Harmonic and ROS-Gazebo Bridge
sudo apt install -y \
  ros-jazzy-ros-gz \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-ros-gz-image \
  ros-jazzy-ros-gz-interfaces \
  ros-jazzy-cv-bridge

# 4. Install Colcon and Python dependencies
sudo apt install -y \
  python3-colcon-common-extensions \
  python3-pip \
  python3-opencv \
  python3-numpy
```

---

## Workspace Structure

```text
Simulator/
├── src/
│   ├── models_pkg/        # Track, rcCar_assembly, sensors, and road signs
│   │   ├── rcCar_assembly/    # 1:10 scale BFMC car with Ackermann & camera
│   │   ├── track/             # Competition track with mesh and textures
│   │   └── env-hooks/         # Auto-configures GZ_SIM_RESOURCE_PATH
│   ├── sim_pkg/           # Simulation worlds
│   │   └── worlds/
│   │       ├── world.world                    # Base world (track + car)
│   │       └── world_with_separators.world    # World with track separators
│   └── simulator_py/      # Python node & ROS 2 launcher
│       ├── launch/
│       │   └── simulator.launch.py   # Main launch file (Gazebo + Bridge + Node)
│       └── simulator_py/
│           └── simulator_node.py     # Vehicle command handler & feedback publisher
├── build/                 # Colcon build output
├── install/               # Colcon install directory
└── README.md              # Project documentation
```

---

## Build Instructions

Clone and build the workspace using `colcon`:

```bash
# Source ROS 2 Jazzy
source /opt/ros/jazzy/setup.bash

# Navigate to workspace root
cd ~/bfmc/Simulator

# Build all packages with symlink install
colcon build --symlink-install

# Source the workspace environment
source install/setup.bash
```

---

## Running the Simulator

### 1. Launch with Gazebo GUI (Default)
Starts the 3D Gazebo simulator, loads both track and car, launches the bridge, and initializes the ROS 2 node:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch simulator_py simulator.launch.py
```

### 2. Launch in Headless Mode (Server Only)
Runs without the GUI window for lower resource consumption or running on headless compute servers:

```bash
ros2 launch simulator_py simulator.launch.py headless:=true
```

---

## ROS 2 Topics Interface

Once launched, the following topics are active:

| Topic | Type | Direction | Description |
| :--- | :--- | :--- | :--- |
| `/automobile/image_raw` | `sensor_msgs/msg/Image` | Publish (Car $\to$ ROS) | Camera video stream (640×480 RGB8 at ~30 Hz) |
| `/automobile/camera_info` | `sensor_msgs/msg/CameraInfo` | Publish (Car $\to$ ROS) | Intrinsic calibration parameters |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Subscribe (ROS $\to$ Car) | Ackermann velocity & steering angle |
| `/model/automobile/odometry` | `nav_msgs/msg/Odometry` | Publish (Car $\to$ ROS) | Vehicle ground-truth pose & velocity |
| `/model/automobile/tf` | `tf2_msgs/msg/TFMessage` | Publish (Car $\to$ ROS) | Coordinate transformations |
| `/joint_states` | `sensor_msgs/msg/JointState` | Publish (Car $\to$ ROS) | Wheel and steering joint states |
| `/clock` | `rosgraph_msgs/msg/Clock` | Publish (Sim $\to$ ROS) | Simulation clock |
| `/automobile/command` | `std_msgs/msg/String` | Subscribe | BFMC JSON command interface |
| `/automobile/feedback` | `std_msgs/msg/String` | Publish | BFMC status feedback |

---

## Verification & Useful Commands

### Check Active Topics
```bash
ros2 topic list -t
```

### View Live Camera Stream
```bash
ros2 run rqt_image_view rqt_image_view /automobile/image_raw
```

### Monitor Camera Frame Rate
```bash
ros2 topic hz /automobile/image_raw
```

### Drive the Car Manually
Publish a Twist message to drive forward at 0.5 m/s:
```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.0}}" -r 20
```

Publish a steering command (turn left while moving forward):
```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}" -r 20
```

---

## Troubleshooting

- **Qt Plugin Crash (`Could not load the Qt platform plugin "xcb"`):**
  If pip-installed packages (such as `opencv-python`) introduce conflicting Qt libraries, the launch file automatically sets:
  ```bash
  export QT_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins
  export QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms
  ```
- **Local Network Interface Issues (`zeth` / Docker):**
  The launch file automatically binds `GZ_IP=127.0.0.1` and `IGN_IP=127.0.0.1` to ensure Gazebo transport uses the local loopback interface.
