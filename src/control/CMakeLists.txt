cmake_minimum_required(VERSION 3.8)
project(control LANGUAGES CXX)

# Provides macros that set build configurations
find_package(ros2_control_cmake REQUIRED)
set_compiler_options()
export_windows_symbols()


##### DEPENDENCY MANAGEMENT #####

# Create lists of dependencies to install
set(HW_COMP_INCLUDE_DEPENDS # Hardware interface specific dependencies
  pluginlib
  hardware_interface
)
set(CONTROLLER_INCLUDE_DEPENDS  # Controller specific dependencies
  pluginlib
  controller_interface
  realtime_tools
  geometry_msgs
)
set(TIBBLE_INCLUDE_DEPENDS  # Multiple/all things need these dependencies
  rclcpp
  rclcpp_lifecycle
  interfaces
)

# Specify the required version of ros2_control
find_package(controller_manager 4.0.0)
if(NOT controller_manager_FOUND)
  message(FATAL_ERROR "ros2_control version 4.0.0 or higher is required.")
endif()

# Find all the dependency lists
find_package(ament_cmake REQUIRED)
foreach(Dependency IN ITEMS ${HW_COMP_INCLUDE_DEPENDS})
  find_package(${Dependency} REQUIRED)
endforeach()
foreach(Dependency IN ITEMS ${CONTROLLER_INCLUDE_DEPENDS})
  find_package(${Dependency} REQUIRED)
endforeach()
foreach(Dependency IN ITEMS ${TIBBLE_INCLUDE_DEPENDS})
  find_package(${Dependency} REQUIRED)
endforeach()


##### COMPILE #####

# Compile all the custom controller and hardware interface stuff
add_library(control SHARED
  src/tibble_controller.cpp
  src/tibble_hardware_interface.cpp
)

target_compile_features(control PUBLIC cxx_std_17)
target_include_directories(control PUBLIC
  $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include/control>

)
target_link_libraries(control PUBLIC
  controller_interface::controller_interface
  hardware_interface::hardware_interface
  pluginlib::pluginlib
  realtime_tools::realtime_tools
  rclcpp::rclcpp
  rclcpp_lifecycle::rclcpp_lifecycle
  geometry_msgs::geometry_msgs
  interfaces::interfaces
)

# Add executables here (.cpp files that are not the controller or hwc)
# More executables would just copy/paste the below three blocks and swap out names
# add_executable(name src/name.cpp)
# ament_target_dependencies(name
#   rclcpp
#   interfaces probably
# )
# target_link_libraries(name control)


##### EXPORT + INSTALL #####

pluginlib_export_plugin_description_file(hardware_interface tibble_hardware_interface.xml)
pluginlib_export_plugin_description_file(controller_interface tibble_controller.xml)

install(
  DIRECTORY include/
  DESTINATION include
)
install(
  DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)
install(
  TARGETS control
  EXPORT export_control
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

ament_export_targets(export_control HAS_LIBRARY_TARGET)
ament_export_dependencies(
  ${HW_COMP_INCLUDE_DEPENDS}
  ${CONTROLLER_INCLUDE_DEPENDS}
  ${TIBBLE_INCLUDE_DEPENDS}
)
ament_package()
