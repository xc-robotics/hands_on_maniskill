import sapien
from mani_skill.envs.scene import ManiSkillScene
from mani_skill.utils.structs.types import SimConfig
from mani_skill.envs.utils.system.backend import BackendInfo

import time
import numpy as np
from typing import Dict, List
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Rendering options
RENDER_ON = True
USE_VIEWER = False  # ManiSkillScene doesn't support interactive viewer directly
                    # Set to False and use RGB capture, or use gymnasium env for viewer
SAVE_IMAGES = True  # Save RGB images if rendering

def move_specific_joints(
    robot,
    joint_names: List[str],
    delta: float = 0.05,
):
    """Move specific joints by delta in qpos."""
    qpos = robot.get_qpos()
    
    for joint_name in joint_names:
        if joint_name in robot.active_joints_map:
            # Get the joint object
            joint = robot.active_joints_map[joint_name]
            # Get the active index (qpos index) for this joint
            active_idx = joint.active_index[0].item()  # Convert tensor to int
            # Update qpos at the active index (qpos is 2D: [batch_size, num_joints])
            qpos[0, active_idx] += delta
        else:
            print(f"Joint {joint_name} not found in robot.")
    robot.set_qpos(qpos)
    
def print_joint_info(robot, joint_names: List[str]):
    """Print joint info for specific joints."""
    qpos = robot.get_qpos()
    qvel = robot.get_qvel()
    
    for joint_name in joint_names:
        if joint_name in robot.active_joints_map:
            # Get the joint object
            joint = robot.active_joints_map[joint_name]
            # Get the active index (qpos index) for this joint
            active_idx = joint.active_index[0].item()  # Convert tensor to int
            # Access qpos/qvel (they are 2D: [batch_size, num_joints])
            print(f"Joint: {joint_name}, QPos: {qpos[0, active_idx]}, QVel: {qvel[0, active_idx]}")
        else:
            print(f"Joint {joint_name} not found in robot.")
    


def main():
    # 1. Create a backend and ManiSkillScene
    backend = BackendInfo(
        device="cpu",           # torch device
        sim_device="cpu",       # physics device
        sim_backend="physx",    # sapien backend
        render_backend="none" if not RENDER_ON else "auto",  # renderer backend
        render_device="cpu" if RENDER_ON else None,
    )
    
    scene = ManiSkillScene(
        sim_config=SimConfig(sim_freq=240, control_freq=240),
        backend=backend,
    )
    
    # 2. Load your URDF
    loader = scene.create_urdf_loader()
    loader.fix_root_link = True  # Fix the base of the robot
    robot = loader.load("robot_descriptions/agibot_g1_with_gripper_description/agibot_g1_with_120s.urdf")
    
    # Add lighting to the scene (important for rendering!)
    scene.set_ambient_light([0.3, 0.3, 0.3])  # Ambient light
    scene.add_directional_light(
        direction=[1, -1, -1],  # Light direction
        color=[1.0, 1.0, 1.0],  # White light
        shadow=True,
    )
    scene.add_point_light(
        position=[2, 0, 2],  # Light position above
        color=[1.0, 1.0, 1.0],  # White light
        shadow=False,
    )
    
    # Add a ground plane for reference
    ground_builder = scene.create_actor_builder()
    ground_builder.add_box_collision(half_size=[10, 10, 0.1])
    ground_builder.add_box_visual(half_size=[10, 10, 0.1], material=[0.5, 0.5, 0.5, 1.0])
    ground = ground_builder.build_static(name="ground")
    ground.set_pose(sapien.Pose(p=[0, 0, -0.1]))  # Position ground below robot
    
    # 3. Add a camera if rendering is enabled
    camera = None
    saved_images = []
    if RENDER_ON:
        # Position camera to view the robot
        # Robot is at origin, so place camera at angle
        import numpy as np
        
        # Camera position
        cam_pos = np.array([1.2, 0.8, 0.8])  # Closer to robot
        
        # Look at the robot's approximate center (origin + some height)
        look_at = np.array([0.0, 0.0, 0.5])
        
        # Calculate forward vector (from camera to target)
        forward = look_at - cam_pos
        forward = forward / np.linalg.norm(forward)
        
        # Calculate rotation to look at target
        # Up vector
        up = np.array([0, 0, 1])
        
        # Right vector
        right = np.cross(forward, up)
        right = right / np.linalg.norm(right)
        
        # Recalculate up
        up = np.cross(right, forward)
        
        # Build rotation matrix
        rot_mat = np.eye(3)
        rot_mat[:, 0] = right
        rot_mat[:, 1] = -up  # Flip for camera convention
        rot_mat[:, 2] = -forward  # Camera looks down -Z
        
        # Convert rotation matrix to quaternion (w, x, y, z)
        from scipy.spatial.transform import Rotation
        quat_xyzw = Rotation.from_matrix(rot_mat).as_quat()  # Returns [x, y, z, w]
        quat_wxyz = np.array([quat_xyzw[3], quat_xyzw[0], quat_xyzw[1], quat_xyzw[2]])  # Convert to [w, x, y, z]
        
        camera = scene.add_camera(
            name="main_camera",
            pose=sapien.Pose(p=cam_pos.tolist(), q=quat_wxyz.tolist()),
            width=640,
            height=480,
            fovy=1.2,  # Wider field of view
            near=0.01,
            far=10,
        )
        print(f"Camera added at position {cam_pos}, looking at {look_at}")
    
    # 4. Init qpos
    qpos = robot.get_qpos()
    print("Initial qpos:", qpos)
    print(f"Robot base position: {robot.get_pose()}")
    robot.set_qpos(qpos)
    
    # 5. Move active joints
    # In modern ManiSkill API, use active_joints_map
    print("Active joints:")
    for joint_name in robot.active_joints_map.keys():
        print(f"Joint: {joint_name}")
        
    # consume we only want to move partial single-dof joints, such as left gripper, or left arm joints
    # active_joint_names_to_move = [
    #     'idx41_gripper_l_outer_joint1',
    # ]
    active_joints_to_move = [
        'left_joint1',
        'left_joint2',
        'left_joint3',
        'left_joint4',
        'left_joint5',
        'left_joint6',
        'left_joint7',
    ]
    
    # mock loop
    dt = 1/240.0
    step = 0
    max_steps = 300
    
    while step < max_steps:
        move_specific_joints(robot, active_joints_to_move, delta=0.01)
        scene.step()
        
        if RENDER_ON:
            scene.update_render()
            
            # Capture image every 50 steps
            if SAVE_IMAGES and step % 50 == 0 and camera is not None:
                camera.take_picture()
                rgb_list = camera.get_picture("Color")  # Returns list of tensors
                if len(rgb_list) > 0:
                    rgb = rgb_list[0]  # Get first (and only) image from list
                    # RGB is shape (batch, H, W, 4) with RGBA
                    if rgb.shape[0] == 1:
                        rgb = rgb[0]  # Remove batch dimension: (H, W, 4)
                    rgb = rgb[..., :3]  # Take only RGB: (H, W, 3)
                    if hasattr(rgb, 'cpu'):
                        rgb = rgb.cpu().numpy()
                    saved_images.append((step, rgb))
                    print(f"Step {step}: Captured image shape {rgb.shape}")
        
        # Print joint info occasionally
        if step % 50 == 0:
            print(f"\n--- Step {step} ---")
            print_joint_info(robot, active_joints_to_move)
        
        step += 1
        time.sleep(dt)
    
    # Save captured images
    if SAVE_IMAGES and len(saved_images) > 0:
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        for i, (step_num, img) in enumerate(saved_images[:6]):  # Show first 6 images
            axes[i].imshow(img)
            axes[i].set_title(f"Step {step_num}")
            axes[i].axis('off')
        plt.tight_layout()
        output_path = '/workspace/robot_motion_images.png'
        plt.savefig(output_path)
        print(f"\nSaved {len(saved_images)} images to: {output_path}")
        plt.close()
        
if __name__ == "__main__":
    main()

    
    
    