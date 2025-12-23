"""
Example: Interactive Viewer with Gymnasium Environment

This script shows how to use an interactive viewer window with ManiSkill.
The key is to use a gymnasium environment, not ManiSkillScene directly.
"""

import gymnasium as gym
import numpy as np
import mani_skill.envs  # Required to register environments
from mani_skill.envs.sapien_env import BaseEnv

# Import your custom robot
import sys
sys.path.append('/workspace/custom_robots')
import agibot_g1

def main():
    # Create environment with human render mode for interactive viewer
    env = gym.make(
        "PushCube-v1",  # Use a simple task environment
        robot_uids="panda",  # Use built-in Panda robot first to test
        obs_mode="none",
        control_mode="pd_joint_pos",
        render_mode="human",  # This enables the interactive viewer!
        sim_backend="cpu",  # or "physx_cuda" for GPU
    )
    
    print("Environment created. Rendering viewer...")
    
    # Reset environment
    obs, info = env.reset()
    
    # Get the viewer by rendering
    viewer = env.render()
    print("Viewer window opened!")
    print("Controls:")
    print("  - Click and drag to rotate view")
    print("  - Right-click drag to pan")
    print("  - Scroll to zoom")
    print("  - Press 'P' to pause")
    print("  - Close window to exit")
    
    # Define which joints to move
    # You can get joint info from env.agent.robot
    print("\nRobot joints:", list(env.agent.robot.active_joints_map.keys()))
    
    # Get current joint positions
    qpos = env.agent.robot.get_qpos()[0]  # Remove batch dim
    if hasattr(qpos, 'cpu'):
        qpos = qpos.cpu().numpy()
    print(f"Initial joint positions: {qpos}")
    
    # Get action space info
    print(f"Action space: {env.action_space}")
    print(f"Action space shape: {env.action_space.shape}")
    
    # Simple control loop - oscillate joints
    step = 0
    max_steps = 500
    
    while step < max_steps:
        # Check if viewer is closed
        if viewer and viewer.closed:
            print("Viewer closed by user.")
            break
        
        # Create an action - use action space to sample or create proper shape
        # For pd_joint_pos, action is the target joint positions for controllable joints
        action = env.action_space.sample()  # Get properly shaped action
        
        # Modify action to oscillate joints
        amplitude = 0.3
        frequency = 0.01
        for i in range(len(action)):
            action[i] = amplitude * np.sin(frequency * step + i)
        
        # Step the environment
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Render the viewer
        viewer = env.render()
        
        if step % 50 == 0:
            print(f"Step {step}/{max_steps}")
        
        step += 1
    
    print("\nClosing environment...")
    env.close()
    print("Done!")

if __name__ == "__main__":
    main()
