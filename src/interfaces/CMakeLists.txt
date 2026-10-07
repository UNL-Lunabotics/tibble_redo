cmake_minimum_required(VERSION 3.8)
project(interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

# Add new messages or services here
set(msg_files
  "msg/ManualCommands.msg"
  "msg/StateMachineCommands.msg"
  "msg/TibbleCommand.msg"
)
set(srv_files
  "srv/ChangeState.srv"
)

rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
  ${srv_files}
  # Dependencies for any messages or services would go here if there were any
  DEPENDENCIES std_msgs
)

ament_package()
