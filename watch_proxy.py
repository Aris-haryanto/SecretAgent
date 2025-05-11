import os
import time
import sys
import subprocess
from proxy import set_system_proxy, get_network_services, get_user_shell_profiles, create_proxy_profile, configure_proxy
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




def read_file_lines(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as file:
            return file.readlines()
    except Exception as e:
        print(f"Failed to read {path}: {e}")
        return []

def write_file_lines(path, lines):
    try:
        with open(path, "w") as file:
            file.writelines(lines)
    except Exception as e:
        print(f"Failed to write to {path}: {e}")

def source_line():
    return ENV_SOURCE_PROXY.format(proxy_profile=ENV_PROXY_FILE)

def add_source_line_to_profile(profile_path):
    lines = read_file_lines(profile_path)
    src_line = source_line().strip()
    # Avoid duplicates
    if any(line.strip() == src_line for line in lines):
        return False
    # Add with comment for clarity
    # Append at the end with blank line before comment
    if lines and lines[-1].strip() != "":
        lines.append("\n")
    lines.append("# Source proxy environment variables\n")
    lines.append(src_line + "\n")
    write_file_lines(profile_path, lines)
    print(f"Restored source line in {profile_path}")
    return True

def check_and_restore_source_lines():
    home_dir = os.path.expanduser("~")
    proxy_env_path = os.path.join(home_dir, ENV_PROXY_FILE)
    if not os.path.isfile(proxy_env_path):
        # proxy_env does not exist; recreate it
        create_proxy_profile()

    profiles = get_user_shell_profiles()
    restored_any = False
    for pf in profiles:
        lines = read_file_lines(pf)
        src_line = source_line().strip()
        if not any(line.strip() == src_line for line in lines):
            restored = add_source_line_to_profile(pf)
            restored_any = restored_any or restored

    if not restored_any:
        print("All profiles have the proxy source line.")

def get_proxy_settings(service):
    """Return current proxy enabled status and proxy server for the given network service."""
    try:
        http_enabled = subprocess.check_output(
            ["networksetup", "-getwebproxy", service], text=True
        )
        https_enabled = subprocess.check_output(
            ["networksetup", "-getsecurewebproxy", service], text=True
        )
        # Parse enabled and server info
        def parse_proxy_info(output):
            enabled = False
            server = None
            port = None
            for line in output.splitlines():
                if line.startswith("Enabled:"):
                    enabled = line.split(":")[1].strip().lower() == "yes"
                elif line.startswith("Server:"):
                    server = line.split(":")[1].strip()
                elif line.startswith("Port:"):
                    port = line.split(":")[1].strip()
            return enabled, server, port
        http_enabled_flag, http_server, http_port = parse_proxy_info(http_enabled)
        https_enabled_flag, https_server, https_port = parse_proxy_info(https_enabled)

        return {
            "http": {"enabled": http_enabled_flag, "server": http_server, "port": http_port},
            "https": {"enabled": https_enabled_flag, "server": https_server, "port": https_port},
        }
    except Exception as e:
        print(f"Failed to get proxy settings for {service}: {e}")
        return None

def check_and_prevent_proxy_disable():
    """Check system proxy settings and restore them if they were disabled or changed."""
    services = get_network_services()
    if not services:
        print("No network services found to check proxy status.")
        return

    for service in services:
        settings = get_proxy_settings(service)
        if not settings:
            continue

        http = settings["http"]
        https = settings["https"]
        # If either HTTP or HTTPS proxy is disabled or changed, restore them
        if (not http["enabled"] or http["server"] != ENV_HOST_LISTEN or http["port"] != ENV_PORT_LISTEN or
            not https["enabled"] or https["server"] != ENV_HOST_LISTEN or https["port"] != ENV_PORT_LISTEN):
            print(f"Proxy setting changed or disabled on {service}, restoring...")
            set_system_proxy(service, True)

def watch_proxy_env_file_and_system_proxy():
    """Main loop to watch .proxy_env and system proxy settings."""
    home_dir = os.path.expanduser("~")
    proxy_env_path = os.path.join(home_dir, ENV_PROXY_FILE)

    if not os.path.exists(proxy_env_path):
        print(f"{ENV_PROXY_FILE} does not exist. Creating...")
        create_proxy_profile()
    last_mtime = os.path.getmtime(proxy_env_path) if os.path.exists(proxy_env_path) else None

    while True:
        try:
            if os.path.exists(proxy_env_path):
                current_mtime = os.path.getmtime(proxy_env_path)
                if last_mtime is None or current_mtime != last_mtime:
                    print(f"{ENV_PROXY_FILE} modification detected or monitoring started.")
                    last_mtime = current_mtime
                    create_proxy_profile()
                    check_and_restore_source_lines()
                else:
                    # Also check shell profile lines anyway
                    check_and_restore_source_lines()
            else:
                print(f"{ENV_PROXY_FILE} not found. Restoring...")
                create_proxy_profile()
                check_and_restore_source_lines()
                last_mtime = os.path.getmtime(proxy_env_path) if os.path.exists(proxy_env_path) else None

            # Check system proxy settings and restore if needed
            check_and_prevent_proxy_disable()

            time.sleep(60)
        except KeyboardInterrupt:
            print("Stopping SecretAgent.")
            configure_proxy(False)
            sys.exit(0)
        except Exception as e:
            print(f"Error during watching: {e}")
            time.sleep(60)

