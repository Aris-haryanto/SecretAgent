import getpass
import subprocess
import sys
# from cleanup import cleanup

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

        # cleanup()    
        sys.exit(1)