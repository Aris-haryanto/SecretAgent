import asyncio
import os
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster
from init import load_config

config = load_config('config.yml')

async def run_proxy_async():
    options = Options(listen_host=config['host_listen'], listen_port=config['port_listen'])
    # options = Options(listen_host='localhost', listen_port=8080, certs=[cert_path])
    options.ssl_insecure = False

    m = DumpMaster(options)

    class LoggerAddon:
        def request(self, flow):
            # Log request method, URL, and payload
            # print(f"Request: {flow.request.method} {flow.request.url}")
            write_to_file('network.log', f"{flow.request.method} {flow.request.url}\n")

            # if flow.request.content:
            #     print(f"Request Payload: {flow.request.content.decode('utf-8', errors='replace')}")

            # Show the application that triggered the connection
            # self.show_application_info(flow.request.host)

        # def show_application_info(self, host):
        #     try:
        #         # Get the list of active connections using lsof
        #         result = subprocess.run(
        #             ["lsof", "-i", "TCP"],
        #             check=True,
        #             stdout=subprocess.PIPE,
        #             stderr=subprocess.PIPE,
        #             text=True
        #         )
        #         print("Applications making connections to the host:")
        #         for line in result.stdout.strip().splitlines()[1:]:  # Skip the header line
        #             parts = line.split()
        #             if len(parts) >= 9:  # Ensure there are enough parts
        #                 command = parts[0]  # Command name
        #                 pid = parts[1]      # PID
        #                 remote_address = parts[8]  # Remote address (IP:port)
        #                 # Check if the remote address matches the requested host
        #                 if host in remote_address:
        #                     print(f"PID: {pid}, Application: {command}")
        #     except Exception as e:
        #         print(f"Error checking for applications: {e}")

    m.addons.add(LoggerAddon())

    print(f"Starting mitmproxy HTTPS intercepting proxy on https://{config['host_listen']}:{config['port_listen']} ...")
    await m.run()


def run_proxy_server():
    try:
        asyncio.run(run_proxy_async())
    except KeyboardInterrupt:
        print("Proxy interrupted by user. Stopping proxy...")


def write_to_file(file_name, text):
    file_path = os.path.join(config['curr_project_dir'], file_name)
    # Check if the file exists and its size
    if os.path.exists(file_path) and os.path.getsize(file_path) >= 1 * 1024 * 1024:  # 2MB in bytes
        # Rewrite the file if it is 2MB or larger
        with open(file_path, 'w') as file:
            file.write(text)
            print(f"File '{file_path}' was too large. It has been rewritten.")
    else:
        # Append to the file if it is smaller than 2MB
        with open(file_path, 'a') as file:
            file.write(text)
            print(f"Text has been appended to '{file_path}'.")