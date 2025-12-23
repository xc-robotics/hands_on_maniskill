"""
Working example: Access head_camera using direct scene instantiation
"""

import sapien
from mani_skill.envs.scene import ManiSkillScene
from mani_skill.utils.structs.types import SimConfig
from mani_skill.envs.utils.system.backend import BackendInfo
from mani_skill.agents.registration import REGISTERED_AGENTS
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.insert(0, '/workspace/custom_robots')
import agibot_g1

print("Creating scene with rendering enabled...")

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

print("Adding lighting to scene...")
# Add lighting (important for rendering!)
scene.set_ambient_light([0.5, 0.5, 0.5])
scene.add_directional_light(
    direction=[1, -1, -1],
    color=[1.0, 1.0, 1.0],
    shadow=True,
)

# Add ground plane for visual reference
ground_builder = scene.create_actor_builder()
ground_builder.add_box_collision(half_size=[10, 10, 0.1])
ground_builder.add_box_visual(half_size=[10, 10, 0.1], material=[0.8, 0.8, 0.8, 1.0])
ground = ground_builder.build_static(name="ground")
ground.set_pose(sapien.Pose(p=[0, 0, -0.1]))

# Add a colorful cube for the camera to see
cube_builder = scene.create_actor_builder()
cube_builder.add_box_collision(half_size=[0.05, 0.05, 0.05])
cube_builder.add_box_visual(half_size=[0.05, 0.05, 0.05], material=[1.0, 0.2, 0.2, 1.0])  # Red cube
cube = cube_builder.build_kinematic(name="cube")
cube.set_pose(sapien.Pose(p=[0.5, 0, 0.5]))  # In front of robot

print("Instantiating agent with head_camera...")
# Instantiate agent - REGISTERED_AGENTS returns AgentSpec, access .agent_cls
agent_spec = REGISTERED_AGENTS["agibot_g1_omni_picker"]
agent = agent_spec.agent_cls(scene, control_freq=20)

print(f"Agent type: {type(agent)}")
print(f"Agent has sensors: {hasattr(agent, 'sensors')}")

# Check available sensors
if hasattr(agent, 'sensors'):
    print(f"Available sensors: {list(agent.sensors.keys())}")
    
    if 'head_camera' in agent.sensors:
        head_camera = agent.sensors['head_camera']
        print(f"\n✓ Found head_camera!")
        print(f"  Camera name: {head_camera.name}")
        print(f"  Camera type: {type(head_camera)}")
        
        # Step and render
        print("\nRendering scene...")
        scene.step()
        scene.update_render()
        
        # Capture image
        print("Capturing image from head_camera...")
        head_camera.take_picture()
        
        # Get RGB image
        rgb_data = head_camera.get_picture("Color")
        print(f"  RGB data type: {type(rgb_data)}")
        print(f"  RGB data length: {len(rgb_data) if isinstance(rgb_data, list) else 'N/A'}")
        
        if isinstance(rgb_data, list) and len(rgb_data) > 0:
            rgb_image = rgb_data[0]
            print(f"  Raw image shape: {rgb_image.shape}")
            
            # Process image
            if len(rgb_image.shape) == 4 and rgb_image.shape[0] == 1:
                rgb_image = rgb_image[0]  # Remove batch dimension
            
            rgb_image = rgb_image[..., :3]  # Take RGB only
            
            if hasattr(rgb_image, 'cpu'):
                rgb_image = rgb_image.cpu().numpy()
            
            print(f"  Processed image shape: {rgb_image.shape}")
            print(f"  Value range: [{rgb_image.min():.3f}, {rgb_image.max():.3f}]")
            
            # Save image
            plt.figure(figsize=(8, 6))
            plt.imshow(rgb_image)
            plt.title("Head Camera View - Robot Perspective")
            plt.axis('off')
            plt.tight_layout()
            output_path = '/workspace/head_camera_working.png'
            plt.savefig(output_path, bbox_inches='tight', dpi=150)
            print(f"\n✓✓ SUCCESS! Saved image to: {output_path}")
            plt.close()
            
        else:
            print("  ⚠ No RGB data returned")
    else:
        print(f"⚠ head_camera not found! Available sensors: {list(agent.sensors.keys())}")
else:
    print("⚠ Agent has no sensors attribute!")

print("\nDone!")
