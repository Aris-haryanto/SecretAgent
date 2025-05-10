import os
import sys
from utils import run_command
from cleanup import cleanup
from init import load_config

config = load_config('config.yml')

def get_network_services():
    """Get a list of all network services on macOS."""
    output = run_command(["networksetup", "-listallnetworkservices"], capture_output=True)
    output = output.splitlines()
    if output is None:
        print("Failed to retrieve network services. Please check your network configuration.")
        cleanup()
        sys.exit(1)
    
    # Skip the first line (header) and filter out disabled services
    services = [s.strip() for s in output[1:] if s.strip() and not s.startswith("*")]
    return services

def set_system_proxy(service, enable):
    """Enable or disable HTTP and HTTPS proxy for a network service."""
    if enable:
        run_command(["networksetup", "-setwebproxy", service, f"{config['host_listen']}", f"{config['port_listen']}"])
        run_command(["networksetup", "-setsecurewebproxy", service, f"{config['host_listen']}", f"{config['port_listen']}"])
        run_command(["networksetup", "-setwebproxystate", service, "on"])
        run_command(["networksetup", "-setsecurewebproxystate", service, "on"])
    else:
        run_command(["networksetup", "-setwebproxystate", service, "off"])
        run_command(["networksetup", "-setsecurewebproxystate", service, "off"])

def get_user_shell_profiles():
    """Return list of possible user shell profile files."""
    home_dir = os.path.expanduser("~")
    user_shell = os.environ.get("SHELL", "")
    profile_files = []

    if "zsh" in user_shell:
        profile_files.append(os.path.join(home_dir, ".zshrc"))
    elif "bash" in user_shell:
        profile_files.append(os.path.join(home_dir, ".bash_profile"))
        profile_files.append(os.path.join(home_dir, ".bashrc"))
    else:
        profile_files.append(os.path.join(home_dir, ".profile"))

    return profile_files

def create_proxy_profile():
    home_dir = os.path.expanduser("~")
    proxy_env_path = os.path.join(home_dir, config['proxy_file'])
    # If file missing, create with basic template content
    if not os.path.exists(proxy_env_path):
        try:
            with open(proxy_env_path, "w") as f:
                content = (f"""# Proxy environment variables added by SecretAgent

export HTTP_PROXY="http://{config['host_listen']}:{config['port_listen']}"
export http_proxy="http://{config['host_listen']}:{config['port_listen']}"
export HTTPS_PROXY="http://{config['host_listen']}:{config['port_listen']}"
export https_proxy="http://{config['host_listen']}:{config['port_listen']}"
export ALL_PROXY="http://{config['host_listen']}:{config['port_listen']}"
export all_proxy="http://{config['host_listen']}:{config['port_listen']}"
export NO_PROXY="localhost,127.0.0.1,::1"
export no_proxy="localhost,127.0.0.1,::1"
"""
                )
                f.write(content)
            print(f"Restored {config['proxy_file']} with default proxy variables.")
        except Exception as e:
            print(f"Failed to restore {config['proxy_file']}: {e}")


def remove_proxy_profile():
    """Remove the dedicated proxy profile file if it exists."""
    home_dir = os.path.expanduser("~")
    proxy_profile_path = os.path.join(home_dir, config['proxy_file'])
    if os.path.exists(proxy_profile_path):
        os.remove(proxy_profile_path)
        print(f"Removed proxy profile file {proxy_profile_path}")

def add_source_line_to_profile(profile_path):
    """Add source line to a profile file if not present."""
    source_line = config['source_proxy'].format(proxy_profile=config['proxy_file'])
    if not os.path.exists(profile_path):
        # Create empty profile file
        with open(profile_path, "w") as f:
            f.write(f"# Created by SecretAgent\n")
    with open(profile_path, "r") as f:
        lines = f.readlines()
    stripped_lines = [line.strip() for line in lines]
    if source_line not in stripped_lines:
        with open(profile_path, "a") as f:
            f.write(f"\n# Source proxy environment variables\n{source_line}\n")
        print(f"Added source line to {profile_path}")

def remove_source_line_from_profile(profile_path):
    """Remove source line from a profile file if present."""
    if not os.path.exists(profile_path):
        return
    source_line = config['source_proxy'].format(proxy_profile=config['proxy_file'])
    with open(profile_path, "r") as f:
        lines = f.readlines()
    new_lines = [line for line in lines if line.strip() != source_line and line.strip() != "# Source proxy environment variables"]
    if len(new_lines) != len(lines):
        with open(profile_path, "w") as f:
            f.writelines(new_lines)
        print(f"Removed source line from {profile_path}")

def set_env_proxy(enable):
    """Create or remove proxy profile and manage source line in shell profiles."""
    profiles = get_user_shell_profiles()
    if enable:
        create_proxy_profile()
        for pf in profiles:
            add_source_line_to_profile(pf)
    else:
        for pf in profiles:
            remove_source_line_from_profile(pf)
        remove_proxy_profile()

def configure_proxy(enable=True):
    services = get_network_services()
    if not services:
        print("No network services found.")
        cleanup()
        sys.exit(1)

    if enable:
        print("Enabling proxy for all network services...")
        for s in services:
            print(f"Setting proxy on: {s}")
            set_system_proxy(s, True)
        print("Setting CLI environment variables for proxy (dedicated proxy profile)...")
        set_env_proxy(True)
        print("\n Proxy enabled system-wide. Please restart your terminal or source your shell profile to apply CLI proxy settings.")
    else:
        print("Disabling proxy for all network services...")
        for s in services:
            print(f"Disabling proxy on: {s}")
            set_system_proxy(s, False)
        print("Removing CLI environment variables from proxy profile and shell profiles...")
        set_env_proxy(False)
        print("\n Proxy disabled system-wide. Please restart your terminal or source your shell profile to apply CLI changes.")
