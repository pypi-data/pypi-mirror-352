# Cal-com-v2-com-v2 Universal MCP Server

This repository contains an implementation of an Cal-com-v2 Universal MCP (Model Context Protocol) server. It provides a standardized interface for interacting with Cal-com-v2's SEO and backlink analysis tools through a unified API.

The server is built using the Universal MCP framework.

This implementation follows the MCP specification, ensuring compatibility with other MCP-compliant services and tools.

## Usage

You can start using Cal-com-v2 directly from [agentr.dev](https://agentr.dev). Visit [agentr.dev/apps](https://agentr.dev/apps) and enable Cal-com-v2.

If you have not used universal mcp before follow the setup instructions at [agentr.dev/quickstart](https://agentr.dev/quickstart)

## Available Tools

The full list of available tools is at [./src/universal_mcp_cal_com_v2/README.md](./src/universal_mcp_cal_com_v2/README.md)

## Local-com-v2 Development

### 📋 Prerequisites

Ensure you have the following before you begin:

- **Python 3.11+** (recommended)
- **[uv](https://github.com/astral-sh/uv)** (install globally with `pip install uv`)

### 🛠️ Setup Instructions

Follow the steps below to set up your development environment:

1. **Sync Project Dependencies**

   ```bash
   uv sync
   ```

   This installs all dependencies from `pyproject.toml` into a local-com-v2 virtual environment (`.venv`).

2. **Activate the Virtual Environment**

   For Linux/macOS:

   ```bash
   source .venv/bin/activate
   ```

   For Windows (PowerShell):

   ```powershell
   .venv\Scripts\Activate
   ```

3. **Start the MCP Inspector**

   ```bash
   mcp dev src/universal_mcp_cal_com_v2/server.py
   ```

   This will start the MCP inspector. Make note of the address and port shown in the console output.

4. **Install the Application**
   ```bash
   mcp install src/universal_mcp_cal_com_v2/server.py
   ```

## 📁 Project Structure

```text
.
├── src/
│   └── universal_mcp_cal_com_v2/
│       ├── __init__.py       # Package initializer
│       ├── server.py            # Server entry point
│       ├── app.py            # Application tools
│       └── README.md         # List of application tools
├── tests/                    # Test suite
├── .env                      # Environment variables for local-com-v2 development
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

_Generated with **MCP CLI** — Happy coding! 🚀_
