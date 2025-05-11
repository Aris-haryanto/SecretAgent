
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



def install_cert_to_keychain():
    print("Installing the certificate to macOS System Keychain for trust... (requires sudo)")
    
    #remove exist keychain
    remove_cert_from_keychain()
    
    run_command(["security", "add-trusted-cert", "-d", "-r", "trustRoot", "-k",
                 "/Library/Keychains/System.keychain", ENV_CERT], sudo=True)

    print("Certificate added and trusted to System Keychain.")

def remove_cert_from_keychain():
    print("Removing the certificate from macOS System Keychain... (requires sudo)")
    cert_name = "InterceptCA"

    try:
        output = run_command(
            ["security", "find-certificate", "-c", cert_name, "-a", "-Z", "/Library/Keychains/System.keychain"],
            sudo=True,
            capture_output=True
        )
    except SystemExit:
        print("Certificate not found in keychain or error occurred, skipping removal.")
        return

    sha1s = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("SHA-1 hash:"):
            sha1 = line.split("SHA-1 hash:")[1].strip()
            sha1s.append(sha1)

    if not sha1s:
        print("No matching certificates found in keychain.")
        return

    for sha1 in sha1s:
        print(f"Deleting certificate with SHA-1: {sha1}")
        run_command(["security", "delete-certificate", "-Z", sha1, "/Library/Keychains/System.keychain"], sudo=True)

    print("Certificate(s) removed from System Keychain.")
