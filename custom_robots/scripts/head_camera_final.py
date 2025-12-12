"""
WORKING EXAMPLE: Access robot's head_camera and save image

This example shows the correct way to access the head_camera mounted on the robot.
Since we're using direct scene manipulation (not gym environment), we need to 
manually add a camera mounted to the robot's head_camera link.
"""

import sapien
from mani_skill.envs.scene import ManiSkillScene
from mani_skill.utils.structs.types import SimConfig
from mani_skill.envs.utils.system.backend import BackendInfo
import matplotlib.pyplot as plt
import numpy as np

print("=" * 70)
print("Robot Head Camera Example - Direct Scene Access")
print("=" * 70)

print("\n1. Creating scene with rendering enabled...")

# Create backend with rendering
backend = BackendInfo(
    device="cpu",
    sim_device="cpu",
    sim_backend="physx",
    render_backend="auto",
    render_device="cpu",
)

# Create scene
scene = ManiSkillScene(
    sim_config=SimConfig(sim_freq=100, control_freq=20),
    backend=backend,
)

print("2. Adding lighting to scene...")
# Add lighting (important for rendering!)
scene.set_ambient_light([0.6, 0.6, 0.6])
scene.add_directional_light(
    direction=[1, -1, -1],
    color=[1.0, 1.0, 1.0],
    shadow=True,
)
scene.add_point_light(
    position=[1, 1, 2],
    color=[0.8, 0.8, 0.8],
)

# Add ground plane for visual reference
ground_builder = scene.create_actor_builder()
ground_builder.add_box_collision(half_size=[10, 10, 0.1])
ground_builder.add_box_visual(half_size=[10, 10, 0.1], material=[0.7, 0.7, 0.7, 1.0])
ground = ground_builder.build_static(name="ground")
ground.set_pose(sapien.Pose(p=[0, 0, -0.1]))

# Add a colorful cube for the camera to see
print("3. Adding objects to scene...")
cube_builder = scene.create_actor_builder()
cube_builder.add_box_collision(half_size=[0.1, 0.1, 0.1])
cube_builder.add_box_visual(half_size=[0.1, 0.1, 0.1], material=[1.0, 0.2, 0.2, 1.0])  # Red cube
cube = cube_builder.build_kinematic(name="cube")
cube.set_pose(sapien.Pose(p=[0.5, 0, 0.6]))  # In front of robot at head height

print("4. Loading robot URDF...")
# Load robot URDF
loader = scene.create_urdf_loader()
loader.fix_root_link = True
robot = loader.load("robot_descriptions/agibot_g1_with_gripper_description/agibot_g1_with_omnipicker.urdf")

print(f"   Robot loaded: {robot.name}")
print(f"   Robot has {len(robot.get_links())} links")

# Find the head_camera link
head_camera_link = None
for link in robot.get_links():
    if link.name == "head_camera":
        head_camera_link = link
        print(f"   ✓ Found head_camera link: {link.name}")
        break

if head_camera_link is None:
    print("   ⚠ Warning: head_camera link not found!")
    print(f"   Available links: {[link.name for link in robot.get_links()]}")
    exit(1)

print("5. Adding camera mounted on head_camera link...")
# Create a camera mounted on the head_camera link
# The camera configuration matches what's in agibot_g1.py _sensor_configs
head_camera = scene.add_camera(
    name="head_camera",
    mount=head_camera_link,  # Mount to the head_camera link
    # +90 degree around Y axis
    pose=sapien.Pose(p=[0, 0, 0], q=[0.707, 0, 0.707, 0]),  # Identity pose relative to link
    width=1280,  # Higher resolution for better visualization
    height=720,
    fovy=np.pi / 2,  # 90 degree field of view
    near=0.01,
    far=100,
)

rpy = [0, -1.117, 1.5708] # Ref: https://github.com/fiveages-sim/robot_descriptions/blob/main/humanoid/Agibot/agibot_g1_description/xacro/omnipicker_camera_stand.xacro
# convert rpy to quaternion
def rpy_to_quat(roll, pitch, yaw):
    cy = np.cos(yaw * 0.5)
    sy = np.sin(yaw * 0.5)
    cp = np.cos(pitch * 0.5)
    sp = np.sin(pitch * 0.5)
    cr = np.cos(roll * 0.5)
    sr = np.sin(roll * 0.5)

    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy

    return np.array([qw, qx, qy, qz])

    
def get_link_by_name(robot, link_name):
    for link in robot.get_links():
        if link.name == link_name:
            return link
    return None

left_wrist_camera = scene.add_camera(
    name="left_wrist_camera",
    mount=get_link_by_name(robot, "left_camera_stand"),  # Mount to the left_wrist_camera link
    pose=sapien.Pose(p=[0, -0.07754, 0.028618], 
                     q=rpy_to_quat(*rpy)
                    #  q=[1, 0, 0, 0]
                     ),  # Identity pose relative to link
    width=640,
    height=480,
    fovy=np.pi / 2,
    near=0.01,
    far=100,
)

right_wrist_camera = scene.add_camera(
    name="right_wrist_camera",
    mount=get_link_by_name(robot, "right_camera_stand"),  # Mount to the right_wrist_camera link
    pose=sapien.Pose(p=[0, -0.07754, 0.028618], q=rpy_to_quat(*rpy)),  # Identity pose relative to link
    width=640,
    height=480,
    fovy=np.pi / 2,
    near=0.01,
    far=100,
)

print(f"   ✓ Camera added: {head_camera.name}")
print(f"   Camera type: {type(head_camera)}")
print(f"   ✓ Camera added: {left_wrist_camera.name}")
print(f"   Camera type: {type(left_wrist_camera)}")
print(f"   ✓ Camera added: {right_wrist_camera.name}")
print(f"   Camera type: {type(right_wrist_camera)}")

print("6. Stepping simulation and rendering...")
# Step simulation
scene.step()
scene.update_render()

print("7. Capturing image from head_camera...")
# Capture image
head_camera.take_picture()

# Get RGB image
rgb_data = head_camera.get_picture("Color")
print(f"   RGB data type: {type(rgb_data)}")

if isinstance(rgb_data, list) and len(rgb_data) > 0:
    rgb_image = rgb_data[0]
    print(f"   Raw image shape: {rgb_image.shape}")
    
    # Process image
    if len(rgb_image.shape) == 4 and rgb_image.shape[0] == 1:
        rgb_image = rgb_image[0]  # Remove batch dimension: (1, H, W, 4) -> (H, W, 4)
    
    rgb_image = rgb_image[..., :3]  # Take RGB only: (H, W, 4) -> (H, W, 3)
    
    # Convert to numpy if tensor
    if hasattr(rgb_image, 'cpu'):
        rgb_image = rgb_image.cpu().numpy()
    
    print(f"   Processed image shape: {rgb_image.shape}")
    print(f"   Value range: [{rgb_image.min():.3f}, {rgb_image.max():.3f}]")
    print(f"   Mean value: {rgb_image.mean():.3f}")
    
    # Check if image has content
    if rgb_image.mean() > 0.01:
        print("   ✓ Image has content!")
    else:
        print("   ⚠ Image might be black")
    
    # Save image
    print("8. Saving image...")
    plt.figure(figsize=(10, 7.5))
    plt.imshow(rgb_image)
    plt.title("Head Camera View - Robot's Perspective", fontsize=14, fontweight='bold')
    plt.xlabel(f"Resolution: {rgb_image.shape[1]}x{rgb_image.shape[0]}", fontsize=10)
    plt.axis('off')
    plt.tight_layout()
    output_path = '/workspace/head_camera_final.png'
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()
    
    print(f"\n{'='*70}")
    print(f"✓✓ SUCCESS! Image saved to: {output_path}")
    print(f"{'='*70}\n")
    
    # Also try to get depth
    print("9. (Optional) Capturing depth image...")
    try:
        position_data = head_camera.get_picture("Position")
        if isinstance(position_data, list) and len(position_data) > 0:
            depth_image = position_data[0]
            if len(depth_image.shape) == 4 and depth_image.shape[0] == 1:
                depth_image = depth_image[0]
            
            # Extract Z component (depth) from position
            if depth_image.shape[-1] >= 3:
                depth_image = depth_image[..., 2]  # Z channel
            
            if hasattr(depth_image, 'cpu'):
                depth_image = depth_image.cpu().numpy()
            
            print(f"   Depth image shape: {depth_image.shape}")
            print(f"   Depth range: [{depth_image.min():.3f}, {depth_image.max():.3f}] meters")
            
            # Save depth visualization
            plt.figure(figsize=(10, 7.5))
            im = plt.imshow(depth_image, cmap='viridis')
            plt.title("Head Camera - Depth Map", fontsize=14, fontweight='bold')
            plt.colorbar(im, label='Depth (meters)')
            plt.axis('off')
            plt.tight_layout()
            depth_output_path = '/workspace/head_camera_depth.png'
            plt.savefig(depth_output_path, bbox_inches='tight', dpi=150)
            plt.close()
            print(f"   ✓ Depth image saved to: {depth_output_path}")
    except Exception as e:
        print(f"   Depth capture failed: {e}")
    
else:
    print("   ⚠ No RGB data returned from camera!")

# Get wrist camera images as well
for wrist_camera, name in [(left_wrist_camera, "Left Wrist Camera"), (right_wrist_camera, "Right Wrist Camera")]:
    print(f"7. Capturing image from {name}...")
    wrist_camera.take_picture()
    rgb_data = wrist_camera.get_picture("Color")
    print(f"   RGB data type: {type(rgb_data)}")

    if isinstance(rgb_data, list) and len(rgb_data) > 0:
        rgb_image = rgb_data[0]
        print(f"   Raw image shape: {rgb_image.shape}")
        
        # Process image
        if len(rgb_image.shape) == 4 and rgb_image.shape[0] == 1:
            rgb_image = rgb_image[0]  # Remove batch dimension: (1, H, W, 4) -> (H, W, 4)
        
        rgb_image = rgb_image[..., :3]  # Take RGB only: (H, W, 4) -> (H, W, 3)
        
        # Convert to numpy if tensor
        if hasattr(rgb_image, 'cpu'):
            rgb_image = rgb_image.cpu().numpy()
        
        print(f"   Processed image shape: {rgb_image.shape}")
        print(f"   Value range: [{rgb_image.min():.3f}, {rgb_image.max():.3f}]")
        print(f"   Mean value: {rgb_image.mean():.3f}")
        
        # Check if image has content
        if rgb_image.mean() > 0.01:
            print("   ✓ Image has content!")
        else:
            print("   ⚠ Image might be black")
        
        # Save image
        print("8. Saving image...")
        plt.figure(figsize=(10, 7.5))
        plt.imshow(rgb_image)
        plt.title(f"{name} View - Robot's Perspective", fontsize=14, fontweight='bold')
        plt.xlabel(f"Resolution: {rgb_image.shape[1]}x{rgb_image.shape[0]}", fontsize=10)
        plt.axis('off')
        plt.tight_layout()
        output_path = f'/workspace/{name.lower().replace(" ", "_")}_final.png'
        plt.savefig(output_path, bbox_inches='tight', dpi=150)
        plt.close()
        
        print(f"\n{'='*70}")
        print(f"✓✓ SUCCESS! Image saved to: {output_path}")
        print(f"{'='*70}\n")
        
    else:
        print("   ⚠ No RGB data returned from camera!")

print("\nDone!")
