from mcp.server.mcpserver import MCPServer

from app.tools.clinic_tools import (
    get_clinic_information,
    search_clinic_faq,
)

mcp = MCPServer(
    name="dental-clinic-tools",
    instructions=(
        "Tools for Sunshine Dental Clinic: hours, contact details, "
        "services, and FAQ lookup."
    ),
)

mcp.add_tool(get_clinic_information)
mcp.add_tool(search_clinic_faq)


if __name__ == "__main__":
    mcp.run(transport="stdio")
