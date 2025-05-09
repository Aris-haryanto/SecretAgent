import sys
import signal
import subprocess
import threading
from utils import run_command
from proxy import configure_proxy
from watch_profile import watch_proxy_env_file
from plist import write_launch_agent,unload_and_remove_launch_agent
from certificate import remove_cert_from_keychain, install_cert_to_keychain
from intercept import run_proxy_server
from init import load_config

config = load_config("config.yml")

# Create a global variable to control the thread
stop_event = threading.Event()

def cleanup():
    print("Starting cleanup of all registered components...")

    unload_and_remove_launch_agent()
    remove_cert_from_keychain()
    configure_proxy(False)

    print("Cleanup complete.")

def kill_process_on_port():
    try:
        # Get the list of processes using the specified port
        result = subprocess.run(
            ["lsof", "-t", f"-i:{config['port_listen']}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        pids = result.stdout.strip().splitlines()

        if pids:
            for pid in pids:
                print(f"Killing process with PID: {pid} on port {config['port_listen']}")
                run_command(["kill", "-9", pid])
        else:
            print(f"No process found on port {config['port_listen']}.")
    except subprocess.CalledProcessError as e:
        print(f"Error checking for processes on port {config['port_listen']}: {e.stderr}")

def signal_handler(sig, frame):
    print('Received shutdown signal. Cleaning up...')
    # Perform any cleanup actions here
    cleanup()
    sys.exit(0)

def main():
     # Register the signal handler for SIGINT (Ctrl+C) and SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create a thread for the watch_proxy_env_file function
    watcher_thread = threading.Thread(target=watch_proxy_env_file)
    watcher_thread.daemon = True  # This makes the thread exit when the main program exits
    watcher_thread.start()  # Start the thread

     # Signal the watcher thread to stop
    stop_event.set()


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

    # Wait for the watcher thread to finish
    watcher_thread.join()

if __name__ == "__main__":
    main()