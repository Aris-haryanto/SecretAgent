import sys
import signal
import subprocess
import threading
from utils import run_command
from proxy import configure_proxy
from watch_proxy import check_and_restore_source_lines, watch_proxy_env_file_and_system_proxy
from plist import write_launch_agent,unload_and_remove_launch_agent
from certificate import install_cert_to_keychain, remove_cert_from_keychain
from intercept import run_proxy_server
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



# Create a global variable to control the thread
stop_event = threading.Event()

def cleanup():
    print("Stop intercept ...")
    configure_proxy(False)
    print("Intercept Complete.")

def kill_process_on_port():
    try:
        # Get the list of processes using the specified port
        result = subprocess.run(
            ["lsof", "-t", f"-i:{ENV_PORT_LISTEN}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        pids = result.stdout.strip().splitlines()

        if pids:
            for pid in pids:
                print(f"Killing process with PID: {pid} on port {ENV_PORT_LISTEN}")
                run_command(["kill", "-9", pid])
        else:
            print(f"No process found on port {ENV_PORT_LISTEN}.")
    except subprocess.CalledProcessError as e:
        print(f"Error checking for processes on port {ENV_PORT_LISTEN}: {e.stderr}")

def signal_handler(sig, frame):
    print('Received shutdown signal. Cleaning up...')
    # Perform any cleanup actions here
    cleanup()
    sys.exit(0)

def main():
     # Register the signal handler for SIGINT (Ctrl+C) and SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if len(sys.argv) == 1:
        print("Usage:")
        print("SecretAgent [OPTIONS]")
        print("")
        print("Options:")
        print("  --intercept-on         Run Intercept immediately")
        print("  --intercept-off        Stop Intercept agent and uninstall certificate")
        print("  --startup              register startup agent to run intercept at startup")
        print("  --remove-startup       remove agent at startup")
        print("  --add-certificate      Install ssl certificate")
        print("  --remove-certificate   uninstall ssl certificate")
        print("")
        sys.exit(0)

    if "--startup" in sys.argv:
        write_launch_agent()

        print("Startup registration complete. Proxy will run continuously at startup.")
    
    if "--remove-startup" in sys.argv:
        unload_and_remove_launch_agent()

        print("Remove from Startup complete.")

    if "--add-certificate" in sys.argv:
        install_cert_to_keychain()

        print("Install Certificate")

    if "--remove-certificate" in sys.argv:
        remove_cert_from_keychain()

        print("Uninstall Certificate")

    if "--intercept-off" in sys.argv:
        cleanup()
        return

    if "--intercept-on" in sys.argv:
        # Create a thread for the watch_proxy_env_file function
        watcher_thread = threading.Thread(target=check_and_restore_source_lines)
        watcher_thread = threading.Thread(target=watch_proxy_env_file_and_system_proxy)
        watcher_thread.daemon = True  # This makes the thread exit when the main program exits
        watcher_thread.start()  # Start the thread

        # Signal the watcher thread to stop
        stop_event.set()
        
        kill_process_on_port()
        configure_proxy(True)
        run_proxy_server()
        
        # Wait for the watcher thread to finish
        watcher_thread.join()

if __name__ == "__main__":
    main()