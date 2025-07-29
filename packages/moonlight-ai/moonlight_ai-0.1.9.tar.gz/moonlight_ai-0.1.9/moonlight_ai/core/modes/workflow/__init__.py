import logging
from textwrap import dedent

from .runner import WorkflowRunner
from .trigger import WorkflowTrigger

# Exporting the WorkflowGenerator class for external use
from .generator import WorkflowGenerator

class WorkflowException(Exception):
    pass

logger = logging.getLogger("hive")

class Workflow:
    def __init__(
            self, 
            workflow: dict, 
            available_agents: dict, 
            model_name: str,
            provider: str,
        ):
        
        self.workflow = workflow
        self.model_name = model_name
        self.provider = provider
        self.available_agents = available_agents
        self._setup_agents_instructions()
        
        self.trigger_block = workflow.get("trigger_block", {})
        
        if not self.trigger_block:
            raise WorkflowException("Trigger block is missing.")
        
        self.runner = WorkflowRunner(
            all_agents=available_agents,
            workflow=workflow,
            model_name=self.model_name,
            provider=self.provider,
        )
        
        self.trigger = WorkflowTrigger(
            all_agents=available_agents,
            trigger_block=self.trigger_block,
            model_name=self.model_name,
            provider=self.provider,

        )
       
    def _setup_agents_instructions(self):
        """
        Setup the instructions for all agents in the workflow.
        """
        for agent in self.available_agents.values():
            agent.instruction = dedent(f"""
            You are a {agent.name} Agent. Your sole purpose is mentioned below.
            
            Purpose:
            ```
            {agent.instruction}
            ```
            
            Ensure you do nothing other than what is mentioned in your purpose.
            Your purpose is your only goal. Do not deviate from it. Use the purpose to finish your task.
            """)
            
            agent.refresh_role()
            
    def run(self):
        self.trigger.start()
        
        try:
            logger.info("Trigger running")
            
            while True:
                if self.trigger.is_condition_met():
                    logger.info("Workflow execution started.")
                    self.runner.run()
                    logger.info("Workflow execution completed.")
                    self.trigger.reset_condition()
        finally:
            self.trigger.stop()
            logger.info("Trigger stopped.")