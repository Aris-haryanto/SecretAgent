import os

ENV_LAUNCH_AGENT_LABEL = "com.secret.agent"
ENV_HOME = os.path.expanduser("~")
ENV_LAUNCH_AGENT_DIR = os.path.join(ENV_HOME, "Library", "LaunchAgents")
ENV_PLIST_PATH = os.path.join(ENV_LAUNCH_AGENT_DIR, "com.secret.agent.plist")
ENV_HOST_LISTEN = "127.0.0.1"
ENV_PORT_LISTEN = 41215
ENV_CURR_PROJECT_DIR = os.getcwd()  # or os.path.dirname(os.path.abspath(__file__))
ENV_CERT = os.path.join(ENV_CURR_PROJECT_DIR, "secret-agent.pem")
ENV_PROXY_FILE = ".proxy_env"
ENV_SOURCE_PROXY = f"source {os.path.join(ENV_HOME, ENV_PROXY_FILE)}"