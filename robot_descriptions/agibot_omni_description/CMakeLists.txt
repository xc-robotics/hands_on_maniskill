cmake_minimum_required(VERSION 3.8)
project(agibot_omni_description)

find_package(ament_cmake REQUIRED)

install(
		DIRECTORY meshes xacro
		DESTINATION share/${PROJECT_NAME}/
)

ament_package()