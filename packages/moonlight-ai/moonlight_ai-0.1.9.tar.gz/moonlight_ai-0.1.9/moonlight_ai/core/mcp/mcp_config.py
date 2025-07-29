import json, subprocess, re
from rich.console import Console

console = Console()

class MCPConfigException(Exception):
    pass

class MCPConfig:
    def __init__(
        self,
        
        # Entire Config
        config: dict = {},
        
        # MCP Server Name and Description
        name: str = "",
        description: str = "",
        tags: list = [],
        version: str = "",
        
        # MCP Args and ENV
        args: list = [],
        env: dict = {},
        required_envs: list = [],
        needs_envs: bool = False,
        
        # MCP Command/URL
        command: str = "",
        url: str = "",
        ws_url: str = "",
        
        # MCP Headers
        headers: dict = {},
        auth_token: str = ""
    ):
        # Entire Config
        self.config = config
            
        # Can't have both config and other parameters set
        if self.config and (self.name or self.description or self.args or self.env or self.command or self.url or self.ws_url or self.headers or self.auth_token):
            raise MCPConfigException("Cannot have both config and other parameters set.")

        # Check if config is a string and unpack it
        self._unpack_config()
        
        # MCP Server Config
        self.name = name
        self.description = description
        self.tags = tags
        self.version = version
        
        # MCP Args and ENV
        self.args = args
        self.env = env
        self.required_envs = required_envs
        self.needs_envs = needs_envs
        
        # MCP Command/URL
        self.command = command
        self.url = url
        self.ws_url = ws_url
        
        # MCP Headers
        self.headers = headers
        self.auth_token = auth_token
        
        if not self.config and (not self.url and not self.command):
            raise MCPConfigException("Must have either config or other parameters set.")
        
        # CLean and check config
        self._check_mcp_config()
        
    def _check_mcp_config(self):
        """
        Check if the config is valid and unpack it. Then check if the parameters are valid and clean the command.
        """
                
        # Check if parameters are valid
        self._check_parameters()
        
        # Assign connector type
        self._determine_connector_type()
        
        # Clean command
        self._clean_command()
        
    def _unpack_config(self):
        """
        Unpack the config and check if it is valid. If it is a string, try to load it as JSON.
        """
        
        # No need to unpack if config is empty
        if (not self.config) or (self.config == {}) or (self.config == ""): return
        
        if isinstance(self.config, str):
            try:
                self.config = json.loads(self.config)
            except json.JSONDecodeError:
                raise MCPConfigException("Invalid JSON string provided for config.")
    
        if not isinstance(self.config, dict):
            raise MCPConfigException("Config must be a dictionary or a valid JSON string.")
        
        if "mcpServers" not in self.config:
            raise MCPConfigException("Config must contain 'mcpServers' key")
        
        if not isinstance(self.config["mcpServers"], dict):
            raise MCPConfigException("'mcpServers' must be a dictionary")
        
        if len(self.config["mcpServers"]) == 0:
            raise MCPConfigException("No MCP servers found in config.")
        
        if len(self.config["mcpServers"]) > 1:
            raise MCPConfigException("Multiple MCP servers found in config. Please specify one.")
        
        # Unpack the first server
        self.name = next(iter(self.config["mcpServers"]))
        self.description = self.config["mcpServers"][self.name].get("description", "")
        self.args = self.config["mcpServers"][self.name].get("args", [])
        self.env = self.config["mcpServers"][self.name].get("env", {})
        self.command = self.config["mcpServers"][self.name].get("command", "")
        self.url = self.config["mcpServers"][self.name].get("url", "")
        self.ws_url = self.config["mcpServers"][self.name].get("ws_url", "")
        self.headers = self.config["mcpServers"][self.name].get("headers", {})
        self.auth_token = self.config["mcpServers"][self.name].get("auth_token", "")
        
        sanitized_server_name = self.name.strip().lower()
        self.name = re.sub(r'[^a-z0-9_]', '_', sanitized_server_name)
    
    def _check_parameters(self):
        """
        Check if the parameters are valid and clean them. This includes checking if the command is valid, if the URL is valid, and if the headers are valid.
        """
        
        if not self.name or not self.description:
            raise MCPConfigException("Name and description are required.")
        
        # Strip trailing slashes from URL
        self.url = self.url.rstrip("/")
        
        # Add auth token to headers if provided
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token}"
        
        if not self.env: self.env = {}
        
        # Define default environment variables
        default_envs = ["FORCE_COLOR", "DISPLAY", "PYTHONUNBUFFERED", "DEBIAN_FRONTEND"]
        
        # Extract required environment variables (non-default ones)
        if not self.required_envs:  # Only recalculate if not provided
            self.required_envs = [key for key in self.env.keys() if key not in default_envs]
            self.needs_envs = len(self.required_envs) > 0
        
        # Set default environment variables
        self.env["FORCE_COLOR"] = "0"
        self.env["DISPLAY"] = ":0"
        self.env["PYTHONUNBUFFERED"] = "1"
        self.env["DEBIAN_FRONTEND"] = "noninteractive"
        
        # Ensure command, url, and ws_url are not all set
        if self.command and self.url and self.ws_url:
            raise MCPConfigException("Cannot have both command and url set.")
        
        # Ensure URL is SSE
        if self.url:
            if not self.url.endswith("/sse"):
                raise MCPConfigException("MCP Supports only SSE URLs for now.")
        
        # Ensure args are set if command is given
        if self.command and not self.args:
            raise MCPConfigException("Command must have args set.")
        
        # Ensure at least one of command, url, or ws_url is set
        if not self.command and not self.url and not self.ws_url:
            raise MCPConfigException("Must have either command or url set.")
    
    def get_required_envs(self):
        """
        Get the required environment variables for the MCP client. This is used to get the required environment variables for the MCP client.
        """
        
        if not self.needs_envs:
            raise MCPConfigException("No required environment variables found.")
        
        # Return the required environment variables
        return self.required_envs
    
    def set_required_envs(self, envs: dict):
        """
        Get ENVS for the REQUIRED_ENVs. This is used to set the required environment variables for the MCP client.
        """
        
        if not self.needs_envs:
            raise MCPConfigException("No required environment variables found.")
        
        # Check if envs is a dictionary
        if not isinstance(envs, dict):
            raise MCPConfigException("Environment variables must be a dictionary.")
        
        # Check if all required environment variables are present
        for key in self.required_envs:
            if key not in envs:
                raise MCPConfigException(f"Missing required environment variable: {key}")
        
        # Set the environment variables
        self.env.update(envs)
        
    def _determine_connector_type(self):
        """
        Determine the connector type based on the provided parameters. This is used to set the connector type for the MCP client.
        Available types are: command, url, and ws_url.
        """
        
        self.TYPE_WEBSOCKET = False
        self.TYPE_HTTP = False
        self.TYPE_STDIO = False
        
        if self.command and (not self.command == ""):
            self.TYPE_STDIO = True
            self.connector_type = "stdio"
        elif self.url and (not self.url == ""):
            self.TYPE_HTTP = True
            self.connector_type = "http"
        elif self.ws_url and (not self.ws_url == ""):
            self.TYPE_WEBSOCKET = True
            self.connector_type = "websocket"
        else:
            raise MCPConfigException("No valid connector type found.")
    
    def _python_to_uvx(self):
        """
        Convert Python command to UVX command and verify/install module in uvx environment.
        Checks module existence in uvx and tries dashed/underscored variants. Raises exception if not found/installable.
        """
        
        # Find module name from args with proper detection
        module_name = None
        
        # For Python commands, look for arg after -m
        if self.command == "python":
            for i, arg in enumerate(self.args):
                if arg == "-m" and i+1 < len(self.args):
                    module_name = self.args[i+1]
                    break
        
        # If no module found via -m, find first non-flag argument
        if not module_name:
            for arg in self.args:
                if not arg.startswith("-"):
                    module_name = arg
                    break
        
        if not module_name:
            raise MCPConfigException("Could not identify module name from arguments.")
        
        print(f"Python is not reliable for MCP. Shifting to 'uvx' command.")
        
        # Change the command to uvx
        self.command = "uvx"
        
        # If the args contained -m, remove it and what follows (we extracted module_name already)
        if "-m" in self.args:
            idx = self.args.index("-m")
            if idx + 1 < len(self.args):
                self.args = self.args[:idx] + self.args[idx + 2:]
            else:
                self.args = self.args[:idx]
        
        # Check various naming conventions
        dash_to_under = module_name.replace("-", "_")
        under_to_dash = module_name.replace("_", "-")
        
        # Step 1: Check if module exists in uvx environment
        for name in [module_name, dash_to_under, under_to_dash]:
            try:
                subprocess.run(
                    ["uvx", "run", "--quiet", name, "--version"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                print(f"Module '{name}' exists in uvx environment.")
                return
            except subprocess.CalledProcessError:
                pass
        
        # Step 2: Try installing with uvx using different naming conventions
        for name in [module_name, dash_to_under, under_to_dash]:
            try:
                print(f"Attempting to install '{name}' with uvx...")
                subprocess.run(
                    ["uvx", "install", name],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                print(f"Successfully installed '{name}' with uvx.")
                return
            except subprocess.CalledProcessError:
                print(f"Failed to install '{name}' with uvx.")
        
        # Step 3: All installation attempts failed
        print(f"Failed to install module '{module_name}' after all attempts.")
        raise MCPConfigException(f"Failed to install module '{module_name}'. Check the configuration.")
        
    def _clean_command(self):
        """
        Clean the command and check if it is valid. This includes checking if the command is allowed and if the arguments are valid.
        """
        
        # If no command is set, return
        if not self.command: return
    
        # Allowed and disallowed commands
        self.allowed_commands = [
            "uvx", 
            "npx",
            "python", 
            "docker",
            "node"
        ]
        
        self.disallowed_commands = [
            "curl", 
            "wget", 
            "ssh"
        ]
        
        # Special case for Python command
        if self.command == "python":
            if len(self.args) == 0:
                raise MCPConfig("Python command requires at least one argument")
            if not self.args[0] == "-m":
                raise MCPConfig("Python command requires '-m' argument")
            if len(self.args) < 2:
                raise MCPConfig("Python command requires a module name after '-m'")
            
            # Convert Python command to UVX command if python is not reliable.
            # self._python_to_uvx()
        
        # Check for module if command is uvx
        if self.command == "uvx":
            if len(self.args) == 0:
                raise MCPConfigException("UVX command requires at least one argument")
        
        # Check if command is allowed or disallowed
        if self.command in self.disallowed_commands:
            raise MCPConfigException(f"Command '{self.command}' is not allowed.")
        
        if self.command not in self.allowed_commands:
            raise MCPConfigException(f"Command '{self.command}' is not allowed. Allowed commands: {self.allowed_commands}")
        
    def __repr__(self):
        console.print()
        console.print("[bold green]╭─────────────────────────────────────────╮[/bold green]")
        console.print("[bold green]│            MCP Configuration            │[/bold green]")
        console.print("[bold green]╰─────────────────────────────────────────╯[/bold green]")
        
        # Basic info section
        console.print("[bold magenta]┌ Basic Information[/bold magenta]")
        console.print(f"│ [yellow]Name:[/yellow] {self.name}")
        if self.description:
            console.print(f"│ [yellow]Description:[/yellow] {self.description}")
        if self.tags:
            console.print(f"│ [yellow]Tags:[/yellow] {', '.join(self.tags)}")
        if self.version:
            console.print(f"│ [yellow]Version:[/yellow] {self.version}")
        console.print("└─────────────────")
        
        # Connection details
        console.print("[bold cyan]┌ Connection Details[/bold cyan]")
        console.print(f"│ [green]Type:[/green] {self.connector_type}")
        
        if self.command:
            cmd_str = f"{self.command} {' '.join(self.args)}" if self.args else self.command
            console.print(f"│ [green]Command:[/green] {cmd_str}")
        if self.url:
            console.print(f"│ [green]URL:[/green] {self.url}")
        if self.ws_url:
            console.print(f"│ [green]WebSocket:[/green] {self.ws_url}")
        console.print("└─────────────────")
        
        # Environment variables
        if self.needs_envs and self.required_envs:
            console.print("[bold yellow]┌ Required Environment Variables[/bold yellow]")
            for key in self.required_envs:
                value = self.env.get(key, "**")
                console.print(f"│ [magenta]{key}:[/magenta] {value}")
            console.print("└─────────────────")
        
        # Headers
        if self.headers:
            console.print("[bold red]┌ Headers[/bold red]")
            for key, value in self.headers.items():
                if key == "Authorization" and value.startswith("Bearer "):
                    console.print(f"│ [cyan]{key}:[/cyan] Bearer ***")
                else:
                    console.print(f"│ [cyan]{key}:[/cyan] {value}")
            console.print("└─────────────────")
        
        console.print()
        return ""