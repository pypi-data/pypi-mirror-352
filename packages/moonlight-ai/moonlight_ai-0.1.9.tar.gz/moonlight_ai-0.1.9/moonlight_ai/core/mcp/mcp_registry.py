import asyncio, json, sqlite3, os
from typing import List, Dict, Set, Optional, Tuple, Any
from contextlib import contextmanager
from pathlib import Path

from rich.console import Console
from rich.table import Table

from . import MCPClient, MCPConfig

console = Console()

class MCPRegistryException(Exception): pass

@contextmanager
def get_moonlight_db_connection():
    """
    Context manager for Moonlight (curated) SQLite database connections
    """
    # Get the directory where this Python file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "moonlight_db.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_user_db_connection(user_db_path: str = None):
    """
    Context manager for User SQLite database connections
    """
    if user_db_path is None:
        # Default to current working directory
        user_db_path = os.path.join(os.getcwd(), "user_mcp_registry.db")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(user_db_path)), exist_ok=True)
    
    conn = sqlite3.connect(user_db_path)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    try:
        yield conn
    finally:
        conn.close()

def init_database(get_connection_func):
    """Initialize a SQLite database with required tables"""
    with get_connection_func() as conn:
        cursor = conn.cursor()
        
        # Create mcps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mcps (
                name TEXT PRIMARY KEY,
                description TEXT,
                command TEXT,
                args TEXT,
                required_envs TEXT,
                needs_envs BOOLEAN,
                url TEXT,
                ws_url TEXT,
                headers TEXT,
                auth_token TEXT,
                tags TEXT,
                version TEXT,
                source TEXT DEFAULT 'unknown'
            )
        ''')
        
        # Create tool_index table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_index (
                tool_name TEXT,
                mcp_name TEXT,
                PRIMARY KEY (tool_name, mcp_name),
                FOREIGN KEY (mcp_name) REFERENCES mcps (name) ON DELETE CASCADE
            )
        ''')
        
        # Create tag_index table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tag_index (
                tag TEXT,
                mcp_name TEXT,
                PRIMARY KEY (tag, mcp_name),
                FOREIGN KEY (mcp_name) REFERENCES mcps (name) ON DELETE CASCADE
            )
        ''')
        
        # Create tool_cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_cache (
                mcp_name TEXT PRIMARY KEY,
                tools TEXT,
                FOREIGN KEY (mcp_name) REFERENCES mcps (name) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()

class MCPRegistry:
    """
    Registry for Model Context Protocol servers.
    Allows registering, searching, and managing MCP configurations.
    Supports dual database system: moonlight_db for curated MCPs and user_db for user-added MCPs.
    """
    
    _instance = None  # Singleton instance
    
    def __new__(cls, user_db: str = None):
        """
        Implement singleton pattern with user_db parameter
        """
        if cls._instance is None:
            cls._instance = super(MCPRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, user_db: str = None):
        """
        Initialize the registry if not already initialized
        
        Args:
            user_db: Path to user database file. If None, uses "user_mcp_registry.db" in current directory
        """
        if self._initialized:
            return
            
        # Set user database path
        self.user_db_path = user_db or os.path.join(os.getcwd(), "user_mcp_registry.db")
        
        # Registry storage
        self._mcps: Dict[str, MCPConfig] = {}
        self._tools_index: Dict[str, Set[str]] = {}
        self._tag_index: Dict[str, Set[str]] = {}
                
        # Cache of tool availability per MCP
        self._tool_cache: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize both databases
        init_database(get_moonlight_db_connection)
        init_database(lambda: get_user_db_connection(self.user_db_path))
        
        # Mark as initialized
        self._initialized = True
        
        # Load from both databases
        self._load_from_dbs()
        
        # Load curated MCPs from storage
        self._load_curated_mcps()

    def _load_from_dbs(self) -> None:
        """
        Load registry data from both databases
        """
        try:
            # Clear existing data
            self._mcps.clear()
            self._tools_index.clear()
            self._tag_index.clear()
            self._tool_cache.clear()
            
            # Load from moonlight (curated) database first
            self._load_from_db(get_moonlight_db_connection, "moonlight")
            
            # Load from user database
            self._load_from_db(lambda: get_user_db_connection(self.user_db_path), "user")
            
            total_mcps = len(self._mcps)
            moonlight_count = sum(1 for config in self._mcps.values() if hasattr(config, '_source') and config._source == "moonlight")
            user_count = total_mcps - moonlight_count
            
            console.print(f"[green]Loaded {total_mcps} MCPs total: {moonlight_count} curated, {user_count} user-added[/green]")
        
        except Exception as e:
            console.print(f"[red]Failed to load MCP registry from databases: {str(e)}[/red]")
            raise MCPRegistryException(f"Failed to load MCP registry from databases: {str(e)}")
    
    def _load_from_db(self, get_connection_func, source_type: str) -> None:
        """
        Load registry data from a specific database
        
        Args:
            get_connection_func: Function that returns database connection
            source_type: Either "moonlight" or "user"
        """
        try:
            with get_connection_func() as conn:
                cursor = conn.cursor()
                
                # Load MCPs
                cursor.execute('SELECT * FROM mcps')
                for row in cursor.fetchall():
                    # Convert row to MCPConfig
                    config_dict = {
                        "name": row["name"],
                        "description": row["description"] or "",
                        "command": row["command"] or "",
                        "args": json.loads(row["args"]) if row["args"] else [],
                        "required_envs": json.loads(row["required_envs"]) if row["required_envs"] else [],
                        "needs_envs": bool(row["needs_envs"]),
                        "url": row["url"] or "",
                        "ws_url": row["ws_url"] or "",
                        "headers": json.loads(row["headers"]) if row["headers"] else {},
                        "auth_token": row["auth_token"] or "",
                        "tags": json.loads(row["tags"]) if row["tags"] else [],
                        "version": row["version"] or ""
                    }
                    mcp_config = MCPConfig(**config_dict)
                    # Mark the source for internal tracking
                    mcp_config._source = source_type
                    self._mcps[row["name"]] = mcp_config
                
                # Load tool index
                cursor.execute('SELECT tool_name, mcp_name FROM tool_index')
                for row in cursor.fetchall():
                    tool_name = row["tool_name"]
                    mcp_name = row["mcp_name"]
                    if tool_name not in self._tools_index:
                        self._tools_index[tool_name] = set()
                    self._tools_index[tool_name].add(mcp_name)
                
                # Load tag index
                cursor.execute('SELECT tag, mcp_name FROM tag_index')
                for row in cursor.fetchall():
                    tag = row["tag"]
                    mcp_name = row["mcp_name"]
                    if tag not in self._tag_index:
                        self._tag_index[tag] = set()
                    self._tag_index[tag].add(mcp_name)
                
                # Load tool cache
                cursor.execute('SELECT mcp_name, tools FROM tool_cache')
                for row in cursor.fetchall():
                    tools_data = json.loads(row["tools"]) if row["tools"] else []
                    self._tool_cache[row["mcp_name"]] = tools_data
                    
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load from {source_type} database: {str(e)}[/yellow]")
    
    def _load_curated_mcps(self) -> None:
        """
        Load curated MCPs from the mcp_registry_storage.json file
        """
        try:
            # Path to the curated MCP storage
            storage_path = Path(__file__).parent.parent.parent / "mcp_servers" / "mcp_registry_storage.json"
            
            if not storage_path.exists():
                console.print(f"[yellow]Warning: Curated MCP storage not found at {storage_path}[/yellow]")
                return
            
            with open(storage_path, 'r', encoding='utf-8') as f:
                curated_data = json.load(f)
            
            # Convert to MCPConfig objects and store in moonlight database
            curated_configs = []
            for entry in curated_data:
                if 'server_config' in entry:
                    config = entry['server_config']
                    mcp_config = MCPConfig(
                        name=entry.get('server_name', ''),
                        description=config.get('description', ''),
                        command=config.get('command', ''),
                        args=config.get('args', []),
                        required_envs=list(config.get('env', {}).keys()),
                        needs_envs=bool(config.get('env')),
                        url=config.get('url', ''),
                        ws_url=config.get('ws_url', ''),
                        headers=config.get('headers', {}),
                        auth_token=config.get('auth_token', ''),
                        tags=config.get('tags', []),
                        version=config.get('version', '')
                    )
                    curated_configs.append(mcp_config)
            
            # Replace all curated MCPs in moonlight database
            self._replace_moonlight_mcps(curated_configs)
            
            console.print(f"[blue]📦 Loaded {len(curated_configs)} curated MCPs from storage[/blue]")
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load curated MCPs: {str(e)}[/yellow]")
    
    def _replace_moonlight_mcps(self, curated_mcps: List[MCPConfig]) -> None:
        """
        Replace all MCPs in the moonlight database with new curated data
        
        Args:
            curated_mcps: List of curated MCP configurations
        """
        try:
            with get_moonlight_db_connection() as conn:
                cursor = conn.cursor()
                
                # Clear all moonlight data
                cursor.execute("DELETE FROM tool_cache")
                cursor.execute("DELETE FROM tag_index") 
                cursor.execute("DELETE FROM tool_index")
                cursor.execute("DELETE FROM mcps")
                
                # Insert new curated MCPs
                for mcp_config in curated_mcps:
                    self._insert_mcp_to_db(cursor, mcp_config, "moonlight")
                
                conn.commit()
            
            # Reload everything to refresh in-memory state
            self._load_from_dbs()
            
        except Exception as e:
            console.print(f"[red]Failed to replace moonlight MCPs: {str(e)}[/red]")
            raise MCPRegistryException(f"Failed to replace moonlight MCPs: {str(e)}")
    
    def _save_user_db(self) -> None:
        """
        Persist only user-added MCPs to user database
        """
        try:
            with get_user_db_connection(self.user_db_path) as conn:
                cursor = conn.cursor()
                
                # Begin transaction
                cursor.execute("BEGIN")
                
                # Clear existing data
                cursor.execute("DELETE FROM tool_cache")
                cursor.execute("DELETE FROM tag_index")
                cursor.execute("DELETE FROM tool_index")
                cursor.execute("DELETE FROM mcps")
                
                # Save only user MCPs
                for name, config in self._mcps.items():
                    if hasattr(config, '_source') and config._source == "user":
                        self._insert_mcp_to_db(cursor, config, "user")
                        
                        # Save tools index for this MCP
                        for tool_name, mcp_names in self._tools_index.items():
                            if name in mcp_names:
                                cursor.execute('''
                                    INSERT INTO tool_index (tool_name, mcp_name)
                                    VALUES (?, ?)
                                ''', (tool_name, name))
                        
                        # Save tag index for this MCP - DEDUPLICATE TAGS
                        unique_tags = set(config.tags)  # Remove duplicates
                        for tag in unique_tags:
                            cursor.execute('''
                                INSERT INTO tag_index (tag, mcp_name)
                                VALUES (?, ?)
                            ''', (tag, name))
                        
                        # Save tool cache for this MCP
                        if name in self._tool_cache:
                            cursor.execute('''
                                INSERT INTO tool_cache (mcp_name, tools)
                                VALUES (?, ?)
                            ''', (name, json.dumps(self._tool_cache[name])))
                
                # Commit transaction
                conn.commit()
                
        except Exception as e:
            console.print(f"[red]Failed to save user MCP registry to database: {str(e)}[/red]")
            raise MCPRegistryException(f"Failed to save user MCP registry to database: {str(e)}")
    
    def _insert_mcp_to_db(self, cursor, mcp_config: MCPConfig, source_type: str):
        """
        Insert MCP configuration into database
        
        Args:
            cursor: Database cursor
            mcp_config: MCP configuration to insert
            source_type: Either "moonlight" or "user"
        """
        cursor.execute('''
            INSERT OR REPLACE INTO mcps (
                name, description, command, args, required_envs, 
                needs_envs, url, ws_url, headers, auth_token, tags, version, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            mcp_config.name, mcp_config.description, mcp_config.command, 
            json.dumps(mcp_config.args), json.dumps(mcp_config.required_envs),
            mcp_config.needs_envs, mcp_config.url, mcp_config.ws_url, 
            json.dumps(mcp_config.headers), mcp_config.auth_token, 
            json.dumps(mcp_config.tags), mcp_config.version, source_type
        ))
        
        # # Index tags
        # for tag in mcp_config.tags:
        #     cursor.execute('''
        #         INSERT OR REPLACE INTO tag_index (tag, mcp_name)
        #         VALUES (?, ?)
        #     ''', (tag, mcp_config.name))
        
    def test_connection(
            self, 
            mcp_config: MCPConfig
        ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Test connection to an MCP server and retrieve its tools
        
        Args:
            mcp_config: The MCP configuration to test
            
        Returns:
            Tuple of (success, message, tools)
        """
        try:
            tools = self._discover_mcp_tools(mcp_config)
            tool_names = [tool.get("name") for tool in tools]
            return True, f"Successfully connected. Found {len(tools)} tools: {', '.join(tool_names)}", tools
        except Exception as e:
            return False, f"Connection test failed: {str(e)}", []
    
    def register(
            self, 
            mcp_config: MCPConfig
        ) -> bool:
        """
        Register an MCP configuration in the USER registry only.
        Curated MCPs are managed separately through the moonlight database.
        
        Args:
            mcp_config: The MCP configuration to register
            
        Returns:
            True if registration was successful, False otherwise
        """
        if not isinstance(mcp_config, MCPConfig):
            raise MCPRegistryException("mcp_config must be an instance of MCPConfig")
            
        name = mcp_config.name.strip()
        
        if not name:
            console.print("[red]MCP name cannot be empty[/red]")
            return False
        
        # Check if already exists (in either database)
        if name in self._mcps:
            existing_source = getattr(self._mcps[name], '_source', 'unknown')
            if existing_source == "moonlight":
                console.print(f"[red]Cannot register '{name}': already exists as curated MCP[/red]")
                return False
            else:
                console.print(f"[yellow]MCP '{name}' already exists in user registry. Updating...[/yellow]")
        
        # Test the connection before registering
        try:
            success, message, tools = self.test_connection(mcp_config)
            
            if success:
                # Create a clean version to store in the registry
                clean_config = MCPConfig(
                    name=mcp_config.name,
                    description=mcp_config.description,
                    command=mcp_config.command,
                    args=mcp_config.args.copy() if mcp_config.args else [],
                    required_envs=mcp_config.required_envs,
                    needs_envs=mcp_config.needs_envs,
                    url=mcp_config.url,
                    ws_url=mcp_config.ws_url,
                    headers=mcp_config.headers.copy() if mcp_config.headers else {},
                    auth_token=mcp_config.auth_token,
                    tags=mcp_config.tags.copy() if mcp_config.tags else [],
                    version=mcp_config.version
                )
                
                # Mark as user-added
                clean_config._source = "user"

                # Register the clean version
                self._mcps[name] = clean_config
                
                # Index by tags
                for tag in mcp_config.tags:
                    if tag not in self._tag_index:
                        self._tag_index[tag] = set()
                    self._tag_index[tag].add(name)
                
                # Store complete tool information
                self._tool_cache[name] = tools
                
                # Update tools index with tool names
                for tool in tools:
                    tool_name = tool.get("name")
                    if tool_name:
                        if tool_name not in self._tools_index:
                            self._tools_index[tool_name] = set()
                        self._tools_index[tool_name].add(name)
                
                # Persist changes to user database only
                self._save_user_db()
                
                console.print(f"[green]Successfully registered {name} with {len(tools)} tools to user database[/green]")
                return True
            else:
                console.print(f"[red]Failed to register {name}: {message}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Failed to register {name}: {e}[/red]")
            return False
    
    def unregister(
            self, 
            name: str
        ) -> bool:
        """
        Remove an MCP configuration from the USER registry only.
        Curated MCPs cannot be unregistered.
        
        Args:
            name: Name of the MCP to unregister
            
        Returns:
            True if unregistration was successful
        """
        if name not in self._mcps:
            console.print(f"[yellow]MCP '{name}' not found[/yellow]")
            return False
        
        # Check if it's a curated MCP
        if hasattr(self._mcps[name], '_source') and self._mcps[name]._source == "moonlight":
            console.print(f"[red]Cannot unregister curated MCP '{name}'. Only user-added MCPs can be removed.[/red]")
            return False
        
        # Remove from main dictionary
        del self._mcps[name]
        
        # Remove from tools index
        tools_to_remove = []
        for tool_name, mcp_names in self._tools_index.items():
            mcp_names.discard(name)
            if not mcp_names:
                tools_to_remove.append(tool_name)
        
        for tool in tools_to_remove:
            del self._tools_index[tool]
        
        # Remove from tag index
        tags_to_remove = []
        for tag, mcp_names in self._tag_index.items():
            mcp_names.discard(name)
            if not mcp_names:
                tags_to_remove.append(tag)
        
        for tag in tags_to_remove:
            del self._tag_index[tag]
        
        # Remove from tool cache
        if name in self._tool_cache:
            del self._tool_cache[name]
        
        # Persist changes to user database only
        self._save_user_db()
        
        console.print(f"[green]Successfully unregistered user MCP '{name}'[/green]")
        return True
    
    def get_user_mcps(self) -> List[MCPConfig]:
        """Get only user-added MCPs"""
        return [config for config in self._mcps.values() 
                if hasattr(config, '_source') and config._source == "user"]
    
    def get_curated_mcps(self) -> List[MCPConfig]:
        """Get only curated MCPs"""
        return [config for config in self._mcps.values() 
                if hasattr(config, '_source') and config._source == "moonlight"]
        
    def get_by_name(
            self, 
            name: str
        ) -> Optional[MCPConfig]:
        """
        Get an MCP configuration by name
        
        Args:
            name: Name of the MCP to retrieve
            
        Returns:
            MCPConfig if found, None otherwise
        """
        return self._mcps.get(name)
    
    def search_by_tool(
            self, 
            tool_name: str
        ) -> List[MCPConfig]:
        """
        Find all MCPs that provide a specific tool
        
        Args:
            tool_name: Name of the tool to search for
            
        Returns:
            List of MCPConfig objects that provide the tool
        """
        if tool_name not in self._tools_index:
            return []
            
        return [self._mcps[name] for name in self._tools_index[tool_name] if name in self._mcps]
    
    def search_by_tag(
            self, 
            tag: str
        ) -> List[MCPConfig]:
        """
        Find all MCPs with a specific tag
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of MCPConfig objects with the specified tag
        """
        if tag not in self._tag_index:
            return []
            
        return [self._mcps[name] for name in self._tag_index[tag] if name in self._mcps]
    
    def search_by_description(
        self, 
        query: str,
        fuzzy: bool = True
    ) -> List[MCPConfig]:
        """
        Find all MCPs whose descriptions contain the given query
        
        Args:
            query: Text to search for in descriptions
            fuzzy: If True, use case-insensitive partial matching
                
        Returns:
            List of MCPConfig objects matching the description search
        """
        results = []
        
        if not query:
            return results
            
        query = query.lower() if fuzzy else query
        
        for name, config in self._mcps.items():
            description = config.description
            if fuzzy:
                description = description.lower()
                
            if query in description:
                results.append(config)
                
        return results

    def search(
            self, 
            query: str,
            fuzzy: bool = True
        ) -> List[MCPConfig]:
        """
        Universal search across names, descriptions, tags, and tools
        
        Args:
            query: Text to search for across all fields
            fuzzy: If True, use case-insensitive partial matching
                
        Returns:
            List of MCPConfig objects matching the search
        """
        if not query:
            return []
            
        query = query.lower() if fuzzy else query
        results = set()
        
        # Search in names
        for name, config in self._mcps.items():
            name_to_check = name.lower() if fuzzy else name
            if query in name_to_check:
                results.add(name)
        
        # Search in descriptions
        for name, config in self._mcps.items():
            description = config.description.lower() if fuzzy else config.description
            if query in description:
                results.add(name)
        
        # Search in tags
        for name, config in self._mcps.items():
            for tag in config.tags:
                tag_to_check = tag.lower() if fuzzy else tag
                if query in tag_to_check:
                    results.add(name)
                    break
        
        # Search in tools
        for tool_name, mcp_names in self._tools_index.items():
            tool_to_check = tool_name.lower() if fuzzy else tool_name
            if query in tool_to_check:
                results.update(mcp_names)
        
        # Convert set of names to list of configs
        return [self._mcps[name] for name in results if name in self._mcps]
    
    def list_all(self) -> List[MCPConfig]:
        """
        List all registered MCPs
        
        Returns:
            List of all registered MCPConfig objects
        """
        return list(self._mcps.values())
    
    def get_tools_for_mcp(
            self, 
            name: str
        ) -> List[Dict[str, Any]]:
        """
        Get the list of tools provided by an MCP
        
        Args:
            name: Name of the MCP
            
        Returns:
            List of tool information dictionaries
        """
        if name not in self._mcps:
            raise MCPRegistryException(f"MCP '{name}' not found in registry")
            
        # Return from cache if available
        if name in self._tool_cache:
            return self._tool_cache[name]
            
        # Try to discover tools
        try:
            success, message, tools = self.test_connection(self._mcps[name])
            
            if not success:
                raise MCPRegistryException(message)
                
            # Cache the discovered tools
            self._tool_cache[name] = tools
            
            # Update tools index
            for tool in tools:
                tool_name = tool.get("name")
                if tool_name:
                    if tool_name not in self._tools_index:
                        self._tools_index[tool_name] = set()
                    self._tools_index[tool_name].add(name)
                
            # Persist changes
            if hasattr(self._mcps[name], '_source') and self._mcps[name]._source == "user":
                self._save_user_db()
            
            return tools
        except Exception as e:
            raise MCPRegistryException(f"Failed to discover tools for MCP '{name}': {e}")
    
    def _discover_mcp_tools(
            self, 
            mcp_config: MCPConfig
        ) -> List[Dict[str, Any]]:
        """
        Connect to an MCP and discover its tools
        
        Args:
            mcp_config: Configuration for the MCP
            
        Returns:
            List of tool information dictionaries
        """
        try:
            # Create event loop if needed
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            tools_data = []
            
            def discover_tools():
                with MCPClient(config=mcp_config) as client:
                    discovered_tools = client.discover_tools()
                    return discovered_tools
            
            # Run the discovery process with a timeout
            discovered_tools = loop.run_until_complete(
                asyncio.wait_for(
                    asyncio.to_thread(discover_tools),
                    timeout=30.0
                )
            )
            
            # Convert Tool objects to serializable dictionaries
            for tool in discovered_tools:
                tool_dict = {
                    "name": tool.name,
                    "description": getattr(tool, "description", ""),
                    "inputSchema": getattr(tool, "inputSchema", {}),
                    "annotations": getattr(tool, "annotations", None)
                }
                tools_data.append(tool_dict)
            
            return tools_data
            
        except Exception as e:
            raise MCPRegistryException(f"Failed to discover tools: {e}")
    
    def _register_super(
            self, 
            mcp_config: MCPConfig,
            skip_connection_test: bool = False  # Add this parameter
        ) -> bool:
        """
        Register an MCP configuration in the MOONLIGHT (curated) registry.
        This is for adding curated MCPs programmatically.
        
        Args:
            mcp_config: The MCP configuration to register
            skip_connection_test: If True, skip the connection test (for bulk imports)
            
        Returns:
            True if registration was successful, False otherwise
        """
        if not isinstance(mcp_config, MCPConfig):
            raise MCPRegistryException("mcp_config must be an instance of MCPConfig")
            
        name = mcp_config.name.strip()
        
        if not name:
            console.print("[red]MCP name cannot be empty[/red]")
            return False
        
        # Check if already exists
        if name in self._mcps:
            existing_source = getattr(self._mcps[name], '_source', 'unknown')
            console.print(f"[yellow]MCP '{name}' already exists ({existing_source}). Updating...[/yellow]")
        
        tools = []
        
        # Test the connection before registering (optional)
        if not skip_connection_test:
            try:
                success, message, tools = self.test_connection(mcp_config)
                
                if not success:
                    console.print(f"[yellow]Warning: Connection test failed for {name}: {message}[/yellow]")
                    console.print(f"[yellow]Registering anyway (connection test can fail if server isn't running)[/yellow]")
                    tools = []  # Continue with empty tools
            except Exception as e:
                console.print(f"[yellow]Warning: Connection test error for {name}: {e}[/yellow]")
                console.print(f"[yellow]Registering anyway (connection test can fail if server isn't running)[/yellow]")
                tools = []  # Continue with empty tools
        
        try:
            # Create a clean version to store in the registry
            clean_config = MCPConfig(
                name=mcp_config.name,
                description=mcp_config.description,
                command=mcp_config.command,
                args=mcp_config.args.copy() if mcp_config.args else [],
                required_envs=mcp_config.required_envs,
                needs_envs=mcp_config.needs_envs,
                url=mcp_config.url,
                ws_url=mcp_config.ws_url,
                headers=mcp_config.headers.copy() if mcp_config.headers else {},
                auth_token=mcp_config.auth_token,
                tags=mcp_config.tags.copy() if mcp_config.tags else [],
                version=mcp_config.version
            )
            
            # Mark as moonlight (curated)
            clean_config._source = "moonlight"

            # Register the clean version
            self._mcps[name] = clean_config
            
            # Index by tags
            for tag in mcp_config.tags:
                if tag not in self._tag_index:
                    self._tag_index[tag] = set()
                self._tag_index[tag].add(name)
            
            # Store complete tool information
            if tools:
                self._tool_cache[name] = tools
                
                # Update tools index with tool names
                for tool in tools:
                    tool_name = tool.get("name")
                    if tool_name:
                        if tool_name not in self._tools_index:
                            self._tools_index[tool_name] = set()
                        self._tools_index[tool_name].add(name)
            
            # Persist changes to moonlight database only
            self._save_moonlight_db()
            
            console.print(f"[blue]Successfully registered {name} with {len(tools)} tools to moonlight database[/blue]")
            return True
            
        except Exception as e:
            console.print(f"[red]Failed to register {name}: {e}[/red]")
            return False

    def _save_moonlight_db(self) -> None:
        """
        Persist only moonlight (curated) MCPs to moonlight database
        """
        try:
            with get_moonlight_db_connection() as conn:
                cursor = conn.cursor()
                
                # Begin transaction
                cursor.execute("BEGIN")
                
                # Clear existing data
                cursor.execute("DELETE FROM tool_cache")
                cursor.execute("DELETE FROM tag_index")
                cursor.execute("DELETE FROM tool_index")
                cursor.execute("DELETE FROM mcps")
                
                # Save only moonlight MCPs
                for name, config in self._mcps.items():
                    if hasattr(config, '_source') and config._source == "moonlight":
                        self._insert_mcp_to_db(cursor, config, "moonlight")
                        
                        # Save tag index for this MCP - DEDUPLICATE TAGS
                        unique_tags = set(config.tags)  # Remove duplicates
                        for tag in unique_tags:
                            cursor.execute('''
                                INSERT OR IGNORE INTO tag_index (tag, mcp_name)
                                VALUES (?, ?)
                            ''', (tag, name))
                        
                        # Save tools index for this MCP
                        for tool_name, mcp_names in self._tools_index.items():
                            if name in mcp_names:
                                cursor.execute('''
                                    INSERT OR IGNORE INTO tool_index (tool_name, mcp_name)
                                    VALUES (?, ?)
                                ''', (tool_name, name))
                        
                        # Save tool cache for this MCP
                        if name in self._tool_cache:
                            cursor.execute('''
                                INSERT OR REPLACE INTO tool_cache (mcp_name, tools)
                                VALUES (?, ?)
                            ''', (name, json.dumps(self._tool_cache[name])))
                
                # Commit transaction
                conn.commit()
                
        except Exception as e:
            console.print(f"[red]Failed to save moonlight MCP registry to database: {str(e)}[/red]")
            raise MCPRegistryException(f"Failed to save moonlight MCP registry to database: {str(e)}")

    def __str__(self):
        """
        Print the registry contents in a formatted table
        """
        table = Table(title="MCP Registry")
        
        table.add_column("Name", style="cyan")
        table.add_column("Description")
        table.add_column("Type", style="green")
        table.add_column("Source", style="magenta")
        table.add_column("Tools", style="yellow")
        
        for name, config in self._mcps.items():
            # Determine connector type for display
            if hasattr(config, 'TYPE_STDIO') and config.TYPE_STDIO:
                connector_type = "stdio"
            elif hasattr(config, 'TYPE_HTTP') and config.TYPE_HTTP:
                connector_type = "http"
            elif hasattr(config, 'TYPE_WEBSOCKET') and config.TYPE_WEBSOCKET:
                connector_type = "websocket"
            elif config.command:
                connector_type = "stdio"
            elif config.url:
                connector_type = "http"
            elif config.ws_url:
                connector_type = "websocket"
            else:
                connector_type = "unknown"
            
            # Determine source
            source = getattr(config, '_source', 'unknown')
            source_display = "🌙" if source == "moonlight" else "👤" if source == "user" else "❓"
                
            if name in self._tool_cache:
                tool_names = [tool.get("name", "") for tool in self._tool_cache[name] if tool.get("name")]
                tools_str = ", ".join(tool_names) if tool_names else "[dim]no tools[/dim]"
            else:
                tools_str = "[dim]unknown[/dim]"
                
            table.add_row(name, config.description, connector_type, source_display, tools_str)
        
        console.print(table)
        return ""
    
    def __repr__(self):
        """
        Print the registry contents in a formatted table
        """
        table = Table(title="MCP Registry")
        
        table.add_column("Name", style="cyan")
        table.add_column("Description")
        table.add_column("Type", style="green")
        table.add_column("Source", style="magenta")
        table.add_column("Tools", style="yellow")
        
        for name, config in self._mcps.items():
            # Determine connector type for display
            if hasattr(config, 'TYPE_STDIO') and config.TYPE_STDIO:
                connector_type = "stdio"
            elif hasattr(config, 'TYPE_HTTP') and config.TYPE_HTTP:
                connector_type = "http"
            elif hasattr(config, 'TYPE_WEBSOCKET') and config.TYPE_WEBSOCKET:
                connector_type = "websocket"
            elif config.command:
                connector_type = "stdio"
            elif config.url:
                connector_type = "http"
            elif config.ws_url:
                connector_type = "websocket"
            else:
                connector_type = "unknown"
            
            # Determine source
            source = getattr(config, '_source', 'unknown')
            source_display = "🌙" if source == "moonlight" else "👤" if source == "user" else "❓"
                
            if name in self._tool_cache:
                tool_names = [tool.get("name", "") for tool in self._tool_cache[name] if tool.get("name")]
                tools_str = ", ".join(tool_names) if tool_names else "[dim]no tools[/dim]"
            else:
                tools_str = "[dim]unknown[/dim]"
                
            table.add_row(name, config.description, connector_type, source_display, tools_str)
        
        console.print(table)
        return ""