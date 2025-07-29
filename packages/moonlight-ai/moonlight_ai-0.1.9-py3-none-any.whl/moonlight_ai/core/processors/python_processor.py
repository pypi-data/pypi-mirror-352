import sys, signal, types, traceback, re, threading, concurrent.futures
from pydantic import BaseModel
from typing import Optional
from .base import LogFilteredStringIO

class AgentPythonProcessorOutput(BaseModel):
    output: Optional[str] = None
    error: Optional[str] = None
    is_error: bool = False
    
class AgentPythonProcessor:
    def __init__(
            self, 
            timeout: int = 300
        ):
        
        self.timeout = timeout
        self._output = ''
        self._error = None
        self._namespace = {}
        
        self.agents = {}
        self.functions = []
        self.mcp_clients = {}
        
    def add_agents(
        self,
        agents: dict
    ):
        """
        Add agents to the processor.
        """
        self.agents.update(agents)
        
    def add_functions(
        self,
        functions: list
    ):
        """
        Add functions to the processor.
        """
        for func in functions:
            if isinstance(func, types.FunctionType):
                self.functions.append(func)
            else:
                raise TypeError("All items in functions must be callable.")
    
    def add_mcp_clients(
        self,
        mcp_clients: dict
    ):
        """
        Add MCP clients to the processor.
        """
        self.mcp_clients.update(mcp_clients)
        
    def _create_namespace(self):
        # Add agents to the namespace
        namespace = dict(self.agents)
        
        # Add MCP clients to the namespace
        namespace.update(self.mcp_clients)
        
        # Ensure we have the essential builtins
        namespace.update({
            '__name__': '__main__',
            '__builtins__': __builtins__,
            '__file__': '<string>'
        })
        
        # Add provided functions
        for func in self.functions:
            if isinstance(func, types.FunctionType):
                namespace[func.__name__] = func
        return namespace

    def _handle_timeout(self, signum, frame):
        raise TimeoutError(f"Timeout after {self.timeout} seconds")

    def _strip_ansi_codes(self, text):
        if not isinstance(text, str):
            return text
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def execute(
            self, 
            code: str
        ):
        
        original_stdout = sys.stdout
        sys.stdout = captured_output = LogFilteredStringIO()

        try:
            namespace = self._create_namespace()
            try:
                # Compile code first to catch syntax errors
                compiled_code = compile(code, '<string>', 'exec')
            except SyntaxError as e:
                # Handle syntax errors specifically
                return AgentPythonProcessorOutput(
                    output=None,
                    error=f"SyntaxError: {str(e)}",
                    is_error=True
                )
            
            if threading.current_thread() is threading.main_thread() and hasattr(signal, 'SIGALRM'):
                # Use signal-based timeout in main thread
                signal.signal(signal.SIGALRM, self._handle_timeout)
                signal.alarm(self.timeout)
                exec(compiled_code, namespace)
                signal.alarm(0)  # Clear alarm
            else:
                # Use thread-based timeout in non-main threads
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(exec, compiled_code, namespace)
                    try:
                        future.result(timeout=self.timeout)
                    except concurrent.futures.TimeoutError:
                        return AgentPythonProcessorOutput(
                            output=None,
                            error=f"TimeoutError: Execution timed out after {self.timeout} seconds",
                            is_error=True
                        )

            self._namespace = namespace
            
        except Exception as e:
            error_trace = traceback.format_exc()
            return AgentPythonProcessorOutput(
                output=None,
                error=self._strip_ansi_codes(f"{type(e).__name__}: {str(e)}\n{error_trace}"),
                is_error=True
            )

        finally:
            # Cleanup
            sys.stdout = original_stdout
            
            # Reset signal handler only if we're in main thread
            if threading.current_thread() is threading.main_thread() and hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, signal.SIG_DFL)
                
            return AgentPythonProcessorOutput(
                output=self._strip_ansi_codes(captured_output.getvalue()),
                error=None,
                is_error=False
            )