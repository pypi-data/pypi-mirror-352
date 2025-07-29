import logging
from textwrap import dedent

from rich.console import Console
from rich.markdown import Markdown

from ...src.helpers import log_error, discover_agents
from ...src.json_parser import parse_json

from .base import MoonlightProvider

console = Console()
logger = logging.getLogger(__name__)

class AgentException(Exception):
    pass

class AgentHistory:
    def __init__(
            self,
            max_length: int = 4096,
            system_role: str = "",
            multimodal: bool = False,
        ):
        self.history = []
    
        self.max_length = max_length
        self.multimodal = multimodal
        
        self._set_system_role(system_role)

    def _set_system_role(
            self,
            system_role: str = "",
        ):
        self.system_role = system_role        
        if len(self.history) > 1:
            self.history.insert(0, {"role": "system", "content": system_role})
        else:
            self.history = [
                {"role": "system", "content": system_role}
            ]
    
    def update_system_role(
            self, 
            system_role: str = "",
        ):
        self.system_role = system_role
        self.history.pop(0)
        self.history.insert(0, {"role": "system", "content": system_role})
        
    def append_message(
            self, 
            role: str = "", 
            message: str = "",
            images: list = [],
        ):
        
        if not self.multimodal and images:
            log_error("Multimodality is not enabled. Cannot append images.\nPass Agent(multimodal=True) to enable it.")
        
        # Append Images
        if self.multimodal and images:
            message = [{"type": "text", "text": message}]
            for i, image_b64 in enumerate(images):
                message.append({"type": "text", "text": f"Image #{i}"})
                message.append({"type": "image_url", "image_url": {"url": image_b64}})
        
        # Append text message
        self.history.append({"role": role, "content": message})
        
    def clear_history(self):
        self.history = []
        self._set_system_role(self.system_role)
    
    def __repr__(self):
        return f"ConversationHistory(max_length={self.max_length}, check_length={self.check_length})"
    
    def __str__(self):
        out_str = "=" * 20 + "\n"
        out_str += f"Conversation History: \n{self.history}"
        out_str += "\n" + "=" * 20
        return out_str

class AgentResponse:
    def __init__(
            self, 
            response: dict = {}
        ):
        self.raw_message = response.get('raw_message', '')
        self.assistant_message = response.get('assistant_message', '')
        self.python_codes = response.get('python_codes', [])
        self.reason = response.get('reason', '')
        self.plan = response.get('plan')
        self.total_tokens = response.get('total_tokens', 0)     
       
    def __repr__(self):
        console.rule("[bold green]Agent Response Details[/bold green]")
        
        # Render Reason with Markdown and print label separately
        console.print("[bold yellow]Reason:[/bold yellow]")
        md_reason = Markdown(self.reason)
        console.print(md_reason)
        console.print("")  # for spacing
        
        # Render Assistant Message with Markdown and print label separately
        console.print("[bold yellow]Assistant Message:[/bold yellow]")
        md_assistant = Markdown(self.assistant_message)
        console.print(md_assistant)
        console.print("")  # for spacing
        
        console.print(f"[bold yellow]Total Tokens:[/bold yellow] {self.total_tokens}")
        
        if self.plan:
            console.print(f"[bold yellow]Plan:[/bold yellow]")
            
            if isinstance(self.plan, list):
                for _, step in enumerate(self.plan, 1):
                    console.print(f"  [cyan]{step}[/cyan]")
            else:
                console.print(f"  [cyan]{self.plan}[/cyan]")
            console.print("")
            
        if self.python_codes:
            console.print(f"[bold yellow]Python Codes:[/bold yellow]")
            md_python = Markdown(self.python_codes)
            console.print(md_python)
            console.print("")  # for spacing
            
        console.rule()
        return ""
    
class Agent:
    def __init__(
            self,
            
            # About the Agent
            name: str = "Agent",
            description: str = "",

            # Model Parameters
            model_name: str = "",
            max_context: int = 64_000,
            max_output_length: int = 8192,
            temperature: float = 0.7,

            # Instructions
            instruction: str = "",
            
            # Agent Provider/URL
            provider: MoonlightProvider = None,

            # Agent Parameters
            enable_history: bool = True,
            orchestra_mode: bool = False,
            multimodal: bool = False,
            toolcall_enabled: bool = True,
            enable_base_functions: bool = True,
            
            # JSON Mode
            json_mode: bool = False,
            json_schema: str = "",

            # MCP
            mcp_servers: list = [],
            
            # Sub-Agents
            sub_agents: dict = {}
        ):
        
        # About the Agent
        self.name                   =      name
        self.description            =      description

        # Model Parameters
        self.model_name             =      model_name
        self.max_context            =      max_context
        self.max_output_length      =      max_output_length
        self.temperature            =      temperature

        # Instructions
        self.instruction            =      instruction
        self.role                   =      ""

        # Agent Provider
        self.provider               =      provider
        
        # Agent Parameters
        self.enable_history         =      enable_history
        self.multimodal             =      multimodal
        self.orchestra_mode         =      orchestra_mode
        self.toolcall_enabled       =      toolcall_enabled
        self.emable_base_functions  =      enable_base_functions
        
        # JSON Mode
        self.json_mode              =      json_mode
        self.json_schema            =      json_schema
        
        # MCP
        self.mcp_servers            =      mcp_servers
        
        # Sub-Agents
        self.sub_agents             =      sub_agents
        
        # Initialize Agent
        self._init_agent()
    
    def _init_agent(self):
        # Get the instuctions
        self._get_instuctions()
        
        # Check the parameters of the agent
        self._check_parameters()
        
        # Build the role of the agent
        self._build_role()
        
        # Initialize the Agent History
        self.history = AgentHistory(
            system_role=self.role, 
            max_length=self.max_context, 
            multimodal=self.multimodal
        )
        
    def _check_parameters(self):  

        if not isinstance(self.provider, MoonlightProvider):
            raise AgentException("Provider must be an instance of MoonlightProvider.")
        
        if len(self.instruction) == 0:
            logger.warning("System role is not set. Please set the system role. Proceeding with default role.")
            self.instruction = "You are an Agent with a secret mission."
        
        if len(self.model_name) == 0:
           raise AgentException("Found no model. Please pass one!")
        
        if self.json_schema and not self.json_mode:
            raise AgentException("Please enable json_mode to use json_schema.")
        
        if self.json_mode and not self.json_schema:
            raise AgentException("Please provide a json schema to use json_mode.")
        
        if self.json_mode and self.json_schema:            
            try:
                parse_json(
                    self.json_schema,
                    fix_mode=False
                )
            except Exception as e:
                raise AgentException(f"Invalid JSON schema. {e}")
            
            self.instruction += f"You are only allowed to provide JSON data. Anything else will be ignored. Here is the schema:\n \n```\njson\n{self.json_schema}\n```\n. Each json object must be seperated by a comma. Make sure it follows proper JSON format. You are not allowed to return anything but JSON data within the schema and in ```json ... ``` format (markdown json format). You can return either top level object or array of objects. Your wish depending on the schema. Do not return anything else."
        
        if self.emable_base_functions and not self.toolcall_enabled:
            self.enable_base_functions = False
        
        
    def _build_role(self):
        self.role = self.instruction
        
        if not self.toolcall_enabled: return
        
        self.role += self.toolcall_instructions
        
        sub_agents_prompt = ""
        if self.sub_agents:
            sub_agents_prompt = discover_agents(self.sub_agents)
        
        if self.emable_base_functions:
            self.role += self.function_instructions + sub_agents_prompt
            
        if self.mcp_servers:
            self.role += self.mcp_server_instructions

    
    def _get_instuctions(self):
        self.toolcall_instructions = dedent("""\n\n
        # Code Execution Instructions

        The below are instructions for the toolcall. You can run python scripts and get the output. Here are some tips:
        
        ## Running Code
        
        ### Run Python in the following format:
        ```run_python
        print("Hello, world!")
        ```
        
        ### Notes:
        1. The ```run_python``` tags are used to identify the code type. The "run_" prefix is used to indicate that the code should be executed.
        2. When the "run" prefix is used, the code will be executed no matter what. If you want to show the code to user without executing, see the next section.
        3. The `input()` function is not supported.
        4. Use `print()` to show the output. The output will be captured and returned to you.
        5. Typing the variable will not work like it does in a normal python shell. You need to use `print()` to show the output.
        6. Use the given functions as is without importing it. They are already imported. If you can't see it, then import it.
        7. When "run" is used, it will auto run and user cannot see the code and you will be asked to reply again and again so do not provide the code with the "run" prefix unless you want to run it.
        8. User cannot see the code when "run" is used. It will be executed and the output will be returned to you.
        9. Execute the code without "confirming" it with the user or asking for permission. You are in charge. You are the agent and you know what to do. Do not ask for permission or confirmation.
        10. Make sure the code is safe and valid before executing it. If you are not sure, do not execute it. You can ask the user for confirmation if you are not sure.

        ## Showing Code
        
        ### Send message in the following format to run a python script:
        ```python
        print("Hello, world!")
        ```

        ### Notes:
        1. The ```python``` tags are used to identify the code type. The "run_" prefix is used to indicate that the code should be executed.
        2. This shows the code to the user without executing it. The code will be shown in a code block.                                 
        \n""").strip()
        
        self.function_instructions = dedent("""\n\n
        # Function Instructions
        
        The below are instructions for the functions. You can call the functions and get the output. Here are some tips:
        
        ## Running Functions
        1. The functions are already imported. You can call them directly.
        2. You can call the functions with the parameters as you would in a normal python script.
        
        ## Available Functions
        
        ### 1. Run Agent
        
        #### Function Signature
        `run_agent(agent: Agent, message: str = "") -> str`
        
        #### Description
        This function runs the agent with the given message. The agent will see you as the user and will run based on the message.
        
        #### Example
        ```run_python
        agent_output = run_agent(
            agent=<agent_name>,
            message=<message_string> # The message string to pass to the agent that will see and run. You will be considered as the user.
        )
        print(agent_output) # To see the output of the agent.
        ```
        
        ### 2. Web Search
        
        #### Function Signature
        `web_search(query: str, urls: list = None) -> str`
        
        #### Description
        This function runs a web search with the given query. If list of urls are provided, it will search the urls and return contents of those urls. Either query or urls can be provided. If both are provided, it will return an error.
        
        #### Example
        ```run_python
        search_results = web_search(
            query=<query_string>, # The query string to search.
            urls=<list_of_urls>, # The list of urls to search. Either query or urls can be provided. If both are provided, it will return an error.
        )
        print(search_results) # To see the output of the search.
        ```
        
        ### 3. Search in File
        
        #### Function Signature
        `search_in_file(file_path: str) -> str`
        
        #### Description
        This function searches the file with the given file path. The file path must be in the /shared_data/ directory. If the file path is not in the /shared_data/ directory, it will return an error. You can use other methods of your own to search the path to file inside the /shared_data/ directory. Then with the file path, you can use this function to search the file. The file contents will be returned.
        
        #### Example
        ```run_python
        file_contents = search_in_file(
            file_path=<file_path_string> # The file path to search. The file path must be in the /shared_data/ directory. If the file path is not in the /shared_data/ directory, it will return an error.
        )
        print(file_contents) # To see the output of the file contents.
        ```
        """)
        
        self.mcp_server_instructions = ""

        if self.mcp_servers:
            mcp_server_names = [server.name for server in self.mcp_servers]
            self.mcp_server_instructions = dedent(f"""
            \n\n
            # MCP Server Instructions
            The below are instructions for the MCP servers. You can use the MCP servers to run the code. Here are some tips:

            ## Running MCP Servers
            - MCP stands for Model Context Protocol. The MCP servers are open and each have their own sets of tools.
            - You can discover tools available for each MCP server available to you and call them as per discovery.
            - Do not assume any tools are available. Always discover the tools first.
            - See the below for the instructions on how to call the MCP servers and the available MCP servers.
            
            ## How to call MCP Servers
            
            ### To discover tools:
            ```run_python
            available_tools = <mcp_server_name>.discover_tools()
            print(available_tools)
            ```
            
            ### Description of tool descovery:
            - The `discover_tools()` function will return a list of available tools in the MCP server.
            - Each tool will have name, description and required arguments.
            - You can use the name of the tool to call the tool.
            
            ### To call a tool:
            ```run_python
            <mcp_server_name>.call_tool(
                name=<tool_name>, # The name of the tool to call.
                arguments=<args_dict>, # The arguments to pass to the tool.
            )
            ```
            
            ### Description of tool call:
            - The `call_tool()` function will call the tool with the given name and arguments.
            - The arguments must be in the form of a dictionary.
            - The function will return the output of the tool.
            - Must have arguments as per the tool description when discovered.
            
            ## Available MCP Servers
            {mcp_server_names}
            """)
        else:
            self.mcp_server_instructions = dedent(f"""
            \n\n
            ## Available MCP Servers
            None
            """)
            
    def refresh_role(self):
        self._build_role()
        self.history.update_system_role(self.role)       
    
    def get_history(self):
        return self.history.history
    
    def __repr__(self):
        return f"Agent(name={self.name}, description={self.description})"
    
    def __str__(self):
        out_str = "=" * 20 + "\n"
        out_str += f"Agent: {self.name}\n\nModel: {self.model_name}\nMax Context: {self.max_context}, \nMax Output Length: {self.max_output_length} \nProvider: {self.provider}\nTemperature: {self.temperature}\n\nDescription: {self.description},\n\nSystem Role: {self.role}\n\nFunctions: {[func.__name__ for func in self.functions]}\n\nParameters: {self.parameters}"
        out_str += "\n" + "=" * 20
        return out_str