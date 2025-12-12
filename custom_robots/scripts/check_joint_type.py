import sapien
from mani_skill.envs.scene import ManiSkillScene
from mani_skill.utils.structs.types import SimConfig
from mani_skill.envs.utils.system.backend import BackendInfo

backend = BackendInfo(
    device='cpu',
    sim_device='cpu',
    sim_backend='physx',
    render_backend='none',
    render_device=None,
)

scene = ManiSkillScene(
    sim_config=SimConfig(sim_freq=100, control_freq=20),
    backend=backend,
)

loader = scene.create_urdf_loader()
robot = loader.load('robot_descriptions/agibot_g1_with_gripper_description/agibot_g1_with_120s.urdf')

# Check what active_joints_map contains
joint_name = 'left_joint1'
joint_obj = robot.active_joints_map[joint_name]
print(f'Type of joint object: {type(joint_obj)}')
print(f'Joint object attributes: {dir(joint_obj)}')
print(f'Joint name: {joint_obj.name}')

# Try to find qpos index
if hasattr(joint_obj, 'dof_index'):
    print(f'DOF index: {joint_obj.dof_index}')
if hasattr(joint_obj, 'active_index'):
    print(f'Active index: {joint_obj.active_index}')
if hasattr(joint_obj, 'index'):
    print(f'Index: {joint_obj.index}')