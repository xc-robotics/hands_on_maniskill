import sapien
import numpy as np
from mani_skill.agents.base_agent import BaseAgent, Keyframe
from mani_skill.agents.controllers import *
from mani_skill.agents.registration import register_agent

@register_agent()
class AgibotG1OmniPicker(BaseAgent):
    uid="agibot_g1_omni_picker"
    # urdf_path="robot_descriptions/agibot_g1_description/urdf/agibot_g1_omni-picker.urdf"
    urdf_path="robot_descriptions/agibot_g1_with_gripper_description/agibot_g1_with_omnipicker.urdf"
    fix_root_link=True
    
@register_agent() 
class AgibotG1120s(BaseAgent):
    uid="agibot_g1_120s"
    urdf_path="robot_descriptions/agibot_g1_with_gripper_description/agibot_g1_with_120s.urdf"
    fix_root_link=True
    
# import mani_skill.envs
# import gymnasium as gym
# env = gym.make("EmptyEnv-v1", robot_uids="agibot_g1")