"""
Example script demonstrating how to access the robot's predefined head_camera
and save rendered images.

This script shows two methods:
1. Using a gymnasium environment (recommended for RL tasks)
2. Using ManiSkillScene directly with agent registration

Usage:
    python custom_robots/scripts/head_camera_example.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend


def method_1_gymnasium_env():
    """
    Method 1: Using gymnasium environment (RECOMMENDED)
    This is the standard way to use cameras in ManiSkill for RL tasks.
    """
    print("\n=== Method 1: Using Gymnasium Environment ===\n")
    
    import gymnasium as gym
    import mani_skill.envs
    # Import your robot registration
    import sys
    sys.path.insert(0, '/workspace/custom_robots')
    import agibot_g1
    
    # Create environment with your robot
    # The robot must have _sensor_configs defined (like AgibotG1OmniPicker)
    env = gym.make(
        "EmptyEnv-v1",  # Use any ManiSkill environment
        robot_uids="agibot_g1_omni_picker",  # Your robot with head_camera
        obs_mode="rgbd",  # Observation mode that includes camera data
        render_mode="rgb_array",  # Enable rendering
        num_envs=1,  # Single environment
        sim_backend="cpu",  # or "gpu" if available
    )
    
    # Reset environment to initialize
    obs, info = env.reset()
    
    print("Available observation keys:", obs.keys())
    
    # Access camera data from observations
    if "sensor_data" in obs:
        sensor_data = obs["sensor_data"]
        print("Available sensors:", sensor_data.keys())
        
        if "head_camera" in sensor_data:
            head_cam_data = sensor_data["head_camera"]
            print("Head camera data keys:", head_cam_data.keys())
            
            # Get RGB image
            if "rgb" in head_cam_data:
                rgb_image = head_cam_data["rgb"]  # Shape: (num_envs, H, W, 3)
                print(f"RGB image shape: {rgb_image.shape}")
                
                # Convert to numpy if it's a tensor
                if hasattr(rgb_image, 'cpu'):
                    rgb_image = rgb_image.cpu().numpy()
                
                # Get first environment's image
                rgb_image = rgb_image[0]  # Shape: (H, W, 3)
                
                # Save image
                plt.figure(figsize=(8, 6))
                plt.imshow(rgb_image)
                plt.title("Head Camera - RGB Image (Method 1)")
                plt.axis('off')
                plt.tight_layout()
                plt.savefig('/workspace/head_camera_method1_rgb.png', dpi=150, bbox_inches='tight')
                print("✓ Saved RGB image to: /workspace/head_camera_method1_rgb.png")
                plt.close()
            
            # Get depth image if available
            if "depth" in head_cam_data:
                depth_image = head_cam_data["depth"]  # Shape: (num_envs, H, W, 1)
                print(f"Depth image shape: {depth_image.shape}")
                
                if hasattr(depth_image, 'cpu'):
                    depth_image = depth_image.cpu().numpy()
                
                depth_image = depth_image[0, :, :, 0]  # Shape: (H, W)
                
                # Save depth visualization
                plt.figure(figsize=(8, 6))
                plt.imshow(depth_image, cmap='viridis')
                plt.title("Head Camera - Depth Image (Method 1)")
                plt.colorbar(label='Depth (meters)')
                plt.axis('off')
                plt.tight_layout()
                plt.savefig('/workspace/head_camera_method1_depth.png', dpi=150, bbox_inches='tight')
                print("✓ Saved depth image to: /workspace/head_camera_method1_depth.png")
                plt.close()
    
    # Run a few steps and capture images
    print("\nRunning simulation steps...")
    images = []
    for step in range(5):
        action = env.action_space.sample()  # Random action
        obs, reward, terminated, truncated, info = env.step(action)
        
        if "sensor_data" in obs and "head_camera" in obs["sensor_data"]:
            rgb = obs["sensor_data"]["head_camera"]["rgb"]
            if hasattr(rgb, 'cpu'):
                rgb = rgb.cpu().numpy()
            images.append(rgb[0])
    
    # Save multiple timesteps
    if len(images) > 0:
        fig, axes = plt.subplots(1, len(images), figsize=(15, 3))
        if len(images) == 1:
            axes = [axes]
        for i, img in enumerate(images):
            axes[i].imshow(img)
            axes[i].set_title(f"Step {i}")
            axes[i].axis('off')
        plt.tight_layout()
        plt.savefig('/workspace/head_camera_method1_sequence.png', dpi=150, bbox_inches='tight')
        print(f"✓ Saved {len(images)} timestep images to: /workspace/head_camera_method1_sequence.png")
        plt.close()
    
    env.close()


def method_2_direct_scene_access():
    """
    Method 2: Direct scene access with agent instantiation
    This is more low-level and useful for custom scenarios.
    """
    print("\n=== Method 2: Direct Scene Access ===\n")
    
    import sapien
    from mani_skill.envs.scene import ManiSkillScene
    from mani_skill.utils.structs.types import SimConfig
    from mani_skill.envs.utils.system.backend import BackendInfo
    import sys
    sys.path.insert(0, '/workspace/custom_robots')
    import agibot_g1
    from mani_skill.agents.registration import REGISTERED_AGENTS
    
    # Create backend with rendering enabled
    backend = BackendInfo(
        device="cpu",
        sim_device="cpu",
        sim_backend="physx",
        render_backend="auto",  # Enable rendering
        render_device="cpu",
    )
    
    # Create scene
    scene = ManiSkillScene(
        sim_config=SimConfig(sim_freq=100, control_freq=20),
        backend=backend,
    )
    
    # Add lighting
    scene.set_ambient_light([0.5, 0.5, 0.5])
    scene.add_directional_light(
        direction=[1, -1, -1],
        color=[1.0, 1.0, 1.0],
        shadow=True,
    )
    
    # Add ground plane
    ground_builder = scene.create_actor_builder()
    ground_builder.add_box_collision(half_size=[10, 10, 0.1])
    ground_builder.add_box_visual(half_size=[10, 10, 0.1], material=[0.5, 0.5, 0.5, 1.0])
    ground = ground_builder.build_static(name="ground")
    ground.set_pose(sapien.Pose(p=[0, 0, -0.1]))
    
    # Instantiate the agent (robot with sensors)
    agent_cls = REGISTERED_AGENTS["agibot_g1_omni_picker"]
    agent = agent_cls(scene, control_freq=20)
    
    print(f"Agent type: {type(agent)}")
    print(f"Agent has robot: {hasattr(agent, 'robot')}")
    print(f"Agent has sensors: {hasattr(agent, 'sensors')}")
    
    # Access the sensors defined in _sensor_configs
    if hasattr(agent, 'sensors'):
        print(f"Number of sensors: {len(agent.sensors)}")
        for sensor_name, sensor in agent.sensors.items():
            print(f"  Sensor: {sensor_name}, Type: {type(sensor)}")
    
    # Access the head_camera directly
    # The camera is in agent.sensors dictionary with uid as key
    if hasattr(agent, 'sensors') and 'head_camera' in agent.sensors:
        head_camera = agent.sensors['head_camera']
        print(f"\n✓ Found head_camera: {head_camera}")
        print(f"  Camera type: {type(head_camera)}")
        print(f"  Camera name: {head_camera.name}")
        
        # Step simulation and render
        scene.step()
        scene.update_render()
        
        # Take picture with the head camera
        head_camera.take_picture()
        
        # Get the image
        rgb_data = head_camera.get_picture("Color")  # Returns list of images
        print(f"  RGB data type: {type(rgb_data)}")
        
        if isinstance(rgb_data, list) and len(rgb_data) > 0:
            rgb_image = rgb_data[0]  # Get first image from list
            print(f"  RGB image shape: {rgb_image.shape}")
            
            # Remove batch dimension if present
            if len(rgb_image.shape) == 4 and rgb_image.shape[0] == 1:
                rgb_image = rgb_image[0]  # (1, H, W, 4) -> (H, W, 4)
            
            # Take only RGB channels (remove alpha)
            rgb_image = rgb_image[..., :3]  # (H, W, 4) -> (H, W, 3)
            
            # Convert to numpy if tensor
            if hasattr(rgb_image, 'cpu'):
                rgb_image = rgb_image.cpu().numpy()
            
            print(f"  Final RGB shape: {rgb_image.shape}")
            print(f"  RGB value range: [{rgb_image.min():.3f}, {rgb_image.max():.3f}]")
            
            # Save the image
            plt.figure(figsize=(8, 6))
            plt.imshow(rgb_image)
            plt.title("Head Camera - Robot View (Method 2)")
            plt.axis('off')
            plt.tight_layout()
            plt.savefig('/workspace/head_camera_method2.png', dpi=150, bbox_inches='tight')
            print("\n✓ Saved head camera image to: /workspace/head_camera_method2.png")
            plt.close()
            
            # Also save depth if available
            depth_data = head_camera.get_picture("Position")  # Get depth from position buffer
            if isinstance(depth_data, list) and len(depth_data) > 0:
                depth_image = depth_data[0]
                if len(depth_image.shape) == 4 and depth_image.shape[0] == 1:
                    depth_image = depth_image[0]
                
                # Extract Z component (depth)
                if depth_image.shape[-1] >= 3:
                    depth_image = depth_image[..., 2]  # Z channel
                
                if hasattr(depth_image, 'cpu'):
                    depth_image = depth_image.cpu().numpy()
                
                plt.figure(figsize=(8, 6))
                plt.imshow(depth_image, cmap='viridis')
                plt.title("Head Camera - Depth (Method 2)")
                plt.colorbar(label='Depth (meters)')
                plt.axis('off')
                plt.tight_layout()
                plt.savefig('/workspace/head_camera_method2_depth.png', dpi=150, bbox_inches='tight')
                print("✓ Saved depth image to: /workspace/head_camera_method2_depth.png")
                plt.close()
    else:
        print("⚠ Warning: head_camera not found in agent sensors!")
        print(f"Available sensors: {list(agent.sensors.keys()) if hasattr(agent, 'sensors') else 'None'}")


def main():
    print("=" * 70)
    print("Head Camera Access Example")
    print("=" * 70)
    
    # try:
    #     print("\n--- Running Method 1: Gymnasium Environment ---")
    #     method_1_gymnasium_env()
    # except Exception as e:
    #     print(f"❌ Method 1 failed: {e}")
    #     import traceback
    #     traceback.print_exc()
    
    try:
        print("\n--- Running Method 2: Direct Scene Access ---")
        method_2_direct_scene_access()
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Done! Check /workspace/ for saved images:")
    print("  - head_camera_method1_rgb.png")
    print("  - head_camera_method1_depth.png")
    print("  - head_camera_method1_sequence.png")
    print("  - head_camera_method2.png")
    print("  - head_camera_method2_depth.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
