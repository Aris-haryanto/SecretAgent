import asyncio
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
            print(f"Request: {flow.request.method} {flow.request.url}")
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
