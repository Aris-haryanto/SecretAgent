from certificate import remove_cert_from_keychain
from proxy import configure_proxy

def cleanup():
    print("Starting cleanup of all registered components...")

    # unload_and_remove_launch_agent()
    remove_cert_from_keychain()
    configure_proxy(False)

    print("Cleanup complete.")