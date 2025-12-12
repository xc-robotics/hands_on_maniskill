import sapien
from mani_skill.envs.scene import ManiSkillScene
from mani_skill.utils.structs.types import SimConfig
from mani_skill.envs.utils.system.backend import BackendInfo

import time
import numpy as np
from typing import Dict, List

RENDER_ON=True

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
    
    # 3. Init qpos
    qpos = robot.get_qpos()
    print("Initial qpos:", qpos)
    robot.set_qpos(qpos)
    
    # 4. Move active joints
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
    for step in range(300):
        move_specific_joints(robot, active_joints_to_move, delta=0.01)
        scene.step()
        if RENDER_ON:
            scene.update_render()
        print_joint_info(robot, active_joints_to_move)
        time.sleep(dt)
        
if __name__ == "__main__":
    main()

    
    
    