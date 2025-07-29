import logging, re
from textwrap import dedent

from ....core.agent_architecture import Agent, Hive
from ....core.modes.workflow.block_runner import BlockRunner

class WorkflowRunnerException(Exception):
    pass

logger = logging.getLogger("hive")

class WorkflowRunner:
    def __init__(
            self, 
            workflow: dict, 
            all_agents: dict, 
            model_name: str,
            provider: str,
        ):
        
        # Initalize agents
        self.all_agents = all_agents
        
        # Workflow Connection
        self.workflow = workflow

        # Model and Provider        
        self.model_name = model_name
        self.provider = provider
        
        # Initialize the condition agent
        self._init_conditional_agent()
    
    def _init_conditional_agent(self):
        condition_schema = dedent("""
        {
            "type": "object",
            "properties": {
                "next_block": {
                    "type": "string",
                    "description": "The ID of the block to execute next"
                }
            }
        }
        """)
        
        condition_instructions = dedent("""
        You are a condition checker. Your sole purpose is to evaluate the condition based on the provided parameters. You will return the ID of the next block to execute based on the condition.
        Evaluate condition based on output of previous block.
        """)
        
        self.condition_agent = Agent(
            name="Condition Agent",
            json_mode=True,
            json_schema=condition_schema,
            provider=self.provider,
            model_name=self.model_name,
            instruction=condition_instructions,
            description="Evaluates conditions and determines the next block to execute",
        )
        
    def _get_next_block(self, condition: str, previous_output: str):
        """
        Evaluate the condition to determine the next
        block to execute.
        """
        condition_prompt = dedent(f"""
        Evaluate the condition based on the output of the previous block.

        Previous Output:
        ```
        {previous_output}
        ```
          
        Condition:
        ```
        {condition}
        ```
        
        Evaluate properly and return the next block to execute. Just return the block number. Choose from the available blocks in condition only.
        """).strip()
        
        logger.info("-" * 100)
        logger.info(f"Condition: {condition_prompt}")
        
        logger.info("-" * 100)
        next_block = Hive(self.condition_agent).run(condition_prompt)
        logger.info(next_block)
        
        next_block_id = next_block.get("next_block")
        
        ########################################################################
        # Clean the next block id cuz llm is irresponsible
        if "none" in next_block_id.lower():
            raise WorkflowRunnerException("Next block id is None")

        if "block" in next_block_id.lower():
            match = re.search(r'block_?(\d+)', next_block_id.lower())
            if match:
                block_number = match.group(1)
                next_block_id = f'block_{block_number}'
            else:
                raise WorkflowRunnerException(f"Could not extract block number from {next_block_id}")
        else:
            next_block_id = f'block_{next_block_id}'
    
        logger.info(next_block_id)
        ########################################################################
        
        return next_block_id
            
    def run(self):
        blocks = self.workflow.get("blocks", {})
        
        aggregated_output = {}

        # Run each block. Start with the block 1.
        block_id = "block_1"
        block = blocks[block_id]
        
        block_runner = BlockRunner(
            all_agents=self.all_agents,
            model_name=self.model_name,
            provider=self.provider,
        )
        
        path = []
        
        while True:
            path.append(block_id)
            
            logger.info(f'Running block: {block_id}')

            # get all info about that block
            connected_to = block.get("connected_to", [])
            logger.info(f"CONNECTED TO: {connected_to}")
                        
            task = block.get("task") # task for the agent/Orchestra/deepresearch to carry out
            
            #########################################################################################################
            # build task for agent/Orchestra/deepresearch that includes previous block output
            historical_task = ""
            historical_task += dedent(f"""
            Here is your task that you need to carry out:
            ```
            {task}
            ```
            
            I will give you the outputs of previous blocks for reference. Use that information if needed.
            Make sure to run your task properly. The previous block outputs are just for reference if needed.
            
            Here are the outputs of the previous blocks (if any):
            ```
            """)
            
            for prev_block_id, prev_block_info in aggregated_output.items():
                prev_task = prev_block_info.get("task", "")
                prev_output = prev_block_info.get("output", "")
                historical_task += f"Block ID: {prev_block_id}\nTask: {prev_task}\nOutput: {prev_output}\n\n"
            
            historical_task += dedent(f"""
            ```
            """)
            #########################################################################################################

            block_output = block_runner.run(
                task=historical_task,
                block=block
            )

            # Store the output of the block
            aggregated_output[block_id] = {
                "task": task,
                "output": block_output
            }
            
            logger.info(f'Block Info: {block_id}\n\n Task: {task}\n\n Output: {block_output}\n\n')
            
            # Check if there are any connections to the next block.
            if not connected_to:
                break

            # if there are multiple connections, evaluate the condition to determine the next block.            
            conditions = ""
            next_block_branching = False
            
            for connection in connected_to:
                next_block_id = connection.get("next_block")
                condition = connection.get("condition")
                
                if condition != "None":
                    next_block_branching = True
                    
                    conditions += dedent(f"""
                    ---
                    
                    If Condition:
                    ```
                    {condition}
                    ```
                    
                    is met, then go to block:
                    ```
                    {next_block_id}
                    ```
                    """)

            # evaluate the condition to determine the next block
            if next_block_branching:
                next_block_id = self._get_next_block(condition=conditions, previous_output=block_output)
            else:
                next_block_id = connected_to.get("next_block")
                
            # if next block is None, it means the workflow has ended
            if next_block_id == "None":
                break
            
            # update the block_id with the next block_id and repeat the process
            block_id = next_block_id
            block = blocks[block_id]

        return aggregated_output