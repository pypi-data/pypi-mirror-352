import logging, time
from typing import Dict, List
from datetime import datetime
from textwrap import dedent
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text

from ...core.functionality.web_search import GoogleSearcher
from ...core.agent_architecture import Hive, Agent

console = Console()
logger = logging.getLogger("hive")

class DeepResearcher:
    def __init__(
            self, 
            model, 
            provider, 
            research_task: str, 
            max_depth: int = 2, 
            breadth: int = 3, 
            links_per_query: int = 10, 
            max_content_length: int = 1000,
            no_prints: bool = False,
        ):
            
        self.output = ""
        self.model = model
        self.provider = provider
        self.max_content_length = max_content_length
        self.google_searcher = GoogleSearcher()
        self.research_task = research_task
        self.all_queries = []
        self.max_depth = max_depth
        self.breadth = breadth
        self.total_queries = sum(breadth ** i * breadth for i in range(max_depth + 1))
        self.links_per_query = links_per_query
        self.total_links = self.links_per_query * self.total_queries
        self.processed_queries = 0
        self.processed_links = []
        self.done_queries = []
        self.retry_count = 3
        self.retry_delay = 2
        self.total_run = []
        self.no_prints = no_prints
        self.progress = None
        self.task_id = None
        self._init_agents()
    
    def __repr__(self):
        console.rule()
        console.print(f"[bold yellow]DeepResearcher Output:[/bold yellow]")
        md_results = Markdown(self.output)
        console.print(md_results)
        console.print("")  # for spacing
        console.rule()
        return  ""
    
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
    
    def _init_progress(self):
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
                "Starting research...", 
                total=self.total_queries
            )
    
    def _update_progress(self, description: str = None):
        """Update progress bar"""
        self.processed_queries += 1
        if not self.no_prints and self.progress and self.task_id is not None:
            if description:
                self.progress.update(self.task_id, description=description, advance=1)
            else:
                self.progress.update(self.task_id, advance=1)
    
    def run(self):
        # Initial setup display
        if not self.no_prints:
            console.clear()
            self._print_panel(
                Text.assemble(
                    ("🔍 Deep Research Task\n", "bold cyan"),
                    (f"{self.research_task}\n\n", "white"),
                    ("Configuration:\n", "bold yellow"),
                    (f"• Max Depth: {self.max_depth}\n", "green"),
                    (f"• Breadth: {self.breadth}\n", "green"),
                    (f"• Links per Query: {self.links_per_query}\n", "green"),
                    (f"• Expected Queries: {self.total_queries}\n", "green"),
                    (f"• Expected Links: {self.total_links}", "green")
                ),
                title="🚀 Research Initialization",
                style="cyan"
            )
        
        logger.info(f"Starting research task: {self.research_task}")
        logger.info(f"Configuration: depth={self.max_depth}, breadth={self.breadth}")
        logger.info(f"Expected total queries: {self.total_queries}")
        logger.info(f"Expected total links: {self.total_links}")
        
        # Initialize progress tracking
        self._init_progress()
        
        try:
            if not self.no_prints:
                self.progress.start()
                self.progress.update(self.task_id, description="🎯 Generating initial queries...")
            
            self._print("\n🎯 Generating initial research queries...", "bold blue")
            initial_queries = self._generate_queries()
            
            self._print(f"✅ Generated {len(initial_queries)} initial queries", "bold green")
            
            for i, query in enumerate(initial_queries, 1):
                if not self.no_prints:
                    self._print(f"\n📊 Processing query tree {i}/{len(initial_queries)}: '{query['query']}'", "bold cyan")
                    self.progress.update(self.task_id, description=f"🔍 Processing query tree {i}/{len(initial_queries)}")
                
                self._process_queries_recursively(query=query, current_depth=0)
                
        except KeyboardInterrupt:
            self._print("\n⚠️  Research interrupted by user. Saving results...", "bold yellow")
            logger.info("Research interrupted. Saving results...")
            
        except Exception as e:
            self._print(f"\n❌ Error occurred: {e}. Saving results...", "bold red")
            logger.exception(f"An error occurred during research: {e}. Saving results...")
        
        finally:
            if not self.no_prints and self.progress:
                self.progress.stop()
        
        self._print("\n💾 Research completed. Generating final report...", "bold blue")
        logger.info("Research completed. Saving results...")
        logger.info("Results saved successfully")
        logger.info("Finalizing results...")
        
        if not self.no_prints:
            with console.status("[bold green]🔄 Generating comprehensive final report...", spinner="dots"):
                self._finalize_results()
        else:
            self._finalize_results()
        
        logger.info("Research task completed successfully!")
        
        if not self.no_prints:
            self._print_panel(
                Text.assemble(
                    ("✅ Research Complete!\n\n", "bold green"),
                    (f"📋 Queries Processed: {self.processed_queries}\n", "white"),
                    (f"🔗 Links Analyzed: {len(self.processed_links)}\n", "white"),
                    (f"📄 Report Length: {len(self.output)} characters\n", "white"),
                    ("\n🎉 Final report ready for review!", "bold cyan")
                ),
                title="🏁 Research Summary",
                style="green"
            )
        
        return self.output
    
    def _init_agents(self):
        query_json_schema = """
        {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for."
                    },
                    "research_goal": {
                        "type": "string",
                        "description": "The goal of the research as detailed as possible."
                    }
                },
                "required": ["query", "research_goal"]
            }
        }
        """
        
        self.goals_agent = Agent(
            name="Goals Generator",
            instruction="You will be given a research task and you need to generate research goals based on the task. Make sure that the goals are detailed and relevant to the search. I will give you my previous research goals to avoid repetition. You need to generate new goals based on the research task provided. Return nothing but the goals. Make sure the goals are based on the details provided in the research task. Return nothing but the goals listed. Nothing else is needed. No python code is needed.",
            provider=self.provider,
            model_name=self.model,
            enable_history=False
        )

        self.query_agent = Agent(
            name="Query Generator",
            instruction="You are a research query generator that creates targeted search queries based on research goals. Make sure that no two questions are similar or matches any of the previous questions. You will be given a research goal and you need to generate a query based on the research goal. The queries will be searched on Google. Make the research goal as detailed as possible to generate a query that is relevant to the research goal. Vague queries are discouraged. Ultra-specific queries are encouraged when previous queries are provided. I have provided all the queries done till now so you avoid repetition.",
            json_mode=True,
            json_schema=query_json_schema,
            provider=self.provider,
            model_name=self.model,
            enable_history=False
        )
        
        self.summarizing_agent = Agent(
            name="Summarizer",
            instruction="You will be given a query, research goal and search results. Your task is to make a summary of the search results based on the research goal and query. Make sure to return detailed and relevant information. More detailed and longer responses are preferred. Use only the information provided in the prompt to generate the summary. Information packed summaries are encouraged.",
            provider=self.provider,
            model_name=self.model,
            enable_history=False,
        )
        
        self.final_agent = Agent(
            name="Final Summarizer",
            instruction="Given a task, queries and search results, generate a very detailed report based solely on the queries and search results. The report should be detailed and relevant to the research task. Make sure to provide detailed information based on the queries and search results. The report should be detailed and relevant to the research task. Use only the information provided in the prompt to generate the report.",
            provider=self.provider,
            model_name=self.model,
            max_output_length=60_000,
            max_context=120_000,
            enable_history=False,
        )
        
        self._check_context_and_output_length_compatibility()
    
    def _check_context_and_output_length_compatibility(self):
        test_agent = self.final_agent
        prev_max_context = test_agent.max_context
        prev_max_output_length = test_agent.max_output_length
        
        test_agent.max_context = 120_000
        test_agent.max_output_length = 60_000
        
        try:
            output = Hive(test_agent).run("This is a test to check you. Say 'Hello' if you are working correctly.")
            if isinstance(output, list):
                output = output[0] if output else ""
            else:
                output = output.assistant_message
                
            if "Output could not be generated due to an error" in output or not output:
                raise RuntimeError("Output could not be generated due to an error. Try using a provider that supports long context and output lengths like Google.")
        except Exception as e:
            raise RuntimeError("Output could not be generated due to an error. Try using a provider that supports long context and output lengths like Google.")
        
        finally:
            test_agent.max_context = prev_max_context
            test_agent.max_output_length = prev_max_output_length
            
    def _retry_operation(self, operation, *args, **kwargs):
        """Generic retry mechanism for operations"""
        last_exception = None
        for attempt in range(self.retry_count):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"Operation failed (attempt {attempt + 1}/{self.retry_count}): {str(e)}")
                if not self.no_prints:
                    self._print(f"⚠️  Retry {attempt + 1}/{self.retry_count} for operation", "yellow")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
        raise last_exception
    
    def _finalize_results(self):
        final_prompt = dedent(f"""
        Given the research task:
        ```
        {self.research_task}
        ```
        
        And the queries and search results from multiple sources:
        ```
        {self.total_run}
        ```
        
        Generate a very detailed report based solely on the queries and search results. The report should be detailed and relevant to the research task.
        Make sure to provide detailed information based on the queries and search results.
        The report should be detailed and relevant to the research task.
        Atleast 10 pages of detailed information is expected.
        
        """).strip()
        
        try:
            output = Hive(self.final_agent).run(final_prompt).assistant_message
            if "Output could not be generated due to an error" in output:
                raise RuntimeError("Output could not be generated due to an error. Try using a provider that supports long context and output lengths like Google.")
            self.output = output
            logger.info("Final report generated successfully")   
        except Exception as e:
            raise RuntimeError(f"Failed to generate final report: {str(e)}. Try using a provider that supports long context and output lengths like Google.")
    
    def _generate_queries(self, previous_query={}, num_results=None):
        num_results = num_results or self.breadth
        
        goals_prompt = dedent(f"""
        Given the research task:
        ```
        {self.research_task}
        ```
        
        Generate a research goal based on the research task. Make sure that the goal is detailed and relevant to the search. I will provide you with my previous research goals to avoid repetition. You need to generate new goals based on the research task provided.
        """).strip()
        
        query_prompt = dedent(f"""
        Given the research goal: 
        ```
        {self.research_task}
        ```
        
        Generate a query to search for relevant information and the research goal behind the query.
        Each query must be generated based on what you think the research goal is. The queries will be searched on Google.
        
        Number of queries to generate: 
        ```
        {num_results}
        ```
        
        """).strip()
                        
        if previous_query:
            prompt = dedent(f"""
                            
            Previous query:
            ```
            {previous_query}
            ```
            Now generate the next queries as needed with new research goals to explore more about the research task. Previous query is provided to help you generate new queries.
            
            """).strip()
            
            query_prompt += prompt
            goals_prompt += prompt
            
        if self.done_queries:
            prompt = dedent(f"""
                            
            All queries done till now:
            ```
            {"\n".join(" - " + q for q in self.done_queries)}
            ```
            
            """).strip()
            
            query_prompt += prompt
            goals_prompt += prompt
        
        goals = Hive(self.goals_agent).run(goals_prompt).assistant_message
        
        query_prompt += dedent(f"""
                               
        Research goals generated:
        ```
        {goals}
        ```
                       
        """).strip()
        
        logger.info(f"Generating {num_results} queries...")
        logger.info(f"Prompt: {query_prompt}")
        
        json = Hive(self.query_agent).run(query_prompt)
        if not isinstance(json, list):
            logger.info(f"is json? {self.query_agent.json_mode}")
        if len(json) > num_results:
            json = json[:num_results]
        logger.info(f"Queries generated: {json}")
        return json
    
    def _summarize_results(self, query, search_results):
        summary_prompt = dedent(f"""
        Given the research goal:
        ```
        {query["research_goal"]}
        ```
        And the query:
        ```
        {query["query"]}
        ```
        
        And the search results from multiple sources:
        ```
        {search_results}
        ```
        
        Summarize the search results based on the research goal and query. 
        Make sure to provide detailed and relevant information, considering all the different sources.
        """).strip()
        
        return Hive(self.summarizing_agent).run(summary_prompt).assistant_message
    
    def _combine_search_results(self, search_results: List[Dict], query: str) -> str:
        """
        Combine multiple search results into a single text with clear separation.
        """
        combined_text = ""
        for i, result in enumerate(search_results, 1):
            combined_text += f"\nSource {i}:\n"
            combined_text += f"URL: {result.get('url', 'N/A')}\n"
            combined_text += f"Content: {result.get('content', '').strip()[:self.max_content_length]}...\n"
            combined_text += "-" * 50
            self.processed_links.append(result.get('url', 'N/A'))
        return combined_text

    def _process_single_query(self, query: Dict, current_depth: int) -> Dict:
        """
        Process single query with retries
        """
        def _operation():
            query_id = f"q_{current_depth}_{datetime.now().strftime('%H%M%S%f')}"
            
            # Console output for current query
            if not self.no_prints:
                depth_indicator = "  " * current_depth + "└─" if current_depth > 0 else "🔍"
                self._print(f"{depth_indicator} Processing: '{query['query']}' (Depth: {current_depth})", "cyan")
                if self.progress and self.task_id is not None:
                    self.progress.update(
                        self.task_id, 
                        description=f"🔍 {query['query'][:50]}{'...' if len(query['query']) > 50 else ''}"
                    )
            
            logger.info(f"Processing query: {query['query']} (Depth: {current_depth}, ID: {query_id})")
            
            self.google_searcher.banned_links = self.processed_links
            search_results = self.google_searcher.search(query["query"], num_results=self.links_per_query)
            
            if not search_results:
                logger.warning(f"No results found for query: {query['query']}")
                if not self.no_prints:
                    depth_indicator = "  " * current_depth + "  " if current_depth > 0 else "  "
                    self._print(f"{depth_indicator}⚠️  No results found", "yellow")
                
                self.total_run.append({
                    "id": query_id,
                    "query": query["query"],
                    "research_goal": query["research_goal"],
                    "summary": "No Summary"
                })
                self._update_progress()
                return {
                    "id": query_id,
                    "query": query["query"],
                    "research_goal": query["research_goal"],
                    "summary": "No Summary"
                }
            
            if not self.no_prints:
                depth_indicator = "  " * current_depth + "  " if current_depth > 0 else "  "
                self._print(f"{depth_indicator}📄 Found {len(search_results)} results, summarizing...", "green")
            
            combined_search_results = self._combine_search_results(search_results, query["query"])
            self.done_queries.append(query["query"])
            summary = self._summarize_results(query, combined_search_results)
            
            if not self.no_prints:
                depth_indicator = "  " * current_depth + "  " if current_depth > 0 else "  "
                self._print(f"{depth_indicator}✅ Summary complete ({len(summary)} chars)", "bold green")
            
            self.total_run.append({
                "id": query_id,
                "query": query["query"],
                "research_goal": query["research_goal"],
                "summary": summary
            })
            
            self._update_progress()
            
            return {
                "id": query_id,
                "query": query["query"],
                "research_goal": query["research_goal"],
                "summary": summary
            }
        
        return self._retry_operation(_operation)

    def _process_queries_recursively(self, query: Dict, current_depth: int) -> Dict:
        processed_query = self._process_single_query(query, current_depth)        
         
        if current_depth < self.max_depth:
            if not self.no_prints:
                depth_indicator = "  " * current_depth + "├─" if current_depth > 0 else "🌱"
                self._print(f"{depth_indicator} Generating {self.breadth} child queries...", "blue")
            
            logger.info(f"Generating child queries for: {processed_query['id']}")
            child_queries = self._generate_queries(
                previous_query=processed_query,
                num_results=self.breadth
            )
            
            for i, child_query in enumerate(child_queries, 1):
                if not self.no_prints:
                    depth_indicator = "  " * current_depth + "  " if current_depth > 0 else "  "
                    self._print(f"{depth_indicator}🔄 Processing child query {i}/{len(child_queries)}", "magenta")
                
                self._process_queries_recursively(
                    child_query,
                    current_depth + 1
                )
        
        return processed_query