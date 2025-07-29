import asyncio, json, uuid, websockets

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client

from .mcp_config import MCPConfig

class MCPConnectorException(Exception):
    pass

class MCPConnector:
    def __init__(
            self, 
            config: MCPConfig
        ):
        """
        Initialize the appropriate connector based on configuration
        """
        
        if not isinstance(config, MCPConfig):
            raise MCPConnectorException("Invalid config provided. Expected an instance of MCPConfig.")
        
        self.config = config
        
        # Common properties
        self.ws = None
        self.receiver_task = None
        self.pending_requests = {}
        
        # HTTP specific properties
        self.timeout = 5
        self.sse_read_timeout = 300
        
        # Common properties for HTTP and stdio
        self.context = None
        self.client_session = None
        self.connection_task = None
        
    async def connect(self):
        """
        Connect using the appropriate protocol based on configuration
        """
        
        if self.config.TYPE_WEBSOCKET:
            print("Connecting to WebSocket...")
            return await self._connect_websocket()
        elif self.config.TYPE_HTTP:
            return await self._connect_http()
        elif self.config.TYPE_STDIO:
            return await self._connect_stdio()
    
    async def _connect_websocket(self):
        """
        Establish WebSocket connection
        """
        
        try:
            self.ws = await websockets.connect(
                self.config.ws_url, 
                extra_headers=self.config.headers
            )
            
            self.receiver_task = asyncio.create_task(
                self._receive_messages()
            )
            
            return True
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
            return False
    
    async def _receive_messages(self):
        """
        Handle incoming WebSocket messages
        """
        
        if not self.ws:
            return
            
        try:
            async for message in self.ws:
                data = json.loads(message)
                request_id = data.get("id")
                
                # Handle response to a pending request
                if request_id and request_id in self.pending_requests:
                    future = self.pending_requests.pop(request_id)
                    if "result" in data:
                        future.set_result(data["result"])
                    elif "error" in data:
                        future.set_exception(Exception(data["error"]))
        except Exception as e:
            # Reject all pending requests on connection failure
            for future in self.pending_requests.values():
                if not future.done():
                    future.set_exception(e)
    
    async def _connect_stdio(self):
        """
        Establish stdio connection to the MCP server
        """

        server_params = StdioServerParameters(
            command=self.config.command, 
            args=self.config.args, 
            env=self.config.env
        )
        
        ready_event = asyncio.Event()
        error_container = [None]

        async def run_connection():
            ctx = None
            try:
                # Create the context without redirecting stderr in a way that breaks fileno
                ctx = stdio_client(
                    server_params, 
                    None  # Don't pass sys.stderr here - let the process use default stderr
                )
                
                read_stream, write_stream = await ctx.__aenter__()
                
                # Create client session
                self.client_session = ClientSession(
                    read_stream, 
                    write_stream, 
                    sampling_callback=None
                )
                
                # Try to initialize and check for errors
                try:
                    await self.client_session.__aenter__()
                    
                    # Early validation - try a quick command to validate connection
                    await asyncio.wait_for(
                        self.client_session.initialize(),
                        timeout=5.0
                    )
                    
                except Exception as e:
                    error_container[0] = e
                    ready_event.set()
                    return
                
                # Store context
                self.context = ctx
                
                # Signal readiness
                ready_event.set()
                
                # Keep alive until cancelled
                await asyncio.Future()
                    
            except Exception as e:
                error_container[0] = e
                ready_event.set()
            finally:
                # Connection cleanup handled in close method when task is cancelled
                pass
        
        # Start connection task
        self.connection_task = asyncio.create_task(
            run_connection()
        )
        
        # Wait for ready event with timeout
        try:
            await asyncio.wait_for(
                ready_event.wait(), 
                timeout=20.0
            )
        except asyncio.TimeoutError:
            if self.connection_task and not self.connection_task.done():
                self.connection_task.cancel()
            raise MCPConnectorException("Connection timed out after 20 seconds")
            
        # Propagate any error that occurred
        if error_container[0]:
            if self.connection_task and not self.connection_task.done():
                self.connection_task.cancel()
            raise MCPConnectorException(f"Connection failed: {str(error_container[0])}")
        
        return True
    
    async def _connect_http(self):
        """
        Establish HTTP/SSE connection
        """
        
        ready_event = asyncio.Event()
        error_container = [None]
        
        async def run_connection():
            ctx = None
            try:
                # Create and enter context manager
                ctx = sse_client(
                    url=self.config.url, 
                    headers=self.config.headers, 
                    timeout=self.timeout,
                    sse_read_timeout=self.sse_read_timeout
                )
                
                read_stream, write_stream = await ctx.__aenter__()
                
                # Create client session
                self.client_session = ClientSession(
                    read_stream, 
                    write_stream, 
                    sampling_callback=None
                )
                
                await self.client_session.__aenter__()
                
                # Store context
                self.context = ctx
                
                # Signal readiness
                ready_event.set()
                
                # Keep alive until cancelled
                await asyncio.Future()
                
            except Exception as e:
                import traceback
                error_container[0] = (e, traceback.format_exc())
                ready_event.set()
            finally:
                pass
        
        # Create and start connection task
        self.connection_task = asyncio.create_task(run_connection())
        
        # Wait for connection to be established or fail
        await ready_event.wait()
        
        # Propagate any error that occurred
        if error_container[0]:
            exception, tb = error_container[0]
            print(f"HTTP connection error details:\n{tb}")
            raise MCPConnectorException(f"HTTP connection failed: {exception}")
        
        return True
    
    async def send_request(
            self, 
            method: str, 
            params: dict = {}
        ):
        """
        Send a request using the appropriate protocol
        """
        
        try:
            if self.config.TYPE_WEBSOCKET:
                return await self._send_websocket_request(
                    method=method, 
                    params=params
                )
            else:
                # For HTTP and stdio, use client_session methods based on method name
                if method == "initialize":
                    return await self.client_session.initialize()
                
                elif method == "tools/list":
                    result = await self.client_session.list_tools()
                    return {
                        "tools": [tool.__dict__ for tool in result.tools]
                    }
                    
                elif method == "tools/call":
                    # Apply timeout to tool calls to prevent hanging
                    try:
                        return await asyncio.wait_for(
                            self.client_session.call_tool(
                                params["name"], 
                                params["arguments"]
                            ),
                            timeout=60.0  # 60-second timeout for tool calls
                        )
                    except asyncio.TimeoutError:
                        raise MCPConnectorException(f"Tool call '{params['name']}' timed out")
                    
                elif method == "resources/list":
                    return await self.client_session.list_resources()
                
                elif method == "resources/read":
                    resource = await self.client_session.read_resource(params["uri"])
                    return {
                        "content": resource.content, 
                        "mimeType": resource.mimeType
                    }
                    
                else:
                    raise MCPConnectorException(f"Unknown method: {method}")
                
        except Exception as e:
            raise MCPConnectorException(f"Request failed: {str(e)}")
    
    async def _send_websocket_request(self, method, params=None):
        """
        Send a WebSocket request and wait for response
        """
        
        if not self.ws:
            raise MCPConnectorException("WebSocket is not connected")

        request_id = str(uuid.uuid4())
        future = asyncio.Future()
        self.pending_requests[request_id] = future
        
        await self.ws.send(json.dumps({
            "id": request_id, 
            "method": method, 
            "params": params or {}
        }))

        try:
            # Add timeout to prevent indefinite waiting
            return await asyncio.wait_for(future, timeout=30.0)
        
        except asyncio.TimeoutError:
            self.pending_requests.pop(request_id, None)
            raise MCPConnectorException(f"Request '{method}' timed out")
        
        except Exception as e:
            print(f"Error while waiting for response: {e}")
            self.pending_requests.pop(request_id, None)
            raise MCPConnectorException(f"Request failed: {e}")
    
    async def close(self):
        """
        Close the connection using the appropriate method
        """
        
        if self.config.TYPE_WEBSOCKET:
            await self._close_websocket()
        elif self.config.TYPE_HTTP:
            await self._close_http_stdio()
        elif self.config.TYPE_STDIO:
            await self._close_http_stdio()
    
    async def _close_websocket(self):
        """
        Close WebSocket connection
        """
        
        if self.receiver_task and not self.receiver_task.cancelled():
            self.receiver_task.cancel()
            
            try:
                await asyncio.shield(asyncio.wait_for(
                    asyncio.gather(
                        self.receiver_task, 
                        return_exceptions=True
                    ),
                    timeout=1.0
                ))
                
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass
                
        # Clean up pending requests
        for future in list(self.pending_requests.values()):
            if not future.done():
                future.set_exception(ConnectionError("Connection closed"))
                
        self.pending_requests.clear()
            
        # Close WebSocket connection
        if self.ws:
            try:
                await self.ws.close()
            except Exception:
                pass
            finally:
                self.ws = None
    
    async def _close_http_stdio(self):
        """
        Close HTTP or Stdio connection
        """
        
        # Ensure proper cleanup of the context manager
        if self.context:
            try:
                await self.context.__aexit__(None, None, None)
            except Exception:
                pass
            finally:
                self.context = None
                
        # Ensure proper cleanup of the client session
        if self.client_session:
            try:
                await self.client_session.__aexit__(None, None, None)
            except Exception:
                pass
            finally:
                self.client_session = None
                
        # Carefully cancel connection task
        if self.connection_task and not self.connection_task.done():
            self.connection_task.cancel()
            try:
                await asyncio.shield(asyncio.wait_for(
                    asyncio.gather(self.connection_task, return_exceptions=True),
                    timeout=1.0
                ))
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass
            finally:
                self.connection_task = None
