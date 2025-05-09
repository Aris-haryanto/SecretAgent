import os
from pathlib import Path
import yaml

# Load YAML config file
def load_config(config_path="config.yml"):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    # Expand home directory path if shorthand is used
    if 'home' in config:
        config['home'] = os.path.expanduser(config['home'])

    # For launch_agent_dir and plist_path, expand ~ and allow dynamic generation
    launch_agent_dir = os.path.expanduser(config.get('launch_agent_dir', '~/Library/LaunchAgents'))
    config['launch_agent_dir'] = launch_agent_dir

    # Compose plist_path if not set explicitly or resolve if string contains ~
    plist_path = config.get('plist_path')
    if not plist_path or '~' in plist_path:
        plist_path = os.path.join(launch_agent_dir, f"{config['launch_agent_label']}.plist")
    else:
        plist_path = os.path.expanduser(plist_path)
    config['plist_path'] = plist_path

    return config

