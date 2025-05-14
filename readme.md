# SecretAgent

**SecretAgent** is a Python-based **MITM (Man-in-the-Middle) proxy** tool designed to intercept, inspect, and analyze HTTPS and HTTP network traffic. Built for security teams and researchers, it enables visibility into encrypted sessions and supports AI-based inspection using local models via [Ollama](https://ollama.com/).

> 🔍 Tested on macOS. Compatibility for Linux and Windows is planned.

## 📖 Example
More example and explanation here https://arisharyanto.medium.com/mitm-https-payload-with-python-499ebf8e933f

---

## ⚙️ Features

- 🔐 **MITM Proxy for HTTPS/HTTP**  
  Intercept and inspect live network traffic, including decrypted HTTPS payloads.

- 🧠 **AI Integration with Ollama** *(Experimental)*  
  Use local LLMs to analyze request contents and detect anomalies or threats.

- 📡 **Real-Time Traffic Monitoring**  
  See URLs, headers, payloads, and metadata instantly in your terminal.

- 🐍 **Python-Based and Simple**  
  Lightweight codebase, easy to understand and extend.

---

## 🔍 Use Cases

- Malware traffic inspection
- Suspicious outbound request monitoring
- Internal research on encrypted network behavior
- Traffic classification using LLMs
- Building custom traffic rules for threat detection

---

## 🛠️ Requirements

- Python 3.8 or newer  
- [Ollama](https://ollama.com/) for local AI analysis *(optional)*

---

## 📦 Setup

```bash
# Clone repo on your local
$ git clone https://github.com/Aris-haryanto/SecretAgent.git
$ cd SecretAgent

# create virtual env
$ python3 -m venv .{name of directory virtual env}
$ source .{name of directory virtual env}/bin/activate

# install all of requirements
$ pip install -r requirements.txt

# Download Model
$ ollama run granite3.2:8b

# Run 
$ python3 -m cmd.main --intercept-on
```

## 🗺️ Roadmap
- Full Linux and Windows support
- Train AI to detect more malicious url 
- more protection so it's Cannot be bypassed by threats
- User Activity so we can combined like UBA
- Export logs and alerts for SIEM/SOC workflows

## 🤝 Contributing
Contributions are welcome!
Whether it's bug fixes, new features, or AI rule enhancements.
