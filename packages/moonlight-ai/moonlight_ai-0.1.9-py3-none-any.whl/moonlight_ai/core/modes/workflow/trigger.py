import time, logging, threading, traceback
from datetime import datetime, timedelta
from textwrap import dedent

from ....core.agent_architecture import Agent, Hive
from ....core.modes.workflow.block_runner import BlockRunner

logger = logging.getLogger("hive")

class WorkflowTriggerException(Exception):
    pass

class WorkflowTrigger:
    def __init__(
            self, 
            trigger_block: dict, 
            all_agents: dict,
            model_name: str,
            provider: str,
        ):
        
        """
        Initialize the WorkflowTrigger with a workflow.
        
        Args:
            trigger_block (dict): The workflow to trigger
            all_agents (dict): A dictionary of all agents
            model (str): The model to use for the agent
            provider (str): The provider to use for the agent
        """
        
        self.trigger_block = trigger_block

        self.model_name = model_name
        self.provider = provider

        if not self.trigger_block:
            raise WorkflowTriggerException("Workflow must contain a trigger_block")
            
        self.block_runner = BlockRunner(
            all_agents=all_agents,
            model_name=self.model_name,
            provider=self.provider,
        )
        
        # Thread safety
        self._lock = threading.RLock()
        self.active = False
        self.condition_met = False
        self.last_check_time = None
        
        # Thread management
        self.thread = None
        self.stop_event = threading.Event()
        
        # Initialize condition checker agent
        self._init_condition_agent()
        
        # Parse the repeat interval
        self.interval = self._parse_repeat_interval(self.trigger_block.get("repeat", "1d"))
        
    def _init_condition_agent(self):
        """
        Initialize the agent for checking conditions.
        """
        
        condition_schema = dedent("""
        {
            "type": "object",
            "properties": {
                "condition_met": {
                    "type": "boolean",
                    "description": "Whether the condition is met based on the task output"
                }
            },
            "required": ["condition_met"]
        }
        """)
        
        condition_instructions = dedent("""
        You are a condition checker. Your sole purpose is to evaluate if a condition is met based on the provided output.
        You will return a boolean indicating whether the condition is met or not.
        """)
        
        self.condition_agent = Agent(
            name="Trigger Condition Agent",
            json_mode=True,
            json_schema=condition_schema,
            provider=self.provider,
            model_name=self.model_name,
            instruction=condition_instructions,
            description="Evaluates if a trigger condition is met",
        )
    
    def _parse_repeat_interval(self, repeat):
        """
        Parse the repeat interval string to seconds.
        """
        
        if not repeat or not isinstance(repeat, str):
            return 86400  # Default to 1 day (in seconds)
        
        unit = repeat[-1]
        try:
            value = int(repeat[:-1])
        except ValueError:
            return 86400  # Default to 1 day if parsing fails
        
        # Convert to seconds based on unit
        if unit == 'm':
            return value * 60  # minutes to seconds
        elif unit == 'h':
            return value * 3600  # hours to seconds
        elif unit == 'd':
            return value * 86400  # days to seconds
        elif unit == 'w':
            return value * 604800  # weeks to seconds
        elif unit == 'y':
            return value * 31536000  # years to seconds
        else:
            return 86400  # Default to 1 day for unknown units
    
    def _check_condition(self, task_output, condition):
        """
        Check if the condition is met based on the task output.
        """
        
        condition_prompt = dedent(f"""
        Evaluate if the condition is met based on the output of the task.

        Task Output:
        ```
        {task_output}
        ```
          
        Condition:
        ```
        {condition}
        ```
        
        Return true if the condition is met, false otherwise.
        """).strip()
        
        print("-" * 100)
        print(f"Checking condition: {condition}")
        
        result = Hive(self.condition_agent).run(condition_prompt)
        print(f"Result of Check Condition: {result}")
        condition_met = result.get("condition_met", False)
        
        print(f"Condition met: {condition_met}")
        print("-" * 100)
        
        return condition_met
    
    def _run_trigger_block(self):
        print(f'Trigger block: {self.trigger_block}')
        
        current_time = datetime.now()
        with self._lock:
            self.last_check_time = current_time
        
        print(f"Running trigger at {current_time}")
        
        # Extract trigger block details
        task = self.trigger_block.get("task", "")
        condition = self.trigger_block.get("condition", "")
        
        # Run the trigger block
        try:
            task_output = self.block_runner.run(
                block=self.trigger_block, 
                task=task
            )
                
            # Convert to string if needed for display
            display_output = str(task_output)
            print(f"Task output: {display_output[:200]}...")
            
            # Check if the condition is met
            condition_result = self._check_condition(
                task_output, 
                condition
            )
            
            with self._lock:
                self.condition_met = condition_result
                
        except Exception as e:
            error_message = str(e)
            traceback_info = traceback.format_exc()
            logger.error(f"Error running trigger: {error_message}")
            logger.error(f"Traceback: {traceback_info}")

    def _format_interval(self, seconds):
        """
        Format the interval in a human-readable way.
        """
        
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.1f} minutes"
        elif seconds < 86400:
            return f"{seconds/3600:.1f} hours"
        elif seconds < 604800:
            return f"{seconds/86400:.1f} days"
        elif seconds < 31536000:
            return f"{seconds/604800:.1f} weeks"
        else:
            return f"{seconds/31536000:.1f} years"

    def _trigger_loop(self):
        """
        Main loop for the trigger thread.
        """
        print("Trigger loop started")
        
        # Initialize the first scheduled run time
        next_scheduled_run = datetime.now()
        
        while not self.stop_event.is_set():
            current_time = datetime.now()
            
            # Check if it's time for the next scheduled run
            if current_time >= next_scheduled_run:
                with self._lock:
                    condition_is_met = self.condition_met
                
                # Only run the block if condition is not already met
                if not condition_is_met:
                    print("Running scheduled trigger check")
                    self._run_trigger_block()
                else:
                    print("Skipping trigger run as condition is already met")
                
                # Calculate next run based on the interval, regardless of whether we ran or not
                next_scheduled_run = current_time + timedelta(seconds=self.interval)
                print(f"Next scheduled run at: {next_scheduled_run.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Sleep to avoid using 100% CPU (check every second)
            time.sleep(1)
        
        print("Trigger loop terminated")
        
    def is_condition_met(self):
        """
        Check if the trigger condition was met in the last run.
        """
        with self._lock:
            if not self.active:
                raise WorkflowTriggerException("Trigger is not active")
            return self.condition_met
            
    def reset_condition(self):
        """
        Reset the condition to False.
        """
        with self._lock:
            was_met = self.condition_met
            self.condition_met = False
            
        if was_met:
            print("Trigger condition reset to False")
  
    def is_active(self):
        """
        Check if the trigger is active.
        """
        with self._lock:
            return self.active

    def start(self):
        """
        Start the trigger if not already active.
        """
        with self._lock:
            if self.active:
                logger.warning("Trigger is already active")
                return False
            
            self.active = True
            
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._trigger_loop, daemon=True)
        self.thread.start()
        print(f"Trigger started with interval: {self.interval} seconds ({self._format_interval(self.interval)})")
        return True

    def stop(self):
        """
        Stop the trigger.
        """
        with self._lock:
            if not self.active:
                return
                
            self.active = False
            
        if self.thread and self.thread.is_alive():
            print("Stopping trigger thread...")
            self.stop_event.set()
            self.thread.join(timeout=2)  # Wait up to 2 seconds for thread to terminate
            print("Trigger stopped successfully")