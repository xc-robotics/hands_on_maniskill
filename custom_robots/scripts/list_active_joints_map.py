import sapien
from mani_skill.envs.scene import ManiSkillScene
from mani_skill.utils.structs.types import SimConfig
from mani_skill.envs.utils.system.backend import BackendInfo

# 1) Create a backend (IMPORTANT)
# render_device="none" => no renderer required, but backend object exists
backend = BackendInfo(
    device="cpu",           # torch device
    sim_device="cpu",       # physics device
    sim_backend="physx",    # sapien backend
    render_backend="none",  # disable renderer
    render_device=None,     # MUST exist, but None is allowed
)

# 2) Create ManiSkillScene (NOTE: don't pass sapien.Engine() here)
scene = ManiSkillScene(
    sim_config=SimConfig(sim_freq=100, control_freq=20),
    backend=backend,
)

# 3) Create loader from the scene (recommended API)
loader = scene.create_urdf_loader()

robot = loader.load(
    "robot_descriptions/agibot_g1_with_gripper_description/agibot_g1_with_120s.urdf"
)

print(list(robot.active_joints_map.keys()))
# ['left_wheel_joint', 'right_wheel_joint', 'body_joint1', 'body_joint2', 'head_joint1', 'head_joint2', 'left_joint1', 'right_joint1', 'left_joint2', 'right_joint2', 'left_joint3', 'right_joint3', 'left_joint4', 'right_joint4', 'left_joint5', 'right_joint5', 'left_joint6', 'right_joint6', 'left_joint7', 'right_joint7', 'idx41_gripper_l_outer_joint1', 'idx49_gripper_l_outer_joint2', 'idx39_gripper_l_inner_joint2', 'idx31_gripper_l_inner_joint1', 'idx81_gripper_r_outer_joint1', 'idx89_gripper_r_outer_joint2', 'idx79_gripper_r_inner_joint2', 'idx71_gripper_r_inner_joint1', 'idx42_gripper_l_outer_joint3', 'idx32_gripper_l_inner_joint3', 'idx82_gripper_r_outer_joint3', 'idx72_gripper_r_inner_joint3', 'idx43_gripper_l_outer_joint4', 'idx33_gripper_l_inner_joint4', 'idx83_gripper_r_outer_joint4', 'idx73_gripper_r_inner_joint4']
