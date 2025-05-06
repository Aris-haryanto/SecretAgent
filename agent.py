#!/usr/bin/env python3
import os
import sys
import subprocess
import plistlib
import getpass
import asyncio
import re
from pathlib import Path

LAUNCH_AGENT_LABEL = "com.user.secret.agent"
HOME = str(Path.home())
LAUNCH_AGENT_DIR = os.path.join(HOME, "Library", "LaunchAgents")
PLIST_PATH = os.path.join(LAUNCH_AGENT_DIR, f"{LAUNCH_AGENT_LABEL}.plist")
HOST_LISTEN = "127.0.0.1"
PORT_LISTEN = 41215
CERT = "YOUR_OWN_PATH/.mitmproxy/mitmproxy-ca-cert.pem"
CURR_DIR = "YOUR_OWN_PATH"


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

def install_cert_to_keychain():
    print("Installing the certificate to macOS System Keychain for trust... (requires sudo)")
    
    #remove exist keychain
    remove_cert_from_keychain()
    
    run_command(["security", "add-trusted-cert", "-d", "-r", "trustRoot", "-k",
                 "/Library/Keychains/System.keychain", CERT], sudo=True)

    print("Certificate added and trusted to System Keychain.")


def configure_proxy(enable=True):
    if enable:
        print("Configuring system proxy settings...")
        run_command(["networksetup", "-setwebproxy", "Wi-Fi", f"{HOST_LISTEN}", f"{PORT_LISTEN}"])
        run_command(["networksetup", "-setsecurewebproxy", "Wi-Fi", f"{HOST_LISTEN}", f"{PORT_LISTEN}"])
        run_command(["networksetup", "-setwebproxystate", "Wi-Fi", "on"])
        run_command(["networksetup", "-setsecurewebproxystate", "Wi-Fi", "on"])
        print("Proxy enabled.")
    else:
        print("Disabling system proxy settings...")
        run_command(["networksetup", "-setwebproxystate", "Wi-Fi", "off"])
        run_command(["networksetup", "-setsecurewebproxystate", "Wi-Fi", "off"])
        print("Proxy disabled.")


def write_launch_agent():
    print(f"Creating launch agent plist at {PLIST_PATH} ...")
    os.makedirs(LAUNCH_AGENT_DIR, exist_ok=True)
    python_executable = sys.executable
    script_path = os.path.realpath(__file__)

    plist = {
        "Label": LAUNCH_AGENT_LABEL,
        "ProgramArguments": [python_executable, script_path, "--run-proxy"],
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": os.path.join(CURR_DIR, "agent.log"),
        "StandardErrorPath": os.path.join(CURR_DIR, "agent.err"),
        "WorkingDirectory": CURR_DIR
    }

    with open(PLIST_PATH, "wb") as f:
        plistlib.dump(plist, f)

    run_command(["launchctl", "unload", PLIST_PATH], sudo=False)  # unload if loaded
    run_command(["launchctl", "load", PLIST_PATH], sudo=False)
    print(f"Launch agent {LAUNCH_AGENT_LABEL} loaded to run continuously at startup.")


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


def unload_and_remove_launch_agent():
    print("Unloading and removing launch agent...")
    if os.path.exists(PLIST_PATH):
        run_command(["launchctl", "unload", PLIST_PATH], sudo=False)
        os.remove(PLIST_PATH)
        print(f"Removed launch agent plist: {PLIST_PATH}")
    else:
        print("Launch agent plist not found; skipping removal.")


def cleanup():
    print("Starting cleanup of all registered components...")

    unload_and_remove_launch_agent()
    remove_cert_from_keychain()
    configure_proxy(False)

    print("Cleanup complete.")


async def run_proxy_async():
    from mitmproxy.options import Options
    from mitmproxy.tools.dump import DumpMaster

    options = Options(listen_host=HOST_LISTEN, listen_port=PORT_LISTEN)
    # options = Options(listen_host='localhost', listen_port=8080, certs=[cert_path])
    options.ssl_insecure = False

    m = DumpMaster(options)

    class LoggerAddon:
        def request(self, flow):
            # Log request method, URL, and payload
            print(f"Request: {flow.request.method} {flow.request.url}")
            # if flow.request.content:
            #     print(f"Request Payload: {flow.request.content.decode('utf-8', errors='replace')}")

            # Show the application that triggered the connection
            self.show_application_info(flow.request.host)

        def show_application_info(self, host):
            try:
                # Get the list of active connections using netstat
                result = subprocess.run(
                    ["netstat", "-anp", "tcp"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print("Applications making connections to the host:")
                for line in result.stdout.strip().splitlines()[2:]:  # Skip the header lines
                    # Use regex to extract the relevant information
                    match = re.search(r'(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)', line)
                    if match:
                        local_address = match.group(2)
                        remote_address = match.group(3)
                        pid = match.group(5)
                        # Check if the remote address matches the requested host
                        if host in remote_address:
                            try:
                                process = subprocess.run(
                                    ["ps", "-p", pid, "-o", "comm="],
                                    check=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True
                                )
                                app_name = process.stdout.strip()
                                print(f"PID: {pid}, Application: {app_name}")
                            except subprocess.CalledProcessError:
                                print(f"PID: {pid} no longer exists or cannot be accessed.")

            except Exception as e:
                print(f"Error checking for applications: {e}")


        # no need response
        # def response(self, flow):
        #     # Log response URL and status code
        #     print(f"Response: {flow.request.url} - {flow.response.status_code}")
        #     if flow.response.content:
        #         print(f"Response Payload: {flow.response.content.decode('utf-8', errors='replace')}")


    m.addons.add(LoggerAddon())

    print(f"Starting mitmproxy HTTPS intercepting proxy on https://{HOST_LISTEN}:{PORT_LISTEN} ...")
    await m.run()


def run_proxy_server():
    try:
        asyncio.run(run_proxy_async())
    except KeyboardInterrupt:
        print("Proxy interrupted by user. Stopping proxy...")

def kill_process_on_port():
    try:
        # Get the list of processes using the specified port
        result = subprocess.run(
            ["lsof", "-t", f"-i:{PORT_LISTEN}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        pids = result.stdout.strip().splitlines()

        if pids:
            for pid in pids:
                print(f"Killing process with PID: {pid} on port {PORT_LISTEN}")
                run_command(["kill", "-9", pid])
        else:
            print(f"No process found on port {PORT_LISTEN}.")
    except subprocess.CalledProcessError as e:
        print(f"Error checking for processes on port {PORT_LISTEN}: {e.stderr}")


def main():
    if len(sys.argv) == 1:
        print("Usage:")
        print("Secret Agent [OPTIONS]")
        print("")
        print("Options:")
        print("  --run-proxy     Run the proxy server immediately (default action)")
        print("  --startup       Install cert, register launch agent to run proxy at startup")
        print("  --cleanup       Remove launch agent and uninstall certificate")
        print("")
        print("Examples:")
        print("Secret Agent --run-proxy")
        print("Secret Agent --startup")
        print("Secret Agent --cleanup")
        print("")
        sys.exit(0)

    if "--cleanup" in sys.argv:
        cleanup()
        return

    if "--startup" in sys.argv:
        kill_process_on_port()
        install_cert_to_keychain()
        write_launch_agent()
        configure_proxy(True)

        print("Startup registration complete. Proxy will run continuously at startup.")

    if "--run-proxy" in sys.argv:
        kill_process_on_port()
        install_cert_to_keychain()
        configure_proxy(True)
        run_proxy_server()


if __name__ == "__main__":
    main()