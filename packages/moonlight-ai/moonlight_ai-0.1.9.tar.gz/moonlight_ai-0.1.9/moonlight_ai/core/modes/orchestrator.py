import re, json, logging
from textwrap import dedent

from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text

from ...src.json_parser import parse_json
from ...core.agent_architecture import Hive, Agent, MoonlightProvider

logger = logging.getLogger("hive")

console = Console()

class OrchestraException(Exception):
    pass

class OrchestraOutput:
    def __init__(
        self, 
        orchestra_task, 
        task_summary
    ):
        self.orchestra_task = orchestra_task
        self.task_summary = task_summary
            
    def __repr__(self):
        console.rule(title="[bold green]Orchestra Execution Report[/bold green]", style="green")
        
        # Print task in a panel
        task_panel = Panel(
            self.orchestra_task.task,
            title="[bold blue]Task[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        console.print(task_panel)
        console.print()
        
        # Print stages and outputs
        console.print("[bold magenta]Execution Stages:[/bold magenta]")
        console.print()
        
        for i, (stage, details) in enumerate(self.orchestra_task.plan.items(), 1):
            # Create a clean stage header
            stage_title = f"Stage {i}"
            console.print(f"[bold cyan]{stage_title}[/bold cyan]")
            console.print(f"[dim]Task:[/dim] {details.get('task', 'No task defined')}")
            console.print(f"[dim]Details:[/dim] {details.get('details', 'No details provided')}")
            console.print(f"[dim]Expected Output:[/dim] {details.get('expected_output', 'No expected output defined')}")
            
            # Status indicator
            status = details.get('status', 'Not started')
            status_color = "green" if status == "completed" else "yellow" if status == "in_progress" else "red"
            console.print(f"[dim]Status:[/dim] [{status_color}]{status}[/{status_color}]")
            
            # Output in a panel if it exists
            output = details.get('output', 'No output yet')
            if output and output != 'No output yet':
                output_panel = Panel(
                    output,
                    title="[dim]Output[/dim]",
                    border_style="dim",
                    padding=(0, 1)
                )
                console.print(output_panel)
            else:
                console.print(f"[dim italic]No output generated[/dim italic]")
            
            console.print()
        
        # Print summary in a highlighted panel
        if hasattr(self, 'task_summary') and self.task_summary:
            summary_panel = Panel(
                Markdown(self.task_summary),
                title="[bold yellow]Final Summary[/bold yellow]",
                border_style="yellow",
                padding=(1, 2)
            )
            console.print(summary_panel)
        
        console.rule(style="green")
        return ""
    
class OrchestraTask:
    def __init__(
            self, 
            task: str, 
            plan: dict
        ):
        self._init_vars()
        self.task = task
        if isinstance(plan, dict):
            self._clean_plan(plan)
        else:
            raise OrchestraException(f"Invalid plan format. Expected dict, got {type(plan)}")
        self.stage_output = {stage: "" for stage in self.plan.keys()}
        
    def _init_vars(self):
        self.output = None
        self.current_task = None
        self.next_task = None
    
    def _clean_plan(
            self, 
            plan: dict
        ):
        self.plan = {}
        
        for stage, content in plan.items():
            if not isinstance(content, dict):
                raise OrchestraException(f"Invalid stage content format for {stage}")
                
            self.plan[stage] = {
                "task": content.get("task", "No task provided."),
                "details": content.get("details", "No details provided."),
                "expected_output": content.get("expected_output", "No expected output."),
                "output": None,
                "status": None
            }
        
    def update_current_stage(
            self, 
            stage: str
        ):            
        self.current_task = self.plan.get(stage, None)
        self.next_task = self.plan.get(f"stage_{int(stage.split('_')[1]) + 1}", None)
    
    def __repr__(self):
        return f"OrchestraTask(task={self.task})"

    def __str__(self):
        out_str = "=" * 20 + "\n"
        out_str += f"OrchestraTask(task={self.task}) \n\n Plan: {self.plan} \n\n Output: {self.output}"
        out_str += "\n" + "=" * 20
        return out_str
        
class Orchestra:
    def __init__(
            self, 
            orchestra_model: str,
            provider: MoonlightProvider,
            no_prints: bool = False
        ):
        
        self.agents = {}
        
        self.orchestra_task = None
        
        self.orchestra_model = orchestra_model
        self.orchestra_provider = provider
        self.no_prints = no_prints
        self.progress = None
        self.task_id = None
        
        self.orchestral_instructions = dedent(f"""
        ## Your Sole Purpose
        - Complete the assigned task accurately and efficiently.

        ## Your Name
        - Orhcestrator Agent

        ##  Current Contextual Information
        - The current year is 2025.

        ## Core Mission Briefing
        1.  You will receive specific details for a task.
        2.  Your objective is to complete this task precisely as instructed, adhering to all guidelines below.

        ## Key Operational Directives & Behavioral Protocols (Strict Adherence Required)

        ### Accuracy and Factual Integrity
        - NEVER hallucinate or invent information. All outputs must be based on verifiable data or the results from provided tools.
        - Do not make up any facts or details.

        ### Adherence to Plan & Instructions
        - Strictly follow the provided plan and all instructions.
        - Diverge from the plan ONLY if absolutely necessary and clearly justified.
        - Follow ALL instructions and notes meticulously.

        ### Autonomous Operation & Inter-Agent Coordination
        - **You CANNOT ask the end-user (the entity that invoked you, Orhcestrator Agent) for any clarification.** You do not have the ability to receive direct user input during your execution.
        - **If a sub-agent asks YOU (Orhcestrator Agent) a question or for further input, YOU must take charge.** This means you need to:
            - Decide on the appropriate response based on the task and context.
            - Use the `run_agent` function again with the questioning agent and your formulated response/instruction.
            - Example: If `search_agent` asks, "Do you need the full content of the article?", you should respond by calling `run_agent(search_agent, "Yes please, provide the full content")` or a similar directive.
        - Your role involves agent co-ordination, not seeking external guidance mid-task.
        - **Do not ask the user for any clarifications or confirmations. You are expected to execute the task as per the instructions provided.**

        ### Task Completion Criteria
        - A task is considered complete when you provide the correct and detailed output.
        - Python code is not mandatory for task completion if the output itself is accurate and fulfills the request.

        ### Resource Utilization (Agents & Tools)
        - Use ONLY the agents and functions provided within your parameters.
        - Make correct and appropriate tool calls, using suitable parameters as defined.
        - If an agent is required, you will be provided with it as a parameter; use the `run_agent()` function to execute it, as detailed in the "Agent Interaction Protocol" section.

        ### Efficiency and Focus
        - Answer directly and to the point. Avoid unnecessary verbosity.
        - Provide only relevant information. Do not conduct exhaustive searches or provide excessive detail unless explicitly requested by the user or necessary for the task.
        - If detailed answers are not requested, focus solely on what the user has asked for.
        - When interacting with other agents, provide clear and concise instructions or responses. You do not need to reflect the output of agent 1:1 in your subsequent call to another agent; simply provide the necessary input or decision.

        ### Problem Solving & Persistence
        - Do not get stuck on a single sub-task. Attempt it at most twice before reassessing or moving to the next step if appropriate.
        - Avoid retrying the exact same approach repeatedly unless you have a strong, identifiable reason why it might now succeed.

        ### Contextual Understanding & Continuity
        - If a step depends on information from a previous step, utilize that existing information. Do not repeat operations unnecessarily.
        - Pay close attention to contextual clues in the task description. Integrate this understanding throughout all parts of your plan and execution.
        - All previous stages and their outputs are available to you. Use them as needed. Do not redo the operations in a different stage of the plan for no reason.
        - If a task requires continuity, ensure that you maintain the context and flow of the task throughout all stages.
        - Example for Continuity: If asked, "What is [X] in [specific context], and what do people think about it on the internet?" For the second part, your internet search should be: "what do people think about [X] in [specific context]" to ensure precise results.
        - **Agent Memory:** Agents have the capability to remember their output history within a given interaction sequence (i.e., during a single stage of your plan). This memory will typically be auto-cleared after each stage completes. (See "Clearing Agent Context" for manual overrides if needed within a stage).

        ## Agent Interaction Protocol

        The `run_agent` function is your primary method for interacting with other agents.

        ### Executing and Conversing with an Agent
        - Use `run_agent` to provide an agent with its initial task or query.
        - **Crucially, if an agent asks YOU (Orchestrator Agent) for further input, clarification, or a decision, you must use `run_agent` again with that *same agent* to provide your response or next instruction.**
            - For example, if `research_agent` asks, "I found three relevant documents. Should I summarize all of them?", you might call:
              `run_agent(
                  agent=research_agent, 
                  message="Yes, please summarize all three documents."
              )`
              OR
              `run_agent(
                  agent=research_agent, 
                  message="No, just summarize the first one for now."
                )`
        - You can use an agent as if you are having a back-and-forth conversation to guide it towards completing its part of the task. It's not limited to one-off instructions.

        ```run_python
        # Replace xyz_agent with the actual agent object from your parameters
        # Replace "Query, Task, or Response for Agent" with the specific input
        agent_output = run_agent(
            agent=xyz_agent, 
            message="Query, Task, or Response for Agent"
        )
        print(agent_output) # This will return the agent's output
        ```

        ### Agent Output Handling
        - The output from `run_agent` is what the sub-agent has returned.
        - You do not need to reflect the raw output of one agent directly into the input of the next `run_agent` call unless it's precisely what's needed. Often, you will process or interpret an agent's output to formulate your next action or instruction.

        ### Clearing Agent Context (if necessary *within* a stage)
        - Agents remember their interaction history within a stage. This history is auto-cleared after each stage.
        - However, if an agent encounters context limit issues *during a stage*, or its prior interactions within that same stage are interfering with a new sub-task for that agent, you can manually clear its history for that stage.
        ```run_python
        # Replace xyz_agent with the actual agent object
        xyz_agent.history.clear_history()
        ```
        
        ## Note on Compliance
        - Adherence to these directives is paramount for successful task completion.
        - Non-compliance may result in task failure or suboptimal outcomes.
        """).strip()

        self.orchestrator = Agent(
            name = "Orchestrator Agent",
            description = "The First, the Main, the orchestrator.",
            instruction = self.orchestral_instructions,
            
            orchestra_mode = True,
            toolcall_enabled=True,
            enable_base_functions=False,
            
            sub_agents = self.agents,
            
            model_name = self.orchestra_model,
            provider=self.orchestra_provider,
        )
        
        # Backup of the orchestrator agent to refresh the orchestra with the latest agents and plan.
        self.orchestrator_backup = Agent(
            name = "Orchestrator Agent",
            description = "The First, the Main, the orchestrator.",
            instruction = self.orchestral_instructions,
            
            orchestra_mode = True,
            toolcall_enabled=True,
            enable_base_functions=False,
            
            sub_agents = self.agents,
            
            model_name = self.orchestra_model,
            provider=self.orchestra_provider,
        )
        
        self._initialize_state_variables()
    
    def _print(self, message: str, style: str = None):
        """Print message only if no_prints is False"""
        if not self.no_prints:
            if style:
                console.print(message, style=style)
            else:
                console.print(message)
    
    def _print_panel(self, content, title: str = None, style: str = "blue"):
        """Print panel only if no_prints is False"""
        if not self.no_prints:
            console.print(Panel(content, title=title, border_style=style))
    
    def _init_progress(self, total_stages: int):
        """Initialize progress bar"""
        if not self.no_prints:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                TimeElapsedColumn(),
                console=console,
                transient=False
            )
            self.task_id = self.progress.add_task(
                "Initializing orchestra...", 
                total=total_stages
            )
    
    def _update_progress(self, description: str = None):
        """Update progress bar"""
        if not self.no_prints and self.progress and self.task_id is not None:
            if description:
                self.progress.update(self.task_id, description=description, advance=1)
            else:
                self.progress.update(self.task_id, advance=1)
    
    def add_agents(self, agents: dict):
        self.agents.update(agents)
        
        if not all([isinstance(agent, Agent) for agent in self.agents.values()]):
            raise ValueError("All agents must be of type Agent.")
        
        if not all([key.endswith("_agent") for key in self.agents.keys()]):
            raise ValueError("All agents must end with '_agent'. Example: {'math_agent': math_agent}")
        
        if any(["final" in key for key in self.agents.keys()]):
            raise ValueError("No agent with 'final' in its name allowed.")

    def _initialize_state_variables(self):
        self._planning = False
        self._orchestra_running = False
            
    def _run_json_agent(
            self, 
            instruction, 
            prompt, 
            json_schema=None
        ):
        
        json_agent = Agent(
            name = "Json Agent",
            description="Agent that provides a json output.",
            instruction=instruction,
            
            json_schema=json_schema,
            json_mode=True,

            
            model_name = self.orchestra_model,
            provider=self.orchestra_provider       
        )
        
        try:
            json_output = Hive(json_agent).run(prompt)
            # Additional validation that the output is proper JSON
            if isinstance(json_output, (dict, list)):
                return json_output
        except Exception as e:
            logger.error(f"JSON agent error: {str(e)}")
            # Return a minimal valid JSON response
            return {"error": str(e), "summary": "Failed to generate valid JSON output"}
    
    def _get_task_summary(self):
        """
        You will be given "Task" which will be user's task and "Execution" which will be the plan and its output at each stage. Based on the task and the plan, provide a final response to the provided task. Make sure it's clean and matches what the user is looking for. 
        
        Notes:
        - Return only the summary of the task based on the execution.
        - Do not include any other information.
        - Do not include any toolcalls, python code is allowed only if it's part of the summary.
        - Cleanly formatted markdown is expected.
        - Provide it as a single summary thats easy to read and understand rather than summarizing it stage by stage (single summary that looks like a report).
        """
        
        instructions = dedent("""        
        ## Your Role: Final Response Generator

        ## Primary Objective
        Based on the provided "Task" (the user's original request) and "Execution" (the detailed plan and its outputs at each stage), your sole purpose is to construct a final, consolidated response that directly and comprehensively answers the user's "Task".

        ## Input You Will Receive:
        - `Task`: The user's initial query or problem statement.
        - `Execution`: The step-by-step plan undertaken to address the `Task`, including the outputs and results from each stage.

        ## Output Requirements (Strict Adherence Necessary):

        1. Core Content & Focus:
            - Your output must be a summary that serves as the definitive answer to the `Task`.
            - This summary must be entirely derived from the information and results presented in the `Execution` data.
            - Ensure the summary directly addresses all aspects of the user's `Task`.

        2.  Exclusivity of Information:
            - Return ONLY the final summary.
            - Do not include any other information: This means no explanations of your summarization process, no recounting of intermediate steps from the `Execution` (unless intrinsically part of the final answer), no self-commentary, and no metadata.

        3.  Format & Presentation:
            - The summary must be presented in **cleanly formatted markdown**.
            - It should be structured as a **single, coherent, and easy-to-read response**. Think of it as a final report or a direct answer, *not* a stage-by-stage recapitulation of the `Execution` details.

        4.  Code & Tool Calls:
            - Your final output **must NOT include any tool call syntax or internal agent instructions.**
            - Python code (or any other code) is permissible **only if it is an integral part of the answer to the `Task` itself** and was explicitly provided as a result within the `Execution` (e.g., if the `Task` was "provide a Python script for X," and the script was an output in the `Execution`).

        Guiding Principle:
        Your output is the **final answer** the end-user receives. It must be clear, accurate, and precisely address what the user asked for in the `Task`, using only the information provided through the `Execution` process.
        """).strip()
        
        prompt = dedent(f"""
        Follow your system instructions and provide the final summary based on the task and execution provided below.

        Task/User's request:
        ```
        {self.orchestra_task.task}
        ```

        Execution/AI's Work (Plan and Results from AI Agents):
        ```
        {json.dumps(self.orchestra_task.plan)}
        ```

        Your Instructions for Generating the Final Response:

        1. Primary Goal: Based *exclusively* on the 'Execution/AI's Work' provided above, construct a detailed and consolidated summary that directly and fully answers the 'Task/User's request'.
        2. Content Focus:
            - The summary must be the complete, user-facing answer to their task.
            - Synthesize information from all relevant stages and results within the 'Execution/AI's Work' into a single, coherent, and easy-to-understand narrative.
            - Address all aspects of the original 'Task/User's request'.
        3. Structure and Formatting:
            - Present the summary in clean, well-structured markdown.
            - The response should be a single, unified report, not a list of stage-by-stage summaries.
        4. Strict Exclusions:
            - Return **nothing but** the final summary.
            - Do not include:
                - Any mention of internal processes, stages, or agent operations (unless the task was specifically about that process).
                - Explanations of how you generated the summary.
                - Metadata, tool call syntax, or any text not part of the direct answer to the user.
            - Python code (or any other code) is only permissible if it is the direct answer or part of the answer to the `Task` and was an output in the `Execution`.

        Ensure your response is accurate, directly derived from the provided 'Execution/AI's Work', and meets all the user's needs as stated in their 'Task/User's request'.
        """).strip()
        
        final_agent = Agent(
            name = "Final Agent",
            description="Final Agent that Summarizes the stages and execution.",
            instruction=instructions,

            model_name = self.orchestra_model,
            provider=self.orchestra_provider,
            
            toolcall_enabled=False,
        )
        
        return Hive(final_agent).run(prompt).assistant_message
       
    def _get_plan(self, message):        
        json_schema = """
        {
            "type": "object",
            "properties": {
                "stage_1": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "Task to be performed by the agent."
                        },
                        "details": {
                            "type": "string",
                            "description": "In depth details of the task."
                        },
                        "expected_output": {
                            "type": "string",
                            "description": "Expected output of the task."
                        }
                    },
                    "required": ["task", "details", "expected_output"]
                }
            }
        }
        """
                
        instruction = dedent(f"""
        ## Your Role: Planning Agent
        - You are a meticulous Planning Agent. Your primary responsibility is to generate a sequential, multi-stage plan to accomplish a given user task.

        ## Available Agents:
        ```
        {"\n".join([f"{name}: {agent.description}" for name, agent in self.agents.items()])}
        ```

        ## Understanding Stages (`stage_n`):
        - `stage_n` refers to a specific step in the plan (e.g., stage_1, stage_2, stage_3, ... where 'n' is the stage number).
        - Each stage represents a distinct, actionable step towards completing the overall task.
        - The JSON object for each stage in the plan should clearly define its purpose, the assigned agent, and the specific instructions or inputs for that agent.

        ## Core Instructions for Plan Generation:

        1. Agent-Centric Planning:
            - You *must* analyze the `Available Agents` and their descriptions *before* formulating any plan.
            - Each stage in your plan *must* be assigned to one of the `Available Agents` best suited for that specific sub-task.

        2. Plan Detail Level:
            - Default Behavior: Provide a plan with a practical level of detail, ensuring each stage is clear and actionable.
            - User-Requested High Detail: If and only if the user explicitly asks for "a very detailed plan" (or similar phrasing indicating a desire for granularity), then break down tasks, including simple ones, into very specific, granular sub-steps. Otherwise, avoid unnecessary verbosity for straightforward operations.

        3. Contextual Continuity and Pronoun Resolution:
            - Dependency Management: If a stage's execution depends on information or outputs from a previous stage, explicitly state this dependency. Design the plan so that outputs from earlier stages are used as inputs for later stages where appropriate. Avoid re-calculating or re-fetching information already obtained.
            - Pronoun Disambiguation: Carefully dissect the user's task, especially pronouns (e.g., "it," "them," "that"). Resolve these pronouns based on the context of the request.
            - Context Integration: Ensure this resolved context is integrated into the instructions for each relevant stage. For example, if the user asks "What is X, and what do people think about it online?", stage 2 should search for "what do people think about X online", not just "what do people think about it online." (Refer to the example below).

        4. Plan Structure:
            - Generate as many stages as are logically necessary to complete the user's task.
            - Do *not* include a dedicated stage for summarizing the results. Summarization is handled by a separate, automated process after your plan is executed.

        Example for Continuity in Plan:
        ```
        If the user asks: "Research the Eiffel Tower, then find out what tourists commonly say about it on social media."

        A good plan would be:
        Stage 1: Agent_WebSearch to "Research general information about the Eiffel Tower (history, location, height)."
        Stage 2: Agent_SocialMediaSearch to "Search social media for tourist opinions on the Eiffel Tower", using the context "Eiffel Tower" from Stage 1.
        > Note: The agent names are placeholders. Use the actual agent names from the `Available Agents` list.
        ```

        JSON Output Requirements:

        1. Strictly JSON: Your entire response *must* be a single JSON object representing the plan.
        2. Code Block: Enclose the entire JSON object within a ```json code block.
        3. No Extra Text: Do not include *any* introductory phrases, explanations, apologies, or any text whatsoever outside the JSON code block. Your response must begin with ```json and end with ```.
        """).strip()
        
        prompt = f"Create a plan for this task: \n```\n{message}\n```\n"
        
        try:
            if not self.no_prints:
                with console.status("[bold blue]🎯 Generating execution plan...", spinner="dots"):
                    plan = self._run_json_agent(instruction, prompt, json_schema)
            else:
                plan = self._run_json_agent(instruction, prompt, json_schema)
                
            if not isinstance(plan, dict) or not plan:
                raise OrchestraException("Invalid or empty plan returned")
            return plan
        except Exception as e:
            logger.error(f"Error getting plan: {str(e)}")
            raise OrchestraException(f"Failed to generate plan: {str(e)}")
                    
    def _cleanse_agents(self):        
        sub_agent_prompt = dedent("""
        ## Your Sole Purpose:
        - {}

        ## Core Instructions:
        1. Execute Your Purpose: Your *only* objective is to fulfill the task defined while following the sole purpose. Your task will be provided by user.
        2. Maintain Strict Focus: Do not deviate from the task. Do not explore unrelated topics, engage in conversations, or generate any information or actions outside the direct scope of your assigned purpose.
        3. Factual Accuracy: Do not invent, fabricate, or hallucinate information. All outputs must be factual and directly derived from the task execution or provided tools.
        4. Resource Utilization: You may use your provided tools and other agents *only if* they are necessary to complete your Sole Purpose.
        5. Comprehensive Output: Upon completion, return a detailed and complete output of your task execution and results.
        6. Completion Without Code: If your task does not require generating Python code, it is considered complete once you provide the correct, detailed output that fully addresses your Sole Purpose.
        7. Warnings and Errors: If you encounter any errors or issues during execution, report them clearly and concisely. Do not attempt to fix them unless explicitly instructed to do so. If it's a warning, just ignore it and continue with the task.

        ## Operational Notes:
        - You are expected to execute the task defined by your "Sole Purpose" and then immediately provide the results.
        - Follow your purpose and do not do anything else even if you are asked to do or are capable of doing it.
        - If you are not able to do something, just say that you are not able to do it and do not try to do it.
        - Do not go beyond the task provided or asked of you.
        - Do your task and deliver without questioning unless needed to clarify the task. Otherwise assume the task is clear and do it. 
        """).strip()
        
        for agent in self.agents.values():
            agent.instruction = sub_agent_prompt.format(agent.instruction)
            agent.refresh_role()

        self.orchestrator.parameters = self.agents
        self.orchestrator.refresh_role()
                               
    def _refresh_orchestra(self):
        for agent in self.agents.values():
            agent.history.clear_history()
        
        self.orchestrator = self.orchestrator_backup
        self.orchestrator.history.clear_history()
        
    def _extract_stage_completion(self, text):
        match = re.search(r"<stage_complete>(.*?)</stage_complete>", text, re.DOTALL)
        if match:
            stage_text = match.group(1).strip()
            try:
                # Clean up the JSON string
                cleaned_text = re.sub(r'[\n\r\t]', '', stage_text)
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
                # Handle cases where single quotes might be used instead of double quotes
                cleaned_text = cleaned_text.replace("'", '"')
                
                try:
                    stage_status, _ = parse_json(cleaned_text)
                except json.JSONDecodeError as e:
                    logger.error(f"Initial JSON parsing failed: {e}")
                    # Try to fix common JSON formatting issues
                    if cleaned_text.startswith('{') and cleaned_text.endswith('}'):
                        # Add quotes around unquoted property names
                        cleaned_text = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1"\2":', cleaned_text)
                        try:
                            stage_status, _ = parse_json(cleaned_text)
                        except json.JSONDecodeError as e2:
                            logger.error(f"Failed to parse JSON even after cleanup: {e2}")
                            return None
                    else:
                        return None
                
                return stage_status
                
            except Exception as e:
                logger.error(f"Error processing stage_complete content: {e}")
                logger.error(f"Problematic text: {stage_text}")
                return None
        return None
                
    def add_task(self, task):
        if not self.no_prints:
            console.clear()
            self._print_panel(
                Text.assemble(
                    ("🎭 Orchestra Task Setup\n", "bold cyan"),
                    (f"Task: {task}\n\n", "white"),
                    ("Available Agents:\n", "bold yellow"),
                    *[Text(f"• {name}: {agent.description}\n", "green") for name, agent in self.agents.items()],
                ),
                title="🚀 Orchestra Initialization",
                style="cyan"
            )
        
        self._planning = True
        self._print("\n🎯 Generating execution plan...", "bold blue")
        
        self.orchestra_task = OrchestraTask(
            task = task, 
            plan = self._get_plan(task)
        )
        
        if not self.no_prints:
            self._print(f"✅ Plan generated with {len(self.orchestra_task.plan)} stages", "bold green")
            
            # Display the plan
            self._print("\n📋 Execution Plan:", "bold magenta")
            for i, (stage, details) in enumerate(self.orchestra_task.plan.items(), 1):
                self._print(f"\n  Stage {i}: {details.get('task', 'No task')}", "cyan")
                self._print(f"    Details: {details.get('details', 'No details')}", "dim")
                self._print(f"    Expected: {details.get('expected_output', 'No expected output')}", "dim")
        
        self._planning = False
     
    def activate(self):
        if not self.no_prints:
            self._print_panel(
                Text.assemble(
                    ("🎭 Starting Orchestra Execution\n", "bold green"),
                    (f"Task: {self.orchestra_task.task}\n", "white"),
                    (f"Stages: {len(self.orchestra_task.plan)}\n", "white"),
                    (f"Agents Available: {len(self.agents)}", "white")
                ),
                title="🎵 Orchestra Activation",
                style="green"
            )
        
        try: 
            if not self.no_prints:
                self._print("\n🔧 Preparing agents and orchestrator...", "blue")
            
            self._cleanse_agents()
        
            self.orchestrator_model = Hive(self.orchestrator)
            self.orchestrator_model.python_processor.add_agents(self.agents)
            
            self._refresh_orchestra()
            
            self._orchestra_running = True

            # Initialize progress tracking
            total_stages = len(self.orchestra_task.plan)
            self._init_progress(total_stages)
            
            if not self.no_prints:
                self.progress.start()
                self._print("\n🎶 Executing orchestra stages...", "bold blue")

            all_outputs = ""

            for i, stage in enumerate(self.orchestra_task.plan.keys(), 1): 

                # Update the current Stage          
                self.orchestra_task.update_current_stage(stage)
                current_task = self.orchestra_task.current_task.get('task')
                
                # Console output for current stage
                if not self.no_prints:
                    stage_title = f"Stage {i}/{total_stages}"
                    self._print(f"\n🎯 {stage_title}: {current_task}", "bold cyan")
                    self.progress.update(self.task_id, description=f"🎯 {stage_title}: {current_task[:50]}{'...' if len(current_task) > 50 else ''}")
                
                # Stage Prompt
                stage_prompt = dedent(f"""
                Complete it and return a detailed output. Use the provided tools and agents to complete the task.
                Task:
                ```
                {current_task}
                ```
                
                Details:
                ```
                {self.orchestra_task.current_task.get('details')}
                ```
                
                Expected Output:
                ```
                {self.orchestra_task.current_task.get('expected_output')}
                ```

                Available Agents:
                ```
                {"\n".join([f"{name}: {agent.description}" for name, agent in self.agents.items()])}
                ```

                - Strictly follow all the instructions and notes that I gave you. 
                - Do not make up any information.
                - Make the correct toolcalls, use only the avaialble agents, avaialble functions and suitable parameters that I have already given you in the prompt.
                - Reply as if it's first person, as if you are a person running the agents and tools    
                - Do not assume the output of any code that you give, run it first and then give/continue with the actual code output.        
                """).strip()
                
                # ---------------------------------------------------------------------------------
                # [Part of: Update the orchestrator instruction the stages and their outputs]
                # Remove previous all_outputs if present
                
                if "All Stages till now:" in self.orchestrator.instruction:
                    self.orchestrator.instruction = re.sub(r"All Stages till now:", "", self.orchestrator.instruction)
                
                while "```all_outputs" in self.orchestrator.instruction:
                    start = self.orchestrator.instruction.find("```all_outputs")
                    end = self.orchestrator.instruction.find("```", start+1)
                    self.orchestrator.instruction = self.orchestrator.instruction[:start] + self.orchestrator.instruction[end+3:]

                # Append the new all_outputs to the orchestrator instruction
                self.orchestrator.instruction = dedent(f"""
                {self.orchestrator.instruction}

                All Stages till now:
                ```all_outputs
                {all_outputs}
                ```
                """).strip()

                # Refresh the orchestrator role
                self.orchestrator.refresh_role()
                # ---------------------------------------------------------------------------------

                # Run the orchestrator model
                if not self.no_prints:
                    self._print(f"  🔄 Executing stage...", "yellow")
                
                output = self.orchestrator_model.run(stage_prompt)
                
                logger.debug("=" * 50)
                logger.debug(f"Stage: {stage}")
                logger.debug(f"Output: {output.assistant_message}")
                logger.debug("=" * 50)
                
                # Append to plan of that stage
                self.orchestra_task.plan[stage]["output"] = output.assistant_message
                self.orchestra_task.plan[stage]["status"] = "completed"
                
                if not self.no_prints:
                    output_length = len(output.assistant_message) if output.assistant_message else 0
                    self._print(f"  ✅ Stage completed ({output_length} chars)", "bold green")
                                
                # ---------------------------------------------------------------------------------
                # [Part of: Update the orchestrator instruction the stages and their outputs]
                # Append the output to the stage_output
                all_outputs += dedent(f"""
                {"Stage: " + stage}
                {"Output: " + self.orchestra_task.plan[stage]["output"] if self.orchestra_task.plan[stage]["output"] else "No output yet."}
                {"-"*50}
                \n
                """).strip()
                # ---------------------------------------------------------------------------------
                
                # Update progress
                self._update_progress()
                
                # Refresh the orchestrator (remove history and refresh role)
                self._refresh_orchestra()
            
            if not self.no_prints:
                self.progress.stop()
                self._print("\n💾 All stages completed. Generating final summary...", "bold blue")
                
                with console.status("[bold green]🔄 Generating comprehensive final summary...", spinner="dots"):
                    self.task_summary = self._get_task_summary()
            else:
                self.task_summary = self._get_task_summary()
                        
        except Exception as e:
            logger.error(f"Error running orchestra: {str(e)}")
            if not self.no_prints:
                self._print(f"\n❌ Orchestra error: {e}", "bold red")
                if self.progress:
                    self.progress.stop()
        finally:
            self._orchestra_running = False
            
        if not self.no_prints:
            self._print_panel(
                Text.assemble(
                    ("✅ Orchestra Execution Complete!\n\n", "bold green"),
                    (f"📋 Stages Completed: {len(self.orchestra_task.plan)}\n", "white"),
                    (f"🤖 Agents Used: {len(self.agents)}\n", "white"),
                    (f"📄 Summary Length: {len(self.task_summary)} characters\n", "white"),
                    ("\n🎉 Final results ready for review!", "bold cyan")
                ),
                title="🏁 Orchestra Summary",
                style="green"
            )
            
        return OrchestraOutput(
            orchestra_task=self.orchestra_task,
            task_summary=self.task_summary
        )