# mcp_server.py
from mcp import MCPServer
from api_client import VisceralosAPIClient
from config import MCP_PORT, MCP_TRANSPORT

class WorkspaceConnector:
    def __init__(self):
        self.server = MCPServer()
        self.api_client = VisceralosAPIClient()
        self.register_tools()
        self.register_resources()
    
    def register_tools(self):
        """Register the workspace creation tool with the MCP server"""
        
        @self.server.tool()
        async def create_workspace(title: str):
            """Create a new workspace for organizing surveys and other content.
            
            Args:
                title (str): The name of the workspace to create
                
            Returns:
                dict: Information about the created workspace including its ID
            """
            try:
                # Call the API client
                response = self.api_client.create_workspace(title)
                
                # Extract workspace information from the response
                workspace = response.get("workspace", {})
                
                return {
                    "success": True,
                    "workspace_id": workspace.get("id"),
                    "workspace_title": workspace.get("title"),
                    "message": f"Workspace '{title}' created successfully"
                }
            except Exception as e:
                print(f"Error creating workspace: {str(e)}")
                return {
                    "success": False,
                    "error": str(e)
                }
    
    def register_resources(self):
        """Register resources that provide context to AI models"""
        
        @self.server.resource()
        async def platform_info():
            """Information about the Visceralos platform"""
            return {
                "name": "Visceralos Workspace Creator",
                "description": "Creates workspaces on the Visceralos platform",
                "capabilities": [
                    "Create workspaces to organize content"
                ]
            }
    
    async def start(self):
        """Start the MCP server"""
        print(f"Starting MCP server on port {MCP_PORT} with {MCP_TRANSPORT} transport")
        await self.server.start(transport=MCP_TRANSPORT, port=MCP_PORT)

# Run the server
if __name__ == "__main__":
    import asyncio
    
    async def main():
        connector = WorkspaceConnector()
        await connector.start()
    
    asyncio.run(main())