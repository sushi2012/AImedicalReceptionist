
from mcp.server.mcpserver import MCPServer as FastMCP

from app.tools.clinic_tools import (
    get_clinic_information,
    search_clinic_faq,
)

mcp = FastMCP("dental-clinic-tools")


@mcp.tool()
def get_clinic_info() -> dict:
    """Get clinic address, phone, working hours, services, and FAQs."""
    return get_clinic_information()


@mcp.tool()
def search_faq(question: str) -> dict:
    """Search clinic FAQs using a patient's question or alternative wording."""
    return search_clinic_faq(question)


if __name__ == "__main__":
    mcp.run(transport="stdio")
