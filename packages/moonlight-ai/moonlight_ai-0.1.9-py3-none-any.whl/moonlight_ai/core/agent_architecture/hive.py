import logging, re
from textwrap import dedent

from .agent import Agent, AgentResponse

from ...core.functionality.web_search import WebSearch
from ...core.completions.providers import CompletionInput, OpenAIProvider
from ...core.processors import AgentPythonProcessor, ShellProcessor, FileProcessor
from ...core.token import TokenCounter
from ...core.mcp import MCPClient

from ...src.helpers import log_error
from ...src.json_parser import parse_json

logger = logging.getLogger("hive")

##############################################################################################
# Connector to the agent architecture
def run_agent(
        agent: Agent,
        message: str
    ):
    if isinstance(agent, str):
        return "ERROR | Please provide the agent as non-string. [Hint: Check your available parameters]"
    
    try:
        response = Hive(agent).run(message).assistant_message
    except Exception as e:
        logger.debug(f"Error running agent: {e}")
        
    return response

def search_in_file(file_path: str):
    if not file_path.startswith("/shared_data/"):
        return "ERROR | Please provide the file path in '/shared_data/' directory."
    
    file_contents = FileProcessor([file_path]).content[file_path]    
    return file_contents

def web_search(
        query: str, 
        urls: list = None
    ):
    if urls is not None and query is not None:
        return "ERROR | Please provide either a URL or a query, not both."
    
    if urls and query:
        return "ERROR | Please provide either a URL or a query, not both."
    
    if urls:
        results = WebSearch(
            urls=urls, 
        ).output
    
    elif query:
        results = WebSearch(
            query=query, 
        ).output
    
    return results
##############################################################################################

# Hive is the main class that runs the agent architecture.
class Hive:
    def __init__(
            self,
            agent: Agent,
        ):
        
        # Agent
        self.agent = agent
        
        # Keep model running
        self.keep_model_running = True
                
        self._setup_python_processor()
        
        # LLM Provider
        self.llm = OpenAIProvider(
            provider=agent.provider,
        )
        
        self.token_counter = TokenCounter(model=self.agent.model_name)
    
    def _setup_python_processor(self):
        """
        Setup the Python processor with the agent's functions and parameters.
        """
        self.python_processor = AgentPythonProcessor()
        
        self.python_processor.add_agents(self.agent.sub_agents)
        self.python_processor.add_functions([
            search_in_file, 
            run_agent, 
            web_search
        ])
        
        # Add the current agent to the processor as well for absolute compatibility
        self.python_processor.add_agents({self.agent.name: self.agent})
        
        # Add the MCP clients to the processor
        self._map_mcp_clients()
        
    def _map_mcp_clients(self):
        """
        For each agent, check if it has an MCP server. If it does, create an MCP client and add it to the processor.
        """
        
        if self.agent.mcp_servers:
            for server_config in self.agent.mcp_servers:
                client = MCPClient(
                    config=server_config
                )
                server_name = server_config.name
                try:
                    client.connect()  # Connect the client
                    self.python_processor.add_mcp_clients({server_name: client})
                except Exception as e:
                    logger.debug(f"Error initializing MCP client for {server_name}: {e}")
        
        # Add the MCP clients to the processor
        self.mcp_clients = getattr(self.python_processor, 'mcp_clients', {})
    
    def _extract_python_code(
            self,
            text: str
        ) -> list:
        """
        Extract Python code blocks from the text.
        """
        pattern = r'```run_python\s*(.*?)\s*```'
        matches = re.findall(pattern, text, re.DOTALL)
        return [dedent(match.strip()) for match in matches if match.strip()]

    def _extract_shell_code(
            self, 
            text: str
        ) -> list:
        """
        Extract shell code blocks from the text.
        """
        pattern = r'```run_shell\s*(.*?)\s*```'
        matches = re.findall(pattern, text, re.DOTALL)
        return [dedent(match.strip()) for match in matches if match.strip()]

    def _run_python_code(
            self, 
            codes: list
        ):
        """
        Run the Python code blocks and return the outputs.
        """
        code_outputs = []
        error_status = False
        logger.debug(f"Running Python code: {codes}")
        for code in codes:
            try:                
                python_output = self.python_processor.execute(code)
                
                if python_output.is_error:
                    output = python_output.error
                    error_status = True
                else:
                    output = python_output.output
                code_outputs.append(output)
                
            except Exception as e:
                code_outputs.append(f"Error running Python code: {e}")
                error_status = True
                
        return code_outputs, error_status

    def _run_shell_code(
            self, 
            codes: list
        ):
        """
        Run the shell code blocks and return the outputs.
        """
        shell_outputs = []
        shell_failed = False

        for code in codes:
            # processor = ShellProcessor(command=code)
            # processor.execute()
            # result = processor.result
            # output = result['output']

            # if result['error']:
            #     output += "\n" + result['error']
            #     shell_failed = True
    
            # if result['returncode'] != 0:
            #     shell_failed = True

            # shell_outputs.append(output)
            shell_outputs.append("Cannot Run Shell Code in this environment.")

        return shell_outputs, shell_failed
             
    def _extract_plan(
            self, 
            reason_text: str
        ):
        """
        Extract the plan from the reason text.
        """
        plan_match = re.search(r'<plan>(.*?)</plan>', reason_text, re.DOTALL)
        if plan_match:
            plan_text = plan_match.group(1).strip()
            return [step.strip() for step in plan_text.split('\n') if step.strip()]
        return []

    def _extract_reason(
            self, 
            text: str
        ):
        """
        Extract the reason from the text.
        """
        reason_match = re.search(r'<(thought|think)>(.*?)</(thought|think)>', text, re.DOTALL)
        if reason_match:
            full_reason = reason_match.group(2).strip()  # Changed from group(1) to group(2)
            # Remove the plan section from reason if it exists
            reason_without_plan = re.sub(r'<plan>.*?</plan>', '', full_reason, flags=re.DOTALL)
            return reason_without_plan.strip()
        return ""

    def _extract_answer(
            self, 
            text: str
        ):
        """
        Extract the answer from the text.
        """
        answer_match = re.search(r"<answer>(.*?)(</answer>|$)", text, re.DOTALL)
        if answer_match:
            return answer_match.group(1).strip()
        return ""
                  
    def _normal_run(
            self, 
            message: str = "", 
            images: list = []
        ):
        """
        The main function that runs the agents.
        
        Args:
            message: The message to send to the agent.
            images: A list of images to send to the agent.
        
        Returns:
            AgentResponse: The response from the agent.
        """
        if not self.agent.enable_history:
            self.agent.history.clear_history()

        if len(images) > 1 and self.agent.provider == "together":
            log_error("Together provider does not support multiple images. Only the first image will be used.")
            images = images[:1]
        
        if message and not images:
            self.agent.history.append_message("user", message)
        elif images and message:
            self.agent.history.append_message("user", message=message, images=images)
        elif images and not message:
            self.agent.history.append_message("user", message="images", images=images)
        
        self.keep_model_running = True
        self.total_tokens = 0
        
        user_input_tokens = self.token_counter.count_tokens(message)
        self.total_tokens += user_input_tokens
        
        while self.keep_model_running:            
            raw_message = self.llm.get_completion(
                CompletionInput(
                    model_name = self.agent.model_name,
                    messages = self.agent.get_history(),
                    max_context = self.agent.max_context,
                    max_output_length = self.agent.max_output_length,
                    temperature = self.agent.temperature
                )
            )
        
            raw_message_tokens = self.token_counter.count_tokens(str(raw_message))
            self.total_tokens += raw_message_tokens
            
            # Extract response content with better error handling
            assistant_message = self._extract_answer(raw_message)
            
            if self.agent.toolcall_enabled:
                assistant_message_with_python = assistant_message
                
                while "```run_python" in assistant_message:
                    assistant_message = re.sub(r'```run_python\s*(.*?)\s*```', '', assistant_message, flags=re.DOTALL)

                while "```run_shell" in assistant_message:
                    assistant_message = re.sub(r'```run_shell\s*(.*?)\s*```', '', assistant_message, flags=re.DOTALL)

                python_codes = self._extract_python_code(assistant_message_with_python)
                shell_codes = self._extract_shell_code(assistant_message_with_python)
                
                if len(python_codes) > 1:
                    self.agent.history.append_message("assistant", assistant_message_with_python)
                    self.agent.history.append_message("user", "SYSTEM: Auto-Run can only run one Python code block at a time. Please combine them into a single script. Do not reply to the user.")
                    continue
                
                python_outputs, python_failed = self._run_python_code(python_codes)
                shell_outputs, shell_failed = self._run_shell_code(shell_codes)
                
                logger.debug("*" * 50)
                logger.debug(f"HIVE")
                logger.debug(f'\n\nAgent Name: {self.agent.name}\n\n')
                logger.debug(f"Assistant message: {assistant_message_with_python}\n\n")
                logger.debug(f"Python Codes: {python_codes}\n\n")
                logger.debug(f"Python Outputs: {python_outputs}\n\n")
                logger.debug(f"Shell Codes: {shell_codes}\n\n")
                logger.debug(f"Shell Outputs: {shell_outputs}\n\n")
                logger.debug("*" * 50)
                
                if not python_codes and not shell_codes: 
                    self.keep_model_running = False
                    break
                    
                if python_failed or shell_failed:
                    agents_next_action = "SYSTEM: You should try to fix this or ask the me for more information."
                    logger.debug(f"Python failed: {python_failed}, Shell failed: {shell_failed}")
                else:
                    agents_next_action = "SYSTEM: You should probably relay this information to me since user can't see the output of the toolcalls. User can't see this message, so no need to thank them. You may optionally proceed with making further toolcalls to get a more detailed output if you want to."
                
                user_message_to_assistant = dedent(f"""
                ```python_outputs
                {python_outputs}
                ```
                The outputs are in a format of list of strings. Each string is the output of that respective code block.

                {"".join(f"```shell_outputs\n{shell_outputs}\n```") if shell_outputs else ""}
                
                {agents_next_action}
                """).strip()

                self.agent.history.append_message("assistant", f"{assistant_message_with_python}")
                self.agent.history.append_message("user", user_message_to_assistant)
            else:
                python_codes = []
                self.keep_model_running = False
                break
        
        self.agent.history.append_message("assistant", assistant_message)

        return AgentResponse({
            "raw_message": raw_message,
            "assistant_message": assistant_message,
            "python_codes": python_codes,
            "reason": self._extract_reason(raw_message),
            "plan": self._extract_plan(raw_message),
            "total_tokens": self.total_tokens,
        })
        
    def run(
            self, 
            message: str = "",
            images: list = [],
        ):   
        
        """
        Run the agent with the given message and images.
        
        Args:
            message: The message to send to the agent.
            images: A list of images to send to the agent.
        
        Returns:
            AgentResponse: The response from the agent.
        """
        try:             
            if self.agent.json_mode:
                message += "\n Return the output in the JSON format only."
                logger.debug("=" * 100)
                logger.debug("Running in JSON mode")
                logger.debug("=" * 100)
                response = self._normal_run(message, images)
                if response == "<out_of_tokens>": return [{"error": "<out_of_tokens>"}]
                # remove the ````json` and ` ``` ` from the response
                response.assistant_message = re.sub(r'```json\s*(.*?)\s*```', r'\1', response.assistant_message, flags=re.DOTALL)
                response.assistant_message = re.sub(r'```', '', response.assistant_message, flags=re.DOTALL)
                response.assistant_message = response.assistant_message.strip()
                json_response, _ = parse_json(dedent(response.assistant_message).strip())
                return json_response
            else:
                response = self._normal_run(message, images)                
                return response
        except Exception as e:
            message = f"Output could not be generated due to an error. {e}"
            
            if self.agent.json_mode:
                return [{"error": message}]
            
            return AgentResponse({
                "raw_message": "",
                "assistant_message": f"Output could not be generated due to an error. {e}",
                "python_codes": [],
                "reason": "",
                "plan": [],
                "total_tokens": 0,
            })

    def __del__(self):
        """
        Clean up resources when the Hive object is garbage collected
        """
        # Close any MCP clients that were created
        if hasattr(self, 'mcp_clients'):
            for client_name, client in self.mcp_clients.items():
                try:
                    client.disconnect()
                except Exception as e:
                    logger.debug(f"Error disconnecting MCP client {client_name}: {e}")