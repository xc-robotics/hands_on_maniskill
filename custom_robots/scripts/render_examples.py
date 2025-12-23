"""
Examples of different rendering modes in ManiSkill:
1. Interactive viewer window
2. RGB image capture
3. Headless rendering
"""

import sapien
from mani_skill.envs.scene import ManiSkillScene
from mani_skill.utils.structs.types import SimConfig
from mani_skill.envs.utils.system.backend import BackendInfo
import time
import numpy as np
from typing import Dict, List
import matplotlib.pyplot as plt

# Choose rendering mode
RENDER_MODE = "viewer"  # Options: "viewer", "rgb_image", "headless"


def move_specific_joints(robot, joint_names: List[str], delta: float = 0.05):
    """Move specific joints by delta in qpos."""
    qpos = robot.get_qpos()
    
    for joint_name in joint_names:
        if joint_name in robot.active_joints_map:
            joint = robot.active_joints_map[joint_name]
            active_idx = joint.active_index[0].item()
            qpos[0, active_idx] += delta
        else:
            print(f"Joint {joint_name} not found in robot.")
    robot.set_qpos(qpos)


def example_viewer_window():
    """
    Example 1: Interactive viewer window
    - Opens a GUI window showing the scene
    - Good for debugging and visualization
    """
    print("=== Example 1: Interactive Viewer Window ===")
    
    backend = BackendInfo(
        device="cpu",
        sim_device="cpu",
        sim_backend="physx",
        render_backend="auto",  # Use auto to select best available renderer
        render_device="cpu",
    )
    
    scene = ManiSkillScene(
        sim_config=SimConfig(sim_freq=240, control_freq=240),
        backend=backend,
    )
    
    # Load robot
    loader = scene.create_urdf_loader()
    loader.fix_root_link = True
    robot = loader.load("robot_descriptions/agibot_g1_with_gripper_description/agibot_g1_with_120s.urdf")
    
    # Add a camera to the scene for viewing
    camera = scene.add_camera(
        name="viewer_camera",
        pose=sapien.Pose(p=[2, 0, 1], q=[0.924, 0, 0.383, 0]),  # Position and orientation
        width=640,
        height=480,
        fovy=1.0,
        near=0.01,
        far=10,
    )
    
    # Create viewer
    # ManiSkillScene wraps SAPIEN scene - access it via scene.px
    sapien_scene = scene.px
    viewer = sapien_scene.create_viewer()
    viewer.set_camera_pose(camera.px.pose)  # Use underlying SAPIEN camera pose
    
    # Define joints to move
    active_joints_to_move = [
        'left_joint1', 'left_joint2', 'left_joint3', 'left_joint4',
        'left_joint5', 'left_joint6', 'left_joint7',
    ]
    
    print("Viewer window opened. Moving robot joints...")
    print("Close the viewer window to exit.")
    
    # Simulation loop
    dt = 1/60.0  # Lower frequency for viewer
    step = 0
    while not viewer.closed:
        if step < 300:
            move_specific_joints(robot, active_joints_to_move, delta=0.01)
        
        scene.step()
        scene.update_render()
        viewer.render()
        
        step += 1
        time.sleep(dt)
    
    print("Viewer closed.")


def example_rgb_image_capture():
    """
    Example 2: Capture RGB images from cameras
    - Renders to images without GUI
    - Can capture multiple cameras
    - Good for data collection
    """
    print("=== Example 2: RGB Image Capture ===")
    
    backend = BackendInfo(
        device="cpu",
        sim_device="cpu",
        sim_backend="physx",
        render_backend="auto",  # Need renderer for images
        render_device="cpu",
    )
    
    scene = ManiSkillScene(
        sim_config=SimConfig(sim_freq=240, control_freq=240),
        backend=backend,
    )
    
    # Load robot
    loader = scene.create_urdf_loader()
    loader.fix_root_link = True
    robot = loader.load("robot_descriptions/agibot_g1_with_gripper_description/agibot_g1_with_120s.urdf")
    
    # Add cameras at different positions
    camera_front = scene.add_camera(
        name="front_camera",
        pose=sapien.Pose(p=[2, 0, 1], q=[0.924, 0, 0.383, 0]),
        width=640,
        height=480,
        fovy=1.0,
        near=0.01,
        far=10,
    )
    
    camera_side = scene.add_camera(
        name="side_camera",
        pose=sapien.Pose(p=[0, 2, 1], q=[0.924, 0, 0, 0.383]),
        width=640,
        height=480,
        fovy=1.0,
        near=0.01,
        far=10,
    )
    
    # Define joints to move
    active_joints_to_move = [
        'left_joint1', 'left_joint2', 'left_joint3', 'left_joint4',
        'left_joint5', 'left_joint6', 'left_joint7',
    ]
    
    print("Capturing images at different timesteps...")
    
    # Simulation loop - capture images at intervals
    dt = 1/240.0
    captured_images = []
    
    for step in range(300):
        if step < 200:
            move_specific_joints(robot, active_joints_to_move, delta=0.01)
        
        scene.step()
        scene.update_render()
        
        # Capture images every 50 steps
        if step % 50 == 0:
            # Take picture from front camera
            camera_front.take_picture()
            rgb_front = camera_front.get_picture("Color")[..., :3]  # Get RGB, drop alpha
            
            # Take picture from side camera
            camera_side.take_picture()
            rgb_side = camera_side.get_picture("Color")[..., :3]
            
            # Convert from tensor to numpy if needed
            if hasattr(rgb_front, 'cpu'):
                rgb_front = rgb_front.cpu().numpy()
            if hasattr(rgb_side, 'cpu'):
                rgb_side = rgb_side.cpu().numpy()
            
            captured_images.append({
                'step': step,
                'front': rgb_front[0],  # Remove batch dimension
                'side': rgb_side[0]
            })
            
            print(f"Step {step}: Captured images - Front shape: {rgb_front.shape}, Side shape: {rgb_side.shape}")
    
    # Display captured images
    print(f"\nTotal images captured: {len(captured_images)}")
    
    # Show first and last frames
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # First frame
    axes[0, 0].imshow(captured_images[0]['front'])
    axes[0, 0].set_title(f"Front Camera - Step {captured_images[0]['step']}")
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(captured_images[0]['side'])
    axes[0, 1].set_title(f"Side Camera - Step {captured_images[0]['step']}")
    axes[0, 1].axis('off')
    
    # Last frame
    axes[1, 0].imshow(captured_images[-1]['front'])
    axes[1, 0].set_title(f"Front Camera - Step {captured_images[-1]['step']}")
    axes[1, 0].axis('off')
    
    axes[1, 1].imshow(captured_images[-1]['side'])
    axes[1, 1].set_title(f"Side Camera - Step {captured_images[-1]['step']}")
    axes[1, 1].axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/captured_images.png')
    print("Images saved to: /workspace/captured_images.png")
    plt.show()


def example_headless():
    """
    Example 3: Headless mode (no rendering)
    - Fastest mode
    - Good for training/simulation without visualization
    """
    print("=== Example 3: Headless Mode (No Rendering) ===")
    
    backend = BackendInfo(
        device="cpu",
        sim_device="cpu",
        sim_backend="physx",
        render_backend="none",  # No rendering
        render_device=None,
    )
    
    scene = ManiSkillScene(
        sim_config=SimConfig(sim_freq=240, control_freq=240),
        backend=backend,
    )
    
    # Load robot
    loader = scene.create_urdf_loader()
    loader.fix_root_link = True
    robot = loader.load("robot_descriptions/agibot_g1_with_gripper_description/agibot_g1_with_120s.urdf")
    
    # Define joints to move
    active_joints_to_move = [
        'left_joint1', 'left_joint2', 'left_joint3', 'left_joint4',
        'left_joint5', 'left_joint6', 'left_joint7',
    ]
    
    print("Running headless simulation (no rendering)...")
    
    # Fast simulation loop
    for step in range(300):
        if step < 200:
            move_specific_joints(robot, active_joints_to_move, delta=0.01)
        
        scene.step()
        
        if step % 100 == 0:
            qpos = robot.get_qpos()
            print(f"Step {step}: Joint positions mean = {qpos.mean().item():.4f}")
    
    print("Headless simulation completed.")


def main():
    print(f"Selected rendering mode: {RENDER_MODE}\n")
    
    if RENDER_MODE == "viewer":
        example_viewer_window()
    elif RENDER_MODE == "rgb_image":
        example_rgb_image_capture()
    elif RENDER_MODE == "headless":
        example_headless()
    else:
        print(f"Unknown render mode: {RENDER_MODE}")
        print("Available modes: 'viewer', 'rgb_image', 'headless'")


if __name__ == "__main__":
    main()
