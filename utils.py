import getpass
import subprocess
import sys

def run_command(cmd, sudo=False, capture_output=False):
    if sudo and getpass.getuser() != "root":
        cmd = ["sudo"] + cmd
    try:
        if capture_output:
            res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return res.stdout.strip()
        else:
            subprocess.run(cmd, check=True)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}")
        if capture_output:
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
        sys.exit(1)

# def run_command(cmd_list):
#     """Run a shell command and return stdout."""
#     try:
#         result = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
#         return result.stdout.strip()
#     except subprocess.CalledProcessError as e:
#         print(f"Command {' '.join(cmd_list)} failed with error:\n{e.stderr.strip()}")
#         return None  # Return None if the command fails