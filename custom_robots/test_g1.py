# Usage: 
# python custom_robots/test_g1.py -r "agibot_g1_omni_picker"
# python custom_robots/test_g1.py -r "agibot_g1_120s"

import agibot_g1 # imports your robot and registers it
# imports the demo_robot example script and lets you test your new robot
import mani_skill.examples.demo_robot as demo_robot_script
import tyro

if __name__ == "__main__":
    args = tyro.cli(demo_robot_script.Args)
    demo_robot_script.main(args)