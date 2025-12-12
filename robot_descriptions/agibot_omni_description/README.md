# Agibot Omni Gripper&Hand Description

This package contains the URDF and related files for the Agibot Omni Gripper and Hands. Origin files could be found at [Agibot OpenSource](https://www.zhiyuan-robot.com/DOCS/PM/X1).

## Build

```bash
cd ~/ros2_ws
colcon build --packages-up-to agibot_omni_description --symlink-install
```

## Visualize

* Omni Picker
  ```bash
  source ~/ros2_ws/install/setup.bash
  ros2 launch robot_common_launch gripper.launch.py gripper:=agibot_omni
  ```
  ![ag2f90c](../.images/omni_picker.png)