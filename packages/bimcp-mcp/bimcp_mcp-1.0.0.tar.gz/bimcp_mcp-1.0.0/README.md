# BIMCP MCP Client

Connect Claude Desktop to BIMCP Cloud Service for seamless Revit integration.

## Installation

Install using UV (recommended):

```bash
uvx bimcp-mcp
```

Or using pip:

```bash
pip install bimcp-mcp
```

## Getting Started

1. **Get your API key** from [https://bimcp.com/api-keys](https://bimcp.com/api-keys)

2. **Configure Claude Desktop**:
   
   Open Claude Desktop settings (Settings → Developer → Edit Config) and add:

   ```json
   {
     "mcpServers": {
       "bimcp": {
         "command": "uvx",
         "args": ["bimcp-mcp"],
         "env": {
           "BIMCP_API_KEY": "your-api-key-here"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

## Configuration Options

- `BIMCP_API_KEY` (required): Your BIMCP API key
- `BIMCP_API_URL` (optional): Custom API endpoint (default: https://api.bimcp.com)

## Features

- Execute C# code directly in Revit
- Access Revit model information
- Query elements (walls, doors, windows, etc.)
- Create and modify BIM elements
- Run structural analysis
- Generate schedules and reports

## Example Usage

Once configured, you can ask Claude:

- "Get information about the current Revit model"
- "Count all the walls in the project"
- "Create a new wall at coordinates..."
- "List all doors on Level 1"
- "Generate a door schedule"

## Troubleshooting

If you encounter issues:

1. Verify your API key is correct
2. Check your internet connection
3. Ensure Claude Desktop was restarted after configuration
4. Check the logs: `~/.claude/logs/`

## Support

- Documentation: [https://docs.bimcp.com](https://docs.bimcp.com)
- Support: support@bimcp.com
- Issues: [https://github.com/BIMCP/bimcp-mcp/issues](https://github.com/BIMCP/bimcp-mcp/issues)

## License

MIT License - See LICENSE file for details.
