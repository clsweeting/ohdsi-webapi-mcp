
## MCP Client Configuration

### Claude Desktop (HTTP mode)
Add this to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "ohdsi-webapi": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Note**: Make sure the HTTP server is running before starting Claude Desktop.
