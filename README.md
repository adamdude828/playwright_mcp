# Playwright MCP

A Model Context Protocol (MCP) server for controlling Playwright browser automation. This server implements the MCP specification and can be used with any MCP-compatible client.

## Installation

You can install directly from GitHub:

```bash
pip install -e git+https://github.com/adamdude828/playwright_mcp.git#egg=playwright_mcp
```

## Configuration

Create a `server_config.json` file with the following content:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "python",
      "args": [
        "-m",
        "playwright_mcp",
        "--mode",
        "server"
      ],
      "logging": {
        "level": "DEBUG"
      }
    }
  }
}
```

## Usage

This server can be used with any MCP-compatible client. Here's an example using [mcp-cli](https://github.com/adamdude828/mcp-cli):

```bash
# Install the example client
pip install -e git+https://github.com/adamdude828/mcp-cli.git#egg=mcp-cli
```

Once installed and configured:

1. List available servers:
```bash
mcp-cli list-servers
```

2. List available tools:
```bash
mcp-cli --server playwright list-tools
```

3. Start the browser daemon:
```bash
mcp-cli --server playwright --tool start-daemon call-tool
```

4. Navigate to a page:
```bash
mcp-cli --server playwright --tool navigate --tool-args '{"url": "https://example.com"}' call-tool
```

5. Stop the browser daemon:
```bash
mcp-cli --server playwright --tool stop-daemon call-tool
```

## Development

To run the integration tests:

```bash
pytest tests/integration/test_mcp_cli_setup.py -v
```

The tests verify:
- MCP CLI availability
- Playwright tool availability
- Browser daemon start/stop functionality
- Navigation capabilities 