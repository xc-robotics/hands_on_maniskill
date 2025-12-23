from mani_skill.envs.scene import ManiSkillScene
from mani_skill.utils.structs.types import SimConfig
from mani_skill.envs.utils.system.backend import BackendInfo
import sapien

backend = BackendInfo(device='cpu', sim_device='cpu', sim_backend='physx', render_backend='auto', render_device='cpu')
scene = ManiSkillScene(sim_config=SimConfig(sim_freq=100, control_freq=20), backend=backend)

loader = scene.create_urdf_loader()
loader.fix_root_link = True
robot = loader.load('robot_descriptions/agibot_g1_with_gripper_description/agibot_g1_with_120s.urdf')

camera = scene.add_camera(
    name='test_camera',
    pose=sapien.Pose(p=[2, 0, 1], q=[0.924, 0, 0.383, 0]),
    width=320,
    height=240,
    fovy=1.0,
    near=0.01,
    far=10,
)

scene.step()
scene.update_render()

camera.take_picture()
result = camera.get_picture('Color')
print(f'Type of result: {type(result)}')
print(f'Result: {result}')
if isinstance(result, dict):
    print(f'Keys: {result.keys()}')