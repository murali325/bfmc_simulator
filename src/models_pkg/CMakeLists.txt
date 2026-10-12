cmake_minimum_required(VERSION 3.8)
project(models_pkg)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  cam_birdeye_REC
  camera
  camera_follow
  car_body
  chassis
  crosswalk_sign
  enter_highway_sign
  leave_highway_sign
  oneway_sign
  parking_sign
  pedestrian_object
  priority_sign
  prohibited_sign
  p_alpha_d
  p_alpha_s
  p_beta_d
  p_beta_s
  p_gamma_d
  p_gamma_s
  p_organizing_d
  p_organizing_s
  ramp
  rcCar_assembly
  rcCar_assembly_obstacle
  rcCar_assembly_REC
  roadblock
  roundabout_sign
  separator
  steering_column
  stop_sign
  subassembly
  track
  traffic_light
  wheel_left
  wheel_right
  DESTINATION share/${PROJECT_NAME}/models
)

ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/env-hooks/${PROJECT_NAME}.dsv.in")

ament_package()
