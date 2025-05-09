import os
import time
import sys

PROXY_PROFILE_FILENAME = ".proxy_env"
SOURCE_LINE_TEMPLATE = 'source ~/{proxy_profile}'

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
    return SOURCE_LINE_TEMPLATE.format(proxy_profile=PROXY_PROFILE_FILENAME)

def add_source_line_to_profile(profile_path):
    lines = read_file_lines(profile_path)
    src_line = source_line().strip()
    # Avoid duplicates
    if any(line.strip() == src_line for line in lines):
        return False
    # Add with comment for clarity
    lines.append("\n# Source proxy environment variables\n")
    lines.append(src_line + "\n")
    write_file_lines(profile_path, lines)
    print(f"Restored source line in {profile_path}")
    return True

def check_and_restore_source_lines():
    home_dir = os.path.expanduser("~")
    proxy_env_path = os.path.join(home_dir, PROXY_PROFILE_FILENAME)
    if not os.path.isfile(proxy_env_path):
        # proxy_env does not exist; no need to restore
        return

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

def watch_proxy_env_file():
    home_dir = os.path.expanduser("~")
    proxy_env_path = os.path.join(home_dir, PROXY_PROFILE_FILENAME)

    if not os.path.exists(proxy_env_path):
        print(f"{PROXY_PROFILE_FILENAME} does not exist. Waiting for creation...")
        last_mtime = None
    else:
        last_mtime = os.path.getmtime(proxy_env_path)

    while True:
        try:
            if os.path.exists(proxy_env_path):
                current_mtime = os.path.getmtime(proxy_env_path)
                if last_mtime is None or current_mtime != last_mtime:
                    print(f"{PROXY_PROFILE_FILENAME} modification detected or monitoring started.")
                    last_mtime = current_mtime
                    check_and_restore_source_lines()
                else:
                    # Still check in case source line was removed even if file not changed
                    check_and_restore_source_lines()
            else:
                print(f"{PROXY_PROFILE_FILENAME} not found. Waiting for creation...")
                last_mtime = None
            time.sleep(60)
        except KeyboardInterrupt:
            print("Stopping watch_profile.py script.")
            sys.exit(0)
        except Exception as e:
            print(f"Error during watching: {e}")
            time.sleep(60)