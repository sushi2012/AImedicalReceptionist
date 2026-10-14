import sys
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient

BACKEND_ROOT = Path(__file__).resolve().parents[2]

_client: MultiServerMCPClient | None = None


def get_mcp_client() -> MultiServerMCPClient:
    global _client

    if _client is None:
        _client = MultiServerMCPClient(
            {
                "clinic": {
                    "transport": "stdio",
                    "command": sys.executable,
                    "args": ["-m", "app.mcp_server.server"],
                    "cwd": str(BACKEND_ROOT),
                }
            }
        )

    return _client


async def get_clinic_tools():
    """Load LangChain tools exposed by the clinic MCP server."""
    return await get_mcp_client().get_tools()
