"""
Simple example: Access robot's head_camera and save image

This is the minimal code to get and save an image from the head_camera.
"""

import gymnasium as gym
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, '/workspace/custom_robots')

# Import robot registration
import agibot_g1
import mani_skill.envs

# Create environment with robot that has head_camera
env = gym.make(
    "PickCube-v1",  # Use PickCube environment
    robot_uids="agibot_g1_omni_picker",  # Robot with head_camera
    obs_mode="rgbd",  # Include camera data
    render_mode="rgb_array",
    num_envs=1,
    sim_backend="cpu",
)

# Reset to initialize
obs, info = env.reset()

# Access head_camera RGB image
rgb_image = obs["sensor_data"]["head_camera"]["rgb"][0]  # [0] to get first env

# Convert to numpy if needed
if hasattr(rgb_image, 'cpu'):
    rgb_image = rgb_image.cpu().numpy()

# Save image
plt.figure(figsize=(8, 6))
plt.imshow(rgb_image)
plt.title("Head Camera View")
plt.axis('off')
plt.savefig('/workspace/head_camera_simple.png', bbox_inches='tight', dpi=150)
print(f"✓ Saved image: /workspace/head_camera_simple.png")
print(f"  Image shape: {rgb_image.shape}")
print(f"  Value range: [{rgb_image.min():.3f}, {rgb_image.max():.3f}]")

env.close()
