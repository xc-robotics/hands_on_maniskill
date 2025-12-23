import os
# Use CPU rendering to avoid Vulkan/GPU issues
os.environ['MUJOCO_GL'] = 'egl'  # or 'osmesa' for pure CPU rendering
os.environ['SAPIEN_RENDERER'] = 'cpu'

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='sapien')

import mani_skill
import gymnasium as gym

env = gym.make("PickCube-v1",
                obs_mode="rgbd",
                control_mode="pd_joint_pos")
info = env.reset()
for _ in range(200):
    action = env.action_space.sample()
    obs, reward, terminated, truncated,  info = env.step(action)
env.close()