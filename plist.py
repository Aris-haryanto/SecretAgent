import os
import sys
import plistlib
from utils import run_command
from init import load_config

config = load_config("config.yml")

def write_launch_agent():
    print(f"Creating launch agent plist at {config['plist_path']} ...")
    os.makedirs(config['launch_agent_dir'], exist_ok=True)
    python_executable = sys.executable
    script_path = os.path.realpath(__file__)

    plist = {
        "Label": config['launch_agent_label'],
        "ProgramArguments": [python_executable, script_path, "--run-proxy"],
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": os.path.join(config['curr_project_dir'], "agent.log"),
        "StandardErrorPath": os.path.join(config['curr_project_dir'], "agent.err"),
        "WorkingDirectory": config['curr_project_dir']
    }

    with open(config['plist_path'], "wb") as f:
        plistlib.dump(plist, f)

    run_command(["launchctl", "unload", config['plist_path']], sudo=False)  # unload if loaded
    run_command(["launchctl", "load", config['plist_path']], sudo=False)
    print(f"Launch agent {config['launch_agent_label']} loaded to run continuously at startup.")


def unload_and_remove_launch_agent():
    print("Unloading and removing launch agent...")
    if os.path.exists(config['plist_path']):
        run_command(["launchctl", "unload", config['plist_path']], sudo=False)
        os.remove(config['plist_path'])
        print(f"Removed launch agent plist: {config['plist_path']}")
    else:
        print("Launch agent plist not found; skipping removal.")