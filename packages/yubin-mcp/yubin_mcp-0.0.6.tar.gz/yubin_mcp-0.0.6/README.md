# YUBIN MCP

MCP server that retrieves addresses and map links from Japanese postal codes and latitude/longitude coordinates

## Installation

```bash
pip install yubin-mcp
```

## Usage

### Use with Claude Desktop

1. Install the MCP server

```bash
pip install yubin-mcp
```

2. Open the configuration file
```bash
open /path/to/Claude/claude_desktop_config.json
```

3. Add the following configuration to the configuration file

```json
{
  "mcpServers": {
    "yubin-mcp": {
      "command": "python",
      "args": [
        "-m",
        "yubin_mcp.server"
      ],
      "env": {},
      "transport": "stdio"
    }
  }
}
```
