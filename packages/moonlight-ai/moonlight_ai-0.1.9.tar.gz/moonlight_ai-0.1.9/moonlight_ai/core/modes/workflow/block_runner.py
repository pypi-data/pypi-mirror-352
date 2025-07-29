from ....core.agent_architecture import Hive
from ....core.modes.orchestrator import Orchestra
from ....core.modes.deepsearch import DeepResearcher

class WorkflowRunnerException(Exception):
    pass

class BlockRunner:
    def __init__(
        self,
        all_agents: dict,
        model_name: str,
        provider: str,
    ):
        self.all_agents = all_agents

        self.model_name = model_name
        self.provider = provider
        
    def _validate_block_type(self, type: str):
        """
        Validate the block type.
        """
        if type not in ["agent", "orchestra", "deepresearch"]:
            raise WorkflowRunnerException("Invalid block type. Must be one of: agent, orchestra, deepresearch.")

    def _run_agent(
            self, 
            agent_name: str,
            task: str
        ):
        
        """
        Run the agent with the given task and parameters.
        """
        agent = self.all_agents.get(agent_name)        
        if not agent:
            raise WorkflowRunnerException(f"Agent '{agent_name}' not found. Available agents: {list(self.all_agents.keys())}")
        
        agent.toolcall_enabled = True
        
        results = Hive(agent).run(task)
        
        agent_response = results.assistant_message
        
        return agent_response
    
    def _run_orchestra(
        self,
        task: str,
        orchestra_agents: list
    ):
        """
        Run the orchestra with the given task and agents.
        """
        
        # Keep only orchestra_agents from the dictionary of all_agents
        try:
            orchestra_agents = {agent_name: self.all_agents[agent_name] for agent_name in orchestra_agents}
        except Exception as e:
            raise WorkflowRunnerException(f"Error in selecting agents for the orchestra: {e}")
        
        if not orchestra_agents:
            raise WorkflowRunnerException("No agents found for the orchestra. Please specify at least one agent.")
        
        # initialize orchestra
        orchestra = Orchestra(
            orchestra_model=self.model_name,
            orchestra_provider=self.provider,
        )
        
        # add agents and task to orchestra
        orchestra.add_agents(orchestra_agents)
        orchestra.add_task(task)
        
        # activate orchestra
        orchestra.activate()
        
        # Get task summary
        results = orchestra.task_summary
        
        # Optionally get output at all stages of orchestra (uncecessary for now)
        # results = orchestra.orchestra_task
        
        return results
    
    def _run_deepresearch(
        self,
        task: str,
    ):
        """
        Run the deepresearch task.
        """
        
        # build the deepresearcher        
        deep_researcher = DeepResearcher(
            model=self.model,
            provider=self.provider,
            research_task=task,
            max_depth=1, # maximum depth of the search, do not exceed 2 or it will take too long
            breadth=1, # same as above
            links_per_query=1, # don't exceed 10
            max_content_length=100, # above 1000 will lead to issues. 1000 is already a stretch
        )
        
        # run the deepresearcher
        deep_researcher.run()
        
        # get the results
        results = deep_researcher.output
        
        return results
    
    def run(
            self, 
            block: dict, 
            task: str
        ) -> str:
        
        # validate block type
        block_type = block.get("type")
        self._validate_block_type(block_type)
        
        # get optional parameters
        agent_name = block.get("agent_name", "") # name of the agent
        orchestra_agents = block.get("orchestra_agents", []) # list of agents for orchestra type
               
        # Run the block based on the type
        if block_type == "agent":
            if not agent_name:
                raise WorkflowRunnerException("Agent name must be specified for agent type blocks.")
            block_output = self._run_agent(agent_name=agent_name, task=task)
        elif block_type == "orchestra":
            if not orchestra_agents:
                raise WorkflowRunnerException("List of orchestra agents must be specified for orchestra type blocks.")
            block_output = self._run_orchestra(task=task, orchestra_agents=orchestra_agents)
        elif block_type == "deepresearch":
            block_output = self._run_deepresearch(task=task)
            
        return block_output