## Latinum Wallet MCP

A Model Context Protocol (MCP) server for interacting with the Latinum Wallet via the standard MCP interface.
This allows AI Agents like Claude or Cursor to pay for services.

### ✅ Installation

```bash
pip install latinum-wallet-mcp
```

### ⚙️ Claude Desktop Integration

To connect with Claude Desktop via MCP, add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "latinum_wallet_mcp": {
      "command": "latinum-wallet-mcp"
    }
  }
}
```

For example, place the config file at:

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### 🔐 License

This software is proprietary. All rights reserved to **Latinum Agentic Commerce**. Redistribution or reverse engineering is prohibited without explicit permission from the author.

Support: [dennj@latinum.ai](mailto:dennj@latinum.ai)
