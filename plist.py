import os
import sys
import plistlib
from utils import run_command
from env import (
    ENV_LAUNCH_AGENT_LABEL,
    ENV_HOME,
    ENV_LAUNCH_AGENT_DIR,
    ENV_PLIST_PATH,
    ENV_HOST_LISTEN,
    ENV_PORT_LISTEN,
    ENV_CERT,
    ENV_CURR_PROJECT_DIR,
    ENV_PROXY_FILE,
    ENV_SOURCE_PROXY
)



def write_launch_agent():
    print(f"Creating LaunchAgent plist at {ENV_PLIST_PATH} ...")
    os.makedirs(ENV_LAUNCH_AGENT_DIR, exist_ok=True)

    if getattr(sys, 'frozen', False):
        # Compiled with PyInstaller
        executable_path = os.path.realpath(sys.executable)
        program_args = [executable_path, "--intercept-on"]
    else:
        # Running as plain Python
        python_executable = sys.executable
        script_path = os.path.realpath('main.py')
        program_args = [python_executable, script_path, "--intercept-on"]

    plist = {
        "Label": ENV_LAUNCH_AGENT_LABEL,
        "ProgramArguments": program_args,
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": os.path.join(ENV_CURR_PROJECT_DIR, "agent.log"),
        "StandardErrorPath": os.path.join(ENV_CURR_PROJECT_DIR, "agent.err"),
        "WorkingDirectory": ENV_CURR_PROJECT_DIR
    }

    with open(ENV_PLIST_PATH, "wb") as f:
        plistlib.dump(plist, f)

    # Set correct permissions
    os.chown(ENV_PLIST_PATH, 0, 0)  # root:wheel
    os.chmod(ENV_PLIST_PATH, 0o644)

    # Reload daemon
    run_command(["launchctl", "unload", ENV_PLIST_PATH], sudo=True)
    run_command(["launchctl", "load", ENV_PLIST_PATH], sudo=True)

    print(f"LaunchAgent {ENV_LAUNCH_AGENT_LABEL} installed and loaded.")



def unload_and_remove_launch_agent():
    print("Unloading and removing launch agent...")
    if os.path.exists(ENV_PLIST_PATH):
        run_command(["launchctl", "unload", ENV_PLIST_PATH], sudo=False)
        os.remove(ENV_PLIST_PATH)
        print(f"Removed launch agent plist: {ENV_PLIST_PATH}")
    else:
        print("Launch agent plist not found; skipping removal.")