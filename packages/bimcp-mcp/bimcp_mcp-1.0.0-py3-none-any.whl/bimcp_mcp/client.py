#!/usr/bin/env python3
"""
BIMCP MCP Client

Lightweight client that runs locally and forwards MCP requests to BIMCP Cloud.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# Configuration
API_KEY = os.environ.get("BIMCP_API_KEY")
API_URL = os.environ.get("BIMCP_API_URL", "https://python-bimcp.onrender.com")

if not API_KEY:
    print("Error: BIMCP_API_KEY environment variable required", file=sys.stderr)
    print("Get your API key at https://bimcp.com", file=sys.stderr)
    sys.exit(1)

# Logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("bimcp-mcp")

# Create server
app = Server("bimcp")

# HTTP client
client = httpx.AsyncClient(
    base_url=API_URL,
    headers={"Authorization": f"Bearer {API_KEY}"},
    timeout=30.0
)

@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available tools."""
    try:
        response = await client.post("/api/mcp/tools/list")
        response.raise_for_status()
        data = response.json()
        
        return [
            types.Tool(
                name=tool["name"],
                description=tool.get("description", ""),
                inputSchema=tool.get("inputSchema", {})
            )
            for tool in data.get("tools", [])
        ]
    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        return []

@app.call_tool()
async def call_tool(
    name: str, 
    arguments: dict
) -> List[types.TextContent]:
    """Call a tool."""
    try:
        response = await client.post(
            "/api/mcp/tools/call",
            json={"name": name, "arguments": arguments}
        )
        response.raise_for_status()
        data = response.json()
        
        return [
            types.TextContent(
                type="text",
                text=item.get("text", "")
            )
            for item in data.get("content", [])
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
        ]

@app.list_resources()
async def list_resources() -> List[types.Resource]:
    """List available resources."""
    try:
        response = await client.post("/api/mcp/resources/list")
        response.raise_for_status()
        data = response.json()
        
        return [
            types.Resource(
                uri=res["uri"],
                name=res.get("name", ""),
                description=res.get("description", "")
            )
            for res in data.get("resources", [])
        ]
    except Exception as e:
        logger.error(f"Failed to list resources: {e}")
        return []

@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource."""
    try:
        response = await client.post(
            "/api/mcp/resources/read",
            json={"uri": uri}
        )
        response.raise_for_status()
        data = response.json()
        
        contents = data.get("contents", [])
        if contents:
            return contents[0].get("text", "")
        return ""
    except Exception as e:
        return f"Error: {str(e)}"

async def run():
    """Run the MCP server."""
    try:
        async with stdio_server() as streams:
            await app.run(
                streams[0],
                streams[1],
                app.create_initialization_options()
            )
    finally:
        await client.aclose()

def main():
    """Entry point."""
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
