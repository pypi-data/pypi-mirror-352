
from universal_mcp.servers import SingleMCPServer

from universal_mcp_http_tools.app import HttpToolsApp

app_instance = HttpToolsApp()

mcp = SingleMCPServer(
    app_instance=app_instance
)

if __name__ == "__main__":
    print(f"Starting {mcp.name}...")
    mcp.run(transport="sse")


