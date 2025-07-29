from textwrap import dedent

from ....core.agent_architecture import Agent, Hive

class WorkflowGenerationException(Exception):
    pass

class WorkflowGenerator:
    def __init__(
            self,
            model_name: str,
            provider: str,
            available_agents: dict,
            helper: bool = False
        ):
        
        # Store agents
        self.all_agents = available_agents
        
        # model_name and provider
        self.model_name = model_name
        self.provider = provider
        
        # Convert to string for prompts and system roles.
        self.available_agents = "".join(f"{i+1}. {agent.name}: {agent.description}\n\n" for i, agent in enumerate(available_agents.values()))
        
        # Parameters
        self.helper = helper
        
        # Initialize agents
        self._init_workflow_agent()
                
    def _init_workflow_agent(self):
        workflow_schema = dedent("""
        {
            "type": "object",
            "properties": {
                "blocks": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["agent", "orhcestra", "deepresearch"]
                            },
                            "agent_name": {"type": "string"},
                            "connected_to": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "next_block": {"type": "string"},
                                        "condition": {"type": "string"}
                                    },
                                    "required": ["next_block", "condition"]
                                }
                            },
                            "task": {"type": "string"},
                            "orhcestra_agents": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["type", "connected_to", "task"]
                    }
                },
                "connections": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "trigger_block": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["agent", "orhcestra"]
                        },
                        "condition": {"type": "string"},
                        "repeat": {
                            "type": "string",
                            "pattern": "^\\\\d+[dwmyh]$"
                        },
                        "task": {"type": "string"},
                        "agent_name": {"type": "string"},
                        "orhcestra_agents": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["type", "condition", "repeat"]
                }
            },
            "required": ["blocks", "connections", "trigger_block"]
        }
        """).strip()
        
        workflow_instructions = dedent("""
        # Workflow Generator
        
        You are a specialized workflow generator that creates workflows based on provided instructions. Your task is to create a workflow that is complete and implementable based on the given instructions.
        You must not provide anything other than the workflow JSON object. Do not include any additional text or explanations.
        
        Response Format:
        1. For new workflows:
            Return a complete JSON object matching the schema with all required "blocks", "connections", and "trigger" properties.
        
        2. For workflow modifications:
            Return the entire workflow object with the necessary changes made given a previous workflow object.
        
        Descriptions:
        1. Agent: A block that represents an agent call. Agents are AI LLMs that can perform tasks and run python/shell codes. Tuned for specific tasks.
        2. orhcestra: A block that represents a orhcestra of agents. Will generate a plan given a task and distribute it among agents given to it. Will return the final result. Can be used for complex tasks that require multiple specialized agents and stages.
        3. Deepresearch: A block that represents a deep research task. Will find as much information as possible from the web.

        Important:
        1. Use only provided agents to create the blocks.
        2. For orhcestra blocks, use the provided agents in the orhcestra_agents list.
        3. Deepresearch does not need any agents or inputs other than the task.
        4. You can have multiple blocks in a branch if needed.
        
        Example for each block type:
        1. Agent block:
           ```
           "block_1": {
               "type": "agent",
               "agent_name": "data_analyst",
               "task": "Analyze the sales data and identify top-performing products",
               "connected_to": [
                   {
                       "next_block": "block_2",
                       "condition": "None"
                   }
               ]
           }
           ```
        
        2. orhcestra block:
           ```
           "block_3": {
               "type": "orhcestra",
               "task": "Create a comprehensive marketing strategy for the new product",
               "orhcestra_agents": ["market_researcher", "copywriter", "data_analyst"],
               "connected_to": [
                   {
                       "next_block": "block_4",
                       "condition": "Strategy is approved"
                   },
                   {
                       "next_block": "block_5",
                       "condition": "Strategy needs revision"
                   }
               ]
           }
           ```
        
        3. Deepresearch block:
           ```
           "block_4": {
               "type": "deepresearch",
               "task": "Research competitive products in the market and their pricing strategies",
               "connected_to": [
                   {
                       "next_block": "block_6",
                       "condition": "None"
                   }
               ]
           }
           ```
        
        4. Trigger Block:
              ```
              "trigger_block": {
                    "type": "agent", # Can be agent, orhcestra, deepresearch. Same as block type.
                    
                    "task": "Check for new nvidia product releases.",
                    "condition": "Is there new nvidia product releases this week?",
                    "repeat": "7d" # Repeat every 7 days                    
                    # Optional Properties same as block type.
                    "agent_name": "web_agent", 
              }
              ```
                
        Rules:
        1. Each block must have a unique identifier (block_1, block_2, etc.)
        2. Block types must be one of: agent, orhcestra, deepresearch
        3. orhcestra type blocks can have max 10 stages
        4. All blocks must specify their connections in connected_to with next_block and condition:
           - next_block: The ID of the next block to execute
           - condition: The condition for taking this path (use "None" for unconditional paths)
        5. All connections must be reflected in the connections object
        6. Every workflow must have exactly one trigger block in it's proper format. It can be agent or orhcestra.
        7. Optional properties (orhcestra_agents, agent_name) should only be included when relevant to block type
        8. The trigger block must have a condition property that specifies the condition for the trigger to activate.
        9. The trigger block must have a repeat property that specifies the frequency of the trigger.
        10. Trigger task is what the agent/orhcestra will do. The condition will check the condition against the task output. (same goes for block conditions).
        
        Validation:
        - Ensure all block IDs referenced in connections exist in blocks
        - Validate that all required properties are present based on block type
        - Select the most appropriate block type for each task in the workflow:
          * Use agent blocks for tasks requiring intelligence or code execution
          * Use orhcestra blocks for complex tasks requiring multiple specialized agents
          * Use deepresearch blocks for comprehensive information gathering from the web
        - First block and last block must not be connected to each other to prevent circular loop.
        - Ensure a clear path from the trigger to the end of the workflow.
        - The final block should not be connected to any other block.
        - No condition must be given when there are no branching out from a block.
        """).strip()
        
        workflow_instructions = dedent(f"""
            {workflow_instructions}
                   
            Available Agents:
            ```
            {dedent(self.available_agents).strip()}
            ```
        """).strip()
            
        self.workflow_agent = Agent(
            name="Workflow Agent",
            toolcall_enabled=False,
            json_mode=True,
            json_schema=workflow_schema,
            provider=self.provider,
            model_name=self.model_name,
            instruction=workflow_instructions,
            description="Creates and manages workflows",      
        )

    def _check_workflow(
            self, 
            workflow_details: str, 
            workflow: dict
        ):
        """
        Will attempt to check the workflow for correctness.
        """
        workflow_helper_instructions = dedent("""
        # Workflow Validator and Improvement Assistant

        You are a specialized workflow validator that ensures workflows are properly structured and implementable.

        ## Your Task
        Analyze provided workflows to verify:
        1. All blocks and connections are valid.
        2. Trigger is properly configured.
        3. Workflow logic is sound and achievable.
        4. Required agents exist.
        5. Conditions are clear and actionable.
        6. There should be a clear path from the trigger to the end of the workflow.
        7. The final block should not be connected to any other block.
        8. The workflow should be straight and not recursive or circular. (except when necessary and except the first and last blocks.)
        
        ## Example Input:
        {
            "blocks": {
                "block_1": {
                    "type": "agent",
                    "task": "Analyze market data"
                }
            },
            "trigger_block": {
                ...
            }
        }

        ## Example Response:
        {
            "correct": false,
            "changes": "Block 'block_1' is missing required 'connected_to' property. Agent name must be specified for agent type blocks."
        }

        OR

        {
            "correct": true,
            "changes": ""
        }

        Return a JSON object indicating if the workflow is correct and any needed changes.
        """)
        
        workflow_helper_instructions = dedent(f"""
        {workflow_helper_instructions}
                
        Available Agents:
        ```
        {dedent(self.available_agents).strip()}
        ```
        
        Schema for workflow:
        ```
        {{
            "blocks": {{
                "block_n" (must be block_number): {{
                    "type": <can be agent, orhcestra, deepresearch>,
                    "agent_name": <agent name if type is agent>,
                    "connected_to": [
                        {{
                            "next_block": "block_n",
                            "condition": "condition only if there are two blocks or more branching out from this, otherwise strictly should be None"
                        }},
                        {{
                            ..
                        }}
                    ],
                    "task": <task for the agent/orhcestra/deepresearch to carry out. Including details.>,
                    "orhcestra_agents": [
                        "agent1",
                        "agent2"
                        <only if orhcestra type, list of strings of agent names>
                    ]
                }}
            }},
            "connections": {{
                "block_n": [
                    "block_m",
                    "block_o"
                ],
                ...
            }},
            "trigger_block": {{
                "condition": "condition",
                "comparision": "comparision",
                "repeat": "any time duration in h, d, m, w, y format",
                ...
            }}  
        }}
        ```
        
        Note:
        - Each block will be given output of the previous block so the current block can work well (current block gets aggregated output of previous blocks).
        - Each block need not have any input as such since the previous block output will be automatically sent to the next blocks.
        - Ensure the agents exist.
        """).strip()
                
        workflow_helper_schema = dedent("""
        {
            "type": "object",
            "properties": {
                "correct": {
                    "type": "boolean",
                    "description": "Indicates if the workflow is correct"
                },
                "changes": {
                    "type": "string",
                    "description": "Changes needed in the workflow. If no changes are needed, this will be an empty string."
                }
            },
            "required": ["correct", "changes"]
        }
        """)
        
        workflow_helper_prompt = dedent(f"""
        Workflow Details:
        {workflow_details}
        
        Workflow:
        {workflow}
        """)
        
        self.workflow_helper_agent = Agent(
            name="Workflow Helper Agent",
            json_mode=True,
            json_schema=workflow_helper_schema,
            provider=self.provider,
            model_name=self.model_name,
            instruction=workflow_helper_instructions,
            description="Attempts to fix workflow",      
        )
        
        response = Hive(self.workflow_helper_agent).run(workflow_helper_prompt)
        
        # Clean
        correct = response.get("correct", False)
        if isinstance(correct, str):
            correct = correct.lower() == "true"
        changes = response.get("changes", "")
        
        return {
            "correct": correct,
            "changes": changes
        }
        
    def _generate_details(self, prompt) -> str:
        """
        Given a prompt, generate detailed workflow instructions.
        """
        workflow_details_agent_instructions = dedent("""
        # Workflow Details Generation Specialist

        You are an expert workflow details generator specialized in breaking down high-level tasks into concise, actionable sequences. Your expertise lies in creating clear, unambiguous workflows for automated execution.

        ## Your Role
        - Transform abstract prompts into concise, step-by-step workflow instructions
        - Ensure every workflow is complete and implementable
        - Use minimal but sufficient detail for each step
        - Keep instructions brief and to the point

        Your task is to generate concise workflow instructions based on the provided prompt.
        Avoid unnecessary elaboration or verbose descriptions.
        
        ## Example:
        Prompt:
        ```
        I need a workflow to automate market research for a high-end luxury watch launch.
        ```
        
        Workflow Details:
        ```
        1. Research niche trends in the luxury watch market using specialized online forums and databases.
        2. Analyze competitor high-end watch designs, pricing, and brand positioning.
        3. Generate a bespoke marketing strategy that highlights exclusivity and craftsmanship.
           3.1 Evaluate if the strategy requires refinement based on market sentiment.
        4. Compile an executive summary with detailed insights tailored for affluent clientele.
        5. Send the summary to the specialized executive team.
        ```
        
        ## Guidelines:
        1. Keep each step brief but clear
        2. Use hierarchical numbering for structure
        3. Include only essential details
        4. Focus on actionable instructions
        5. Return nothing but the workflow instructions
        """)
        
        cleaned_prompt = dedent(f"""
        Here is what the user asked:
        ```
        {prompt}
        ```
        
        DO NOT RUN THE PROMPT. DO NOT RETURN ANYTHING OTHER THAN THE WORKFLOW INSTRUCTIONS.
        DO NOT RETURN ANY EXPLANATIONS OR ADDITIONAL TEXT.
        """)
        
        workflow_details_agent = Agent(
            name="Workflow Details Agent",
            description="Expands workflow prompts into detailed instructions",
            provider=self.provider,
            model_name=self.model_name,
            instruction=workflow_details_agent_instructions,
            toolcall_enabled=False,
        )
        
        worflow_details = Hive(workflow_details_agent).run(cleaned_prompt).assistant_message
        
        return worflow_details
    
    def _get_feedback(
            self, 
            prompt: str, 
            previous_level_details: dict
        ) -> str:
        """
        Will read the detailed workflow instructions and expand them into a full workflow.
        Used for fixing the workflow instructions.
        """
                
        workflow_details_expander_agent_instructions = dedent("""
        # Workflow Details Expansion Specialist

        ## Your Role
        You are an expert workflow refinement specialist tasked with converting high-level workflow instructions into fully actionable, operational procedures. Your expertise lies in identifying gaps, ambiguities, and implementation challenges that would prevent a workflow from being executed successfully in real-world scenarios.

        ## Your Responsibilities
        1. Analyze workflow instructions with meticulous attention to detail
        2. Identify missing operational information, and ambiguous directives
        3. Formulate precise, targeted questions to obtain necessary information from users
        4. Provide constructive refinements that transform abstract instructions into concrete, actionable steps
        5. Ensure all dependencies, resources, and decision points are clearly defined

        Notes:
        - Your analysis should focus on the operational feasibility of the workflow instructions
        - You should not attempt to execute the workflow or provide implementation code
        - Ensure that you do not add a question that is dependant on a stage (for example, "what should I do if the task fails?", "what is the xyz mentioned in 4.1 stage", etc...). Since user cannot see the workflow, they cannot answer these questions.
        - Questions to user must not be nill. At least one question must be there.
        
        When provided with detailed workflow instructions, you will:

        1. Thoroughly analyze these instructions to identify any:
           - Ambiguous success criteria or decision points
           - Timing or sequencing issues
           - Missing contingency plans or error handling procedures
           - Undefined formats, templates, or standards
        
        2. Formulate specific, actionable questions for the user that:
           - Target exactly one piece of missing information per question
           - Are precisely phrased to elicit clear, actionable responses
           - Provide context on why the information is needed
           - Are prioritized by importance to workflow execution

        3. Provide a refined critique of the workflow with specific observations on:
           - Structural improvements needed
           - Logical inconsistencies or circular dependencies
           - Efficiency opportunities
           - Implementation challenges
           - Missing handoffs between steps

        For example (example only, not strict format):
        Previous Level Instructions:
        ```
        1. Research niche trends in the luxury watch market using specialized online forums and databases.
        2. Analyze competitor high-end watch designs, pricing, and brand positioning.
        3. Generate a bespoke marketing strategy that highlights exclusivity and craftsmanship.
            3.1 Evaluate if the strategy requires refinement based on market sentiment.
        4. Compile an executive summary with detailed insights tailored for affluent clientele.
        5. Send the summary to the specialized executive team.
        6. Schedule an exclusive follow-up consultation based on detailed feedback.
        ```

        Issues identified:
          - The criteria for evaluating market sentiment in step 3.1 lack quantifiable thresholds
          - The target recipients for the summary ("executive team") are undefined with no roles or contact information
          - The "executive team" is seemingly assumed.
          - The expected format, length, and key components of the executive summary aren't specified
          - The method for collecting and structuring feedback after distribution is unspecified
          - Follow-ups cannot be a part of the automated workflows.

        Expected Return for the Example:
        {
          "user_inputs": [
            "Who should I send the output to?",
            "Please provide the names, roles, and contact information for all members who should receive the summary.",
            "What is the required format, approximate length, and must-include sections for the executive summary?",
          ],
          "corrections": "The workflow requires significant operational detailing before implementation. The research phase needs specific evaluation criteria. The marketing strategy development lacks clear acceptance thresholds for the sentiment evaluation. The "executive team" needs to be replaced with actual team with their contact information. The executive summary section needs format specifications and distribution targets.
        }

        Your response should be a JSON object following the specified schema that addresses all potential implementation issues.
        """).strip()
        
        workflow_details_expander_json_schema = dedent("""
        {
            "type": "object",
            "properties": {
                "user_inputs": {
                    "type": "array",
                    "description": "An array of specific, actionable questions addressing individual information gaps. Each question should target a single piece of missing information critical for workflow execution. Questions should be phrased to elicit precise responses rather than open-ended discussions."
                },
                "corrections": {
                    "type": "string",
                    "description": "A comprehensive analysis of workflow deficiencies organized by execution impact. Identify structural issues, logical inconsistencies, missing dependencies, and implementation challenges while suggesting specific improvements that would transform the instructions into an actionable workflow."
                }
            },
            "required": ["user_inputs", "corrections"]
        }
        """).strip()
        
        feedback_prompt = dedent(f"""
        Here is the previous level:
        
        Previous Level:
        ```
        {previous_level_details}
        ```
        
        And the original prompt user asked:
        ```
        {prompt}
        ```
        
        DO NOT RETURN ANYTHING OTHER THAN THE JSON OBJECT. DO NOT RETURN ANY EXPLANATIONS OR ADDITIONAL TEXT.
        YOUR ONLY TASK IS TO BREAKDOWN THE PROMPT TO GET THE USER INPUTS AND CORRECTIONS.
        """).strip()
        
        workflow_details_expander_agent = Agent(
            name="Workflow Details Agent",
            description="Expands workflow details into ground reality.",
            provider=self.provider,
            model_name=self.model_name,
            instruction=workflow_details_expander_agent_instructions,
            json_mode=True,
            json_schema=workflow_details_expander_json_schema,
            toolcall_enabled=False
        )
        
        feedback = Hive(workflow_details_expander_agent).run(feedback_prompt)

        return feedback

    def _verify_connections(self, workflow):
        """
        Verify that all connections are valid comparing the connected_to and the connections.
        """
        blocks = workflow.get("blocks", {})
        connections = workflow.get("connections", {})

        for block_id, block in blocks.items():
            connected_to = block.get("connected_to", [])
            for connection in connected_to:
                next_block = connection.get("next_block")
                if next_block not in connections.get(block_id, []):
                    return False, f"Block '{next_block}' is not in the connections for block '{block_id}'"
        return True, ""
    
    def _verify_agents(self, workflow):
        """
        Verify that the agent exists.
        """
        blocks = workflow.get("blocks", {})
        
        for block_id, block in blocks.items():
            if block.get("type") == "agent":
                agent_name = block.get("agent_name", "")
                
                if not agent_name:
                    return False, f"Block '{block_id}' is missing required 'agent_name' property. Agent name must be specified for agent type blocks."
                
                if agent_name not in self.all_agents:
                    return False, f"Agent '{agent_name}' does not exist in the available agents."
        
        return True, ""
    
    def _check_agents_validity(
            self, 
            workflow: dict
        ):
        connections_correct, connections_error = self._verify_connections(workflow)
        agents_correct, agents_error = self._verify_agents(workflow)
        
        is_error = any([not connections_correct, not agents_correct])
        
        errors = dedent(f"""
        Connection Errors:
        ```
        {connections_error if not connections_correct else ""}
        ```
        
        Agent Errors:
        ```
        {agents_error if not agents_correct else ""}
        ```
        """)
        
        return is_error, errors
    
    def _get_new_workflow_prompt(
            self, 
            workflow: dict, 
            workflow_details: str, 
            changes: str
        ):
        
        is_error, errors = self._check_agents_validity(workflow=workflow)
        
        workflow_prompt = dedent(f"""
        Previous Workflow:
        ```
        {workflow}
        ```
        
        Workflow Details:
        ```
        {workflow_details}
        ```
        
        Changes:
        ```
        {changes}
        ```
        
        {errors if is_error else ""}
        
        Now edit the previous workflow based on the changes/feedback. Return full workflow.
        
        """).strip()
                
        return workflow_prompt
    
    def generate_first_level(
            self, 
            prompt: str
        ):
        """
        Generate a basic workflow based on the prompt.
        """
        if not prompt:
            raise WorkflowGenerationException("Prompt must be provided.")
        
        first_level_workflow = self._generate_details(prompt)
        
        feedback = self._get_feedback(
            prompt=prompt, 
            previous_level_details=first_level_workflow
        )
        
        critique = feedback.get("corrections", "")
        requirements_to_answer = feedback.get("user_inputs", [])

        output = {
            "first_level_workflow": first_level_workflow,
            "critique": critique,
            "requirements": requirements_to_answer    
        }
        
        return output
        
    def expand_first_workflow(
            self, 
            critique: str, 
            answered_requirements: list, 
            previous_level_details: str
        ): 
        
        next_prompt = dedent(f"""
        I will give you your previous output and additional details from user including constructive criticism and more parameters. Please update the workflow details appropriatelt based on the feedback.                     
        
        Here is your previous output:
        
        Previous:
        ```
        {previous_level_details}
        ```
        
        User Feedback:
        
        Details:
        ```
        {answered_requirements}
        ```
        
        Constructive Criticism:
        {critique}
        
        Return nothing but the new workflow details in full properly.
        """).strip()
        
        expanded_workflow_details = self._generate_details(next_prompt).strip("```")
        
        return expanded_workflow_details
    
    def generate_final_workflow(
            self,
            critique: str, 
            answered_requirements: list, 
            previous_level_details: str
        ):
        
        workflow_details = self.expand_first_workflow(
            critique=critique, 
            answered_requirements=answered_requirements, 
            previous_level_details=previous_level_details
        )
        
        if not workflow_details:
            raise WorkflowGenerationException("Expanded workflow failed to generate.")
          
        workflow_prompt = dedent(f"""
        Expanded and Detailed Requirements:
        ```
        {workflow_details}
        ```
        
        Now generate a workflow for the given requirements. Do not do anything other than generating workflow. Return full proper workflow.
        """).strip()
        
        
        # First pass
        workflow_generator = Hive(self.workflow_agent)
        workflow = workflow_generator.run(workflow_prompt)
                
        if not self.helper:   
            is_error, errors = self._check_agents_validity(workflow=workflow)

            while is_error:
                workflow = workflow_generator.run(f"Fix all the below issues and return new workflow. \n\n {errors}")
                is_error, errors = self._check_agents_validity(workflow=workflow)

            return workflow
    
        workflow_check = self._check_workflow(
            workflow_details=workflow_details, 
            workflow=workflow
        )
        
        is_workflow_correct = workflow_check['correct']
        changes = workflow_check['changes']
        
        if not is_workflow_correct:
            workflow_prompt = self._get_new_workflow_prompt(
                workflow=workflow, 
                workflow_details=workflow_details, 
                changes=changes
            )

        # proceeds when the workflow is not correct
        while not is_workflow_correct:
            # Generate workflow based on user feedback
            workflow = workflow_generator.run(workflow_prompt)
            
            # Check the new workflow
            workflow_check = self._check_workflow(
                workflow_details=workflow_details, 
                workflow=workflow
            )
            
            # Update correctness and changes
            is_workflow_correct = workflow_check['correct']
            
            # If the workflow is correct, break the loop
            if is_workflow_correct: break
            
            # If the workflow is incorrect, get the new workflow prompt
            changes = workflow_check['changes']
            
            # Get the new workflow prompt to be used in the next iteration
            workflow_prompt = self._get_new_workflow_prompt(
                workflow=workflow, 
                workflow_details=workflow_details, 
                changes=changes
            )

        return workflow