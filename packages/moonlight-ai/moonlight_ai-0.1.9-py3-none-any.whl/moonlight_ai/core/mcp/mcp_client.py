import asyncio
from mcp.types import Tool

from .mcp_connector import MCPConnector
from .mcp_config import MCPConfig

class MCPClientException(Exception):
    pass

class MCPClient:    
    def __init__(
            self, 
            config: MCPConfig, 
        ):
        
        self.config = config
        
        if not isinstance(self.config, MCPConfig):
            raise MCPClientException("Invalid config provided. Expected an instance of MCPConfig.")
        
        if not self.config:
            raise MCPClientException("No config provided.")
        
        self.connector = None
        self._tools = None
        self._loop = None
        self._connected = False
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        
    def connect(self):
        """Synchronous method to connect the client for non-context manager usage"""
        try:
            # Get or create an event loop
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
            
            # Add a global timeout to the connection process
            self._loop.run_until_complete(
                asyncio.wait_for(self._connect(), timeout=30.0)
            )
        except asyncio.TimeoutError:
            # Handle timeout specifically
            if hasattr(self, '_loop') and self._loop:
                self._loop.run_until_complete(self._disconnect())
            raise MCPClientException("Failed to initialize MCP client: Connection timed out")
        except Exception as e:
            # Ensure cleanup if connection fails
            if hasattr(self, '_loop') and self._loop:
                self._loop.run_until_complete(self._disconnect())
            # Provide a more informative error message
            error_msg = str(e)
            if not error_msg:
                error_msg = "Unknown error (empty error message)"
            raise MCPClientException(f"Failed to initialize MCP client: {error_msg}")
        
    def disconnect(self):
        """Synchronous method to disconnect the client for non-context manager usage"""
        if self._loop and self._connected:
            self._loop.run_until_complete(self._disconnect())
        
    async def _connect(self):
        if self._connected:
            return

        try:
            # Create and connect with the universal connector
            self.connector = MCPConnector(self.config)
            await self.connector.connect()
            
            # Initialize the session
            await self._initialize()
            self._connected = True
            
        except Exception as e:
            print(f"Connection failed: {e}")
            await self._cleanup_resources()
            raise
    
    async def _initialize(self):
        # Unified initialization using the connector's send_request method
        await self.connector.send_request("initialize")
        tools_result = await self.connector.send_request("tools/list")
        
        # Check if we have any tools at all
        if isinstance(tools_result.get("tools"), list):
            tools_list = tools_result.get("tools", [])
            if not tools_list:
                await self._cleanup_resources()
                raise MCPClientException("No tools available from the server")
            self._tools = [Tool(**tool) for tool in tools_list]
        elif hasattr(tools_result, "tools"):
            if not tools_result.tools:
                await self._cleanup_resources()
                raise MCPClientException("No tools available from the server")
            self._tools = tools_result.tools
        else:
            await self._cleanup_resources()
            raise MCPClientException("Failed to retrieve tools from server")
            
        return tools_result
        
    async def _disconnect(self):
        if not self._connected:
            return
            
        await self._cleanup_resources()
        self._connected = False
        
    async def _cleanup_resources(self):
        if self.connector:
            try:
                await self.connector.close()
            except Exception as e:
                print(f"Error during connector cleanup: {e}")
            finally:
                self.connector = None
                
        self._tools = None
        self._connected = False

    def discover_tools(self):
        if not self._connected:
            raise MCPClientException("MCP client is not connected. Call connect() first.")
        if not self._tools:
            raise MCPClientException("MCP client is not initialized")
        return self._tools

    def call_tool(self, name, arguments):
        if not self._connected:
            raise MCPClientException("MCP client is not connected. Call connect() first.")
            
        try:
            print(f"Attempting to call tool: {name}")
            return self._loop.run_until_complete(self._call_tool_async(name, arguments))
        except Exception as e:
            print(f"Exception in call_tool outer handler: {e}")
            if self._connected:
                print(f"Connection still active, attempting disconnect")
                self._loop.run_until_complete(self._disconnect())
            else:
                print(f"Connection already marked as not connected")
            raise MCPClientException(f"Error calling tool '{name}': {e}")
        
    async def _call_tool_async(self, name, arguments):
        # Check if the tool exists before calling it
        tool_exists = False
        if self._tools:
            for tool in self._tools:
                if getattr(tool, "name", None) == name:
                    tool_exists = True
                    break
        
        if not tool_exists:
            await self._cleanup_resources()
            raise MCPClientException(f"Tool '{name}' not found in available tools")

        # Call the tool if it exists
        try:
            return await self.connector.send_request("tools/call", {"name": name, "arguments": arguments})
        except Exception as e:
            await self._cleanup_resources()
            raise MCPClientException(f"Error calling tool '{name}': {e}")
            
    def list_resources(self):
        if not self._connected:
            raise MCPClientException("MCP client is not connected. Call connect() first.")
            
        try:
            return self._loop.run_until_complete(self._list_resources_async())
        except Exception as e:
            # Auto-close context on error
            if self._connected:
                self._loop.run_until_complete(self._disconnect())
            raise MCPClientException(f"Error listing resources: {e}")
        
    async def _list_resources_async(self):
        try:
            return await self.connector.send_request("resources/list")
        except Exception as e:
            await self._cleanup_resources()
            raise MCPClientException(f"Error listing resources: {e}")
            
    def read_resource(self, uri):
        if not self._connected:
            raise MCPClientException("MCP client is not connected. Call connect() first.")
            
        try:
            return self._loop.run_until_complete(self._read_resource_async(uri))
        except Exception as e:
            # Auto-close context on error
            if self._connected:
                self._loop.run_until_complete(self._disconnect())
            raise MCPClientException(f"Error reading resource '{uri}': {e}")
        
    async def _read_resource_async(self, uri):
        try:
            result = await self.connector.send_request("resources/read", {"uri": uri})
            if isinstance(result, dict):
                return result.get("content", b""), result.get("mimeType", "")
            else:
                return result.content, result.mimeType
        except Exception as e:
            await self._cleanup_resources()
            raise MCPClientException(f"Error reading resource '{uri}': {e}")