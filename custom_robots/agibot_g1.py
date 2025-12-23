import sapien
import numpy as np
from mani_skill.agents.base_agent import BaseAgent, Keyframe
from mani_skill.agents.controllers import *
from mani_skill.agents.registration import register_agent
from mani_skill.sensors.camera import CameraConfig

K_D455_1280x720 = np.array([
    [925.0,   0.0, 640.0],
    [  0.0, 925.0, 360.0],
    [  0.0,   0.0,   1.0],
    ], dtype=np.float32)
    
@register_agent()
class AgibotG1OmniPicker(BaseAgent):
    uid="agibot_g1_omni_picker"
    # urdf_path="robot_descriptions/agibot_g1_description/urdf/agibot_g1_omni-picker.urdf"
    urdf_path="robot_descriptions/manipulation/Agibot/agibot_g1_with_gripper_description/agibot_g1_with_omnipicker.urdf"
    fix_root_link=True
        
    @property
    def _sensor_configs(self):
        return [
            CameraConfig(
                uid="head_camera",
                pose=sapien.Pose(p=[0, 0, 0], q=[0.707, 0, 0.707, 0]),
                width=1280,
                height=720,
                intrinsic=K_D455_1280x720,
                # fov=np.pi / 2,
                near=0.01,
                far=10,
                mount=self.robot.links_map["head_camera"],
            )
        ]
    
@register_agent() 
class AgibotG1120s(BaseAgent):
    uid="agibot_g1_120s"
    urdf_path="robot_descriptions/agibot_g1_with_gripper_description/agibot_g1_with_120s.urdf"
    fix_root_link=True
    
# import mani_skill.envs
# import gymnasium as gym
# env = gym.make("EmptyEnv-v1", robot_uids="agibot_g1")
