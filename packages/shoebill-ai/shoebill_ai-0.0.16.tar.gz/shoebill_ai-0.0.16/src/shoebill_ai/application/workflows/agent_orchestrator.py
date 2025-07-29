import uuid
from typing import Dict, List, Any, Callable, Optional, TypeVar
from datetime import datetime

from ...application.agents.embedding_service import EmbeddingService
from ...application.agents.multimodal_service import MultimodalService
from ...application.agents.text_service import TextService
from ...application.agents.vision_service import VisionService
from ...application.workflows.function_service import FunctionService
from ...application.workflows.workflow_service import WorkflowService
from ...application.workflows.workflow_queue_service import WorkflowQueueService
from ...domain.agents.base_agent import BaseAgent
from ...domain.agents.embedding_agent import EmbeddingAgent
from ...domain.agents.multimodal_agent import MultimodalAgent
from ...domain.agents.text_agent import TextAgent
from ...domain.agents.vision_agent import VisionAgent
from ...domain.workflows.workflow import Workflow
from ...domain.workflows.workflow_edge import WorkflowEdge
from ...domain.workflows.workflow_node import WorkflowNode, NodeType
from ...domain.workflows.workflow_schedule import WorkflowSchedule
from ...infrastructure.agents.in_memory_agent_registry import InMemoryAgentRegistry
from ...infrastructure.agents.in_memory_workflow_repository import InMemoryWorkflowRepository
from ...infrastructure.workflows.advanced_workflow_execution_engine import AdvancedWorkflowExecutionEngine
from ...infrastructure.workflows.in_memory_function_registry import InMemoryFunctionRegistry
from ...infrastructure.workflows.in_memory_workflow_schedule_repository import InMemoryWorkflowScheduleRepository
from ...infrastructure.workflows.workflow_scheduler import WorkflowScheduler

# Type variable for agent types
T = TypeVar('T', bound=BaseAgent)


class AgentOrchestrator:
    """
    Main entry point for the Agent Orchestration Framework.

    This class provides a simple API for creating and executing workflows with AI agents.
    """

    def __init__(self, api_url: str = None, api_token: str = None, 
                 text_service: TextService = None, 
                 embedding_service: EmbeddingService = None,
                 multimodal_service: MultimodalService = None,
                 vision_service: VisionService = None):
        """
        Initialize the Agent Orchestration Framework with default in-memory implementations.

        Args:
            api_url: Optional base URL for LLM services. If not provided, LLM services will not be initialized.
            api_token: Optional API token for LLM services.
            text_service: Optional pre-configured TextService instance.
            embedding_service: Optional pre-configured EmbeddingService instance.
            multimodal_service: Optional pre-configured MultimodalService instance.
            vision_service: Optional pre-configured VisionService instance.
        """
        # Create registries and repositories
        self.agent_registry = InMemoryAgentRegistry()
        self.function_registry = InMemoryFunctionRegistry()
        self.workflow_repository = InMemoryWorkflowRepository()

        # Create an execution engine
        self.execution_engine = AdvancedWorkflowExecutionEngine(
            agent_registry=self.agent_registry,
            function_registry=self.function_registry,
            workflow_repository=self.workflow_repository
        )

        # Store API URL and token
        self.api_url = api_url
        self.api_token = api_token

        # Store provided services
        self.text_service = text_service
        self.embedding_service = embedding_service
        self.multimodal_service = multimodal_service
        self.vision_service = vision_service

        # Create services
        self.function_service = FunctionService(self.function_registry)
        self.workflow_service = WorkflowService(
            workflow_repository=self.workflow_repository,
            execution_engine=self.execution_engine
        )
        self.workflow_queue_service = WorkflowQueueService(
            agent_registry=self.agent_registry,
            function_registry=self.function_registry,
            workflow_repository=self.workflow_repository
        )

        # Initialize workflow scheduling components
        self.schedule_repository = InMemoryWorkflowScheduleRepository()
        self.workflow_scheduler = WorkflowScheduler(
            schedule_repository=self.schedule_repository,
            workflow_repository=self.workflow_repository,
            execution_engine=self.execution_engine
        )

    # Agent Management

    def create_text_agent(self,
                         name: str,
                         description: str,
                         model_name: str,
                         system_prompt: Optional[str] = None,
                         tools: List[Dict[str, Any]] = None,
                         tags: List[str] = None,
                         config: Dict[str, Any] = None,
                         temperature: float = 0.6,
                         max_tokens: int = 2500) -> TextAgent:
        """
        Create a new TextAgent.

        Args:
            name: The name of the agent
            description: Description of the agent's purpose and capabilities
            model_name: The name of the model to use
            system_prompt: Optional system prompt to guide the agent's behavior
            tools: Optional list of tools the agent can use
            tags: Optional tags for categorizing the agent
            config: Optional configuration for the agent
            temperature: The temperature to use for generation
            max_tokens: The maximum number of tokens to generate

        Returns:
            The created TextAgent
        """
        if not self.api_url and not self.text_service:
            raise ValueError("Either API URL or a TextService must be provided to create a TextAgent")

        # Create a text service if one doesn't exist
        text_service = self.text_service
        if not text_service:
            text_service = TextService(
                api_url=self.api_url,
                api_token=self.api_token,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools
            )

        # Create the agent directly
        agent = TextAgent(
            agent_id=str(uuid.uuid4()),
            name=name,
            description=description,
            service=text_service,
            system_prompt=system_prompt,
            tools=tools or [],
            tags=tags or [],
            config=config or {}
        )

        # Register the agent
        self.agent_registry.register(agent)

        return agent

    def create_vision_agent(self,
                           name: str,
                           description: str,
                           model_name: str,
                           system_prompt: Optional[str] = None,
                           tags: List[str] = None,
                           config: Dict[str, Any] = None,
                           temperature: float = 0.6,
                           max_tokens: int = 2500) -> VisionAgent:
        """
        Create a new VisionAgent.

        Args:
            name: The name of the agent
            description: Description of the agent's purpose and capabilities
            model_name: The name of the model to use
            system_prompt: Optional system prompt to guide the agent's behavior
            tags: Optional tags for categorizing the agent
            config: Optional configuration for the agent
            temperature: The temperature to use for generation
            max_tokens: The maximum number of tokens to generate

        Returns:
            The created VisionAgent
        """
        if not self.api_url and not self.vision_service:
            raise ValueError("Either API URL or a VisionService must be provided to create a VisionAgent")

        # Create a vision service if one doesn't exist
        vision_service = self.vision_service
        if not vision_service:
            vision_service = VisionService(
                api_url=self.api_url,
                api_token=self.api_token,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )

        # Create the agent directly
        agent = VisionAgent(
            agent_id=str(uuid.uuid4()),
            name=name,
            description=description,
            service=vision_service,
            system_prompt=system_prompt,
            tools=[],  # Vision service doesn't support tools
            tags=tags or [],
            config=config or {}
        )

        # Register the agent
        self.agent_registry.register(agent)

        return agent

    def create_multimodal_agent(self,
                               name: str,
                               description: str,
                               model_name: str,
                               system_prompt: Optional[str] = None,
                               tools: List[Dict[str, Any]] = None,
                               tags: List[str] = None,
                               config: Dict[str, Any] = None,
                               temperature: float = 0.6,
                               max_tokens: int = 2500) -> MultimodalAgent:
        """
        Create a new MultimodalAgent.

        Args:
            name: The name of the agent
            description: Description of the agent's purpose and capabilities
            model_name: The name of the model to use
            system_prompt: Optional system prompt to guide the agent's behavior
            tools: Optional list of tools the agent can use
            tags: Optional tags for categorizing the agent
            config: Optional configuration for the agent
            temperature: The temperature to use for generation
            max_tokens: The maximum number of tokens to generate

        Returns:
            The created MultimodalAgent
        """
        if not self.api_url and not self.multimodal_service:
            raise ValueError("Either API URL or a MultimodalService must be provided to create a MultimodalAgent")

        # Create a multimodal service if one doesn't exist
        multimodal_service = self.multimodal_service
        if not multimodal_service:
            multimodal_service = MultimodalService(
                api_url=self.api_url,
                api_token=self.api_token,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools
            )

        # Create the agent directly
        agent = MultimodalAgent(
            agent_id=str(uuid.uuid4()),
            name=name,
            description=description,
            service=multimodal_service,
            system_prompt=system_prompt,
            tools=tools or [],
            tags=tags or [],
            config=config or {}
        )

        # Register the agent
        self.agent_registry.register(agent)

        return agent

    def create_embedding_agent(self,
                              name: str,
                              description: str,
                              model_name: str,
                              tags: List[str] = None,
                              config: Dict[str, Any] = None) -> EmbeddingAgent:
        """
        Create a new EmbeddingAgent.

        Args:
            name: The name of the agent
            description: Description of the agent's purpose and capabilities
            model_name: The name of the model to use
            tags: Optional tags for categorizing the agent
            config: Optional configuration for the agent

        Returns:
            The created EmbeddingAgent
        """
        if not self.api_url and not self.embedding_service:
            raise ValueError("Either API URL or an EmbeddingService must be provided to create an EmbeddingAgent")

        # Create an embedding service if one doesn't exist
        embedding_service = self.embedding_service
        if not embedding_service:
            embedding_service = EmbeddingService(
                api_url=self.api_url,
                api_token=self.api_token,
                model_name=model_name
            )

        # Create the agent directly
        agent = EmbeddingAgent(
            agent_id=str(uuid.uuid4()),
            name=name,
            description=description,
            service=embedding_service,
            system_prompt=None,  # Embedding service doesn't use system prompts
            tools=[],  # Embedding service doesn't use tools
            tags=tags or [],
            config=config or {}
        )

        # Register the agent
        self.agent_registry.register(agent)

        return agent

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent by its ID.

        This method can return any agent type that inherits from BaseAgent,
        including TextAgent, VisionAgent, MultimodalAgent, and EmbeddingAgent.

        Args:
            agent_id: The ID of the agent to retrieve

        Returns:
            The agent if found, None otherwise
        """
        # Get the agent from the registry
        return self.agent_registry.get(agent_id)

    def list_agents(self) -> List[BaseAgent]:
        """
        List all registered agents.

        This method returns all agent types that inherit from BaseAgent,
        including TextAgent, VisionAgent, MultimodalAgent, and EmbeddingAgent.

        Returns:
            A list of all registered agents
        """
        # Get agents from the registry
        return self.agent_registry.list_agents()

    def get_agents_by_tags(self, tags: List[str]) -> List[BaseAgent]:
        """
        Get agents by tags.

        This method returns all agent types that inherit from BaseAgent and match the tags,
        including TextAgent, VisionAgent, MultimodalAgent, and EmbeddingAgent.

        Args:
            tags: The tags to filter by

        Returns:
            A list of agents that have all the specified tags
        """
        # Get agents from the registry
        return self.agent_registry.get_by_tags(tags)

    # Function Management

    def register_function(self, 
                          function: Callable, 
                          function_id: str = None,
                          name: str = None, 
                          description: str = None,
                          input_schema: Dict[str, Any] = None,
                          output_schema: Dict[str, Any] = None,
                          tags: List[str] = None) -> str:
        """
        Register a function with the registry.

        Args:
            function: The function to register
            function_id: Optional unique identifier for the function (generated if not provided)
            name: Optional human-readable name for the function (uses function name if not provided)
            description: Optional description of the function's purpose
            input_schema: Optional JSON schema describing the function's input parameters
            output_schema: Optional JSON schema describing the function's output
            tags: Optional tags for categorizing the function

        Returns:
            The function ID
        """
        return self.function_service.register_function(
            function=function,
            function_id=function_id,
            name=name,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema,
            tags=tags
        )

    def get_function(self, function_id: str) -> Optional[Callable]:
        """
        Get a function by its ID.

        Args:
            function_id: The ID of the function to retrieve

        Returns:
            The function if found, None otherwise
        """
        return self.function_service.get_function(function_id)

    def list_functions(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered functions with their metadata.

        Returns:
            Dict mapping function IDs to their metadata
        """
        return self.function_service.list_functions()

    def execute_function(self, function_id: str, *args, **kwargs) -> Any:
        """
        Execute a function with the given arguments.

        Args:
            function_id: The ID of the function to execute
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The result of the function execution
        """
        return self.function_service.execute_function(function_id, *args, **kwargs)

    # Workflow Management

    def create_workflow(self, name: str, description: Optional[str] = None) -> Workflow:
        """
        Create a new workflow.

        Args:
            name: The name of the workflow
            description: Optional description of the workflow

        Returns:
            The created workflow
        """
        return self.workflow_service.create_workflow(name, description)

    def create_subworkflow(self, parent_workflow_id: str, name: str, description: Optional[str] = None) -> Workflow:
        """
        Create a new subworkflow linked to a parent workflow.

        Args:
            parent_workflow_id: The ID of the parent workflow
            name: The name of the subworkflow
            description: Optional description of the subworkflow

        Returns:
            The created subworkflow
        """
        return self.workflow_service.create_workflow(name, description, parent_workflow_id)

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow by its ID.

        Args:
            workflow_id: The ID of the workflow to retrieve

        Returns:
            The workflow if found, None otherwise
        """
        return self.workflow_service.get_workflow(workflow_id)

    def list_workflows(self) -> Dict[str, Dict[str, Any]]:
        """
        List all workflows.

        Returns:
            Dict mapping workflow IDs to workflow metadata
        """
        return self.workflow_service.list_workflows()

    def add_agent_node(self, 
                      workflow_id: str, 
                      name: str, 
                      agent_id: str,
                      description: Optional[str] = None,
                      config: Dict[str, Any] = None) -> Optional[WorkflowNode]:
        """
        Add an agent node to a workflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the node
            agent_id: The ID of the agent to use
            description: Optional description of the node
            config: Optional additional configuration for the node

        Returns:
            The created node if successful, None otherwise
        """
        node_config = config or {}
        node_config['agent_id'] = agent_id

        return self.workflow_service.add_node(
            workflow_id=workflow_id,
            name=name,
            node_type=NodeType.AGENT,
            config=node_config,
            description=description
        )

    def add_function_node(self, 
                         workflow_id: str, 
                         name: str, 
                         function_id: str,
                         description: Optional[str] = None,
                         config: Dict[str, Any] = None) -> Optional[WorkflowNode]:
        """
        Add a function node to a workflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the node
            function_id: The ID of the function to use
            description: Optional description of the node
            config: Optional additional configuration for the node

        Returns:
            The created node if successful, None otherwise
        """
        node_config = config or {}
        node_config['function_id'] = function_id

        return self.workflow_service.add_node(
            workflow_id=workflow_id,
            name=name,
            node_type=NodeType.FUNCTION,
            config=node_config,
            description=description
        )

    def add_input_node(self, 
                      workflow_id: str, 
                      name: str,
                      description: Optional[str] = None,
                      config: Dict[str, Any] = None) -> Optional[WorkflowNode]:
        """
        Add an input node to a workflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the node
            description: Optional description of the node
            config: Optional configuration for the node

        Returns:
            The created node if successful, None otherwise
        """
        return self.workflow_service.add_node(
            workflow_id=workflow_id,
            name=name,
            node_type=NodeType.INPUT,
            config=config,
            description=description
        )

    def add_output_node(self, 
                       workflow_id: str, 
                       name: str,
                       output_key: str = 'result',
                       description: Optional[str] = None,
                       config: Dict[str, Any] = None) -> Optional[WorkflowNode]:
        """
        Add an output node to a workflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the node
            output_key: The key to use for the output in the workflow results
            description: Optional description of the node
            config: Optional additional configuration for the node

        Returns:
            The created node if successful, None otherwise
        """
        node_config = config or {}
        node_config['output_key'] = output_key

        return self.workflow_service.add_node(
            workflow_id=workflow_id,
            name=name,
            node_type=NodeType.OUTPUT,
            config=node_config,
            description=description
        )

    def add_subworkflow_node(self,
                           workflow_id: str,
                           name: str,
                           subworkflow_id: str,
                           description: Optional[str] = None,
                           config: Dict[str, Any] = None) -> Optional[WorkflowNode]:
        """
        Add a subworkflow node to a workflow.

        Args:
            workflow_id: The ID of the parent workflow
            name: The name of the node
            subworkflow_id: The ID of the subworkflow to use
            description: Optional description of the node
            config: Optional additional configuration for the node

        Returns:
            The created node if successful, None otherwise
        """
        node_config = config or {}
        node_config['subworkflow_id'] = subworkflow_id

        return self.workflow_service.add_node(
            workflow_id=workflow_id,
            name=name,
            node_type=NodeType.SUBWORKFLOW,
            config=node_config,
            description=description
        )

    def add_edge(self, 
                workflow_id: str, 
                source_node_id: str, 
                target_node_id: str,
                source_output: Optional[str] = None,
                target_input: Optional[str] = None,
                condition: Optional[str] = None,
                transformation: Optional[str] = None) -> Optional[WorkflowEdge]:
        """
        Add an edge to a workflow.

        Args:
            workflow_id: The ID of the workflow
            source_node_id: The ID of the source node
            target_node_id: The ID of the target node
            source_output: Optional name of the output from the source node.
                           If not provided, a default will be determined based on the node type.
            target_input: Optional name of the input to the target node.
                          If not provided, a default will be determined based on the node type.
            condition: Optional condition for conditional edges
            transformation: Optional transformation function to apply

        Returns:
            The created edge if successful, None otherwise

        Note:
            When source_output or target_input is not provided, the system will automatically
            determine appropriate values based on the node types. For example:
            - TextAgent nodes expect "message" as input and produce "response" as output
            - VisionAgent nodes expect "image" as input and produce "response" as output
            - Input nodes produce "text" as output by default
            - Output nodes expect "result" as input by default
        """
        return self.workflow_service.add_edge(
            workflow_id=workflow_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            source_output=source_output,
            target_input=target_input,
            condition=condition,
            transformation=transformation
        )

    def execute_workflow(self, 
                        workflow_id: str, 
                        input_data: Dict[str, Any] = None,
                        max_iterations: int = 100) -> Dict[str, Any]:
        """
        Execute a workflow.

        Args:
            workflow_id: The ID of the workflow to execute
            input_data: Optional input data for the workflow
            max_iterations: Maximum number of iterations to prevent infinite loops

        Returns:
            The execution results
        """
        return self.workflow_service.execute_workflow(
            workflow_id=workflow_id,
            input_data=input_data,
            max_iterations=max_iterations
        )

    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a workflow execution.

        Args:
            execution_id: The ID of the execution

        Returns:
            The execution status, or None if not found
        """
        return self.workflow_service.get_execution_status(execution_id)

    def list_executions(self, workflow_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        List all executions, optionally filtered by workflow ID.

        Args:
            workflow_id: Optional workflow ID to filter by

        Returns:
            Dict mapping execution IDs to execution summaries
        """
        return self.workflow_service.list_executions(workflow_id)

    # Workflow Queue Processing

    def create_workflow_queue(self, 
                             workflow_id: str,
                             process_interval_seconds: float = 60.0,
                             refresh_interval_seconds: float = 300.0,
                             max_batch_size: int = 100) -> str:
        """
        Create a queue processor for batch processing of workflow executions.

        Args:
            workflow_id: The ID of the workflow to execute for each queue item
            process_interval_seconds: Time to wait between processing queue items (in seconds)
            refresh_interval_seconds: Time to wait before checking for new items when queue is empty (in seconds)
            max_batch_size: Maximum number of items to process in a batch

        Returns:
            The ID of the created queue processor
        """
        workflow = self.workflow_service.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow with ID '{workflow_id}' not found")

        return self.workflow_queue_service.create_queue_processor(
            workflow=workflow,
            process_interval_seconds=process_interval_seconds,
            refresh_interval_seconds=refresh_interval_seconds,
            max_batch_size=max_batch_size
        )

    def add_items_to_queue(self, processor_id: str, items: List[Dict[str, Any]]) -> None:
        """
        Add items to a workflow processing queue.

        Args:
            processor_id: The ID of the queue processor
            items: List of items to add to the queue
        """
        self.workflow_queue_service.add_items(processor_id, items)

    def set_queue_item_processor(self, 
                               processor_id: str, 
                               item_processor: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """
        Set a custom processor function for queue items before they're passed to the workflow.

        Args:
            processor_id: The ID of the queue processor
            item_processor: Function that takes a queue item and returns processed input data for the workflow
        """
        self.workflow_queue_service.set_item_processor(processor_id, item_processor)

    async def start_queue_processing(self, processor_id: str) -> None:
        """
        Start processing a workflow queue as a background task.

        Args:
            processor_id: The ID of the queue processor
        """
        await self.workflow_queue_service.start_processing(processor_id)

    def stop_queue_processing(self, processor_id: str) -> None:
        """
        Stop a workflow queue processor.

        Args:
            processor_id: The ID of the queue processor
        """
        self.workflow_queue_service.stop_processing(processor_id)

    def get_queue_results(self, processor_id: str) -> List[Dict[str, Any]]:
        """
        Get the results of processed queue items.

        Args:
            processor_id: The ID of the queue processor

        Returns:
            List of workflow execution results
        """
        return self.workflow_queue_service.get_results(processor_id)

    def is_queue_running(self, processor_id: str) -> bool:
        """
        Check if a queue processor is currently running.

        Args:
            processor_id: The ID of the queue processor

        Returns:
            True if the queue processor is running, False otherwise
        """
        return self.workflow_queue_service.is_running(processor_id)

    def get_queue_size(self, processor_id: str) -> int:
        """
        Get the current size of a workflow processing queue.

        Args:
            processor_id: The ID of the queue processor

        Returns:
            The number of items in the queue
        """
        return self.workflow_queue_service.get_queue_size(processor_id)

    def list_queue_processors(self) -> List[str]:
        """
        List all workflow queue processors.

        Returns:
            List of queue processor IDs
        """
        return self.workflow_queue_service.list_processors()

    # Workflow Scheduling

    def create_workflow_schedule(self,
                               workflow_id: str,
                               cron_expression: str,
                               input_data: Optional[Dict[str, Any]] = None,
                               name: Optional[str] = None,
                               description: Optional[str] = None,
                               timezone: str = "UTC",
                               enabled: bool = True,
                               max_iterations: int = 100) -> WorkflowSchedule:
        """
        Create a new schedule for a workflow.

        Args:
            workflow_id: ID of the workflow to execute
            cron_expression: Cron expression defining the schedule
            input_data: Optional input data for the workflow execution
            name: Optional name for the schedule
            description: Optional description of the schedule
            timezone: Timezone for the cron expression
            enabled: Whether the schedule is enabled
            max_iterations: Maximum number of iterations for workflow execution

        Returns:
            The created schedule
        """
        return self.workflow_scheduler.create_schedule(
            workflow_id=workflow_id,
            cron_expression=cron_expression,
            input_data=input_data,
            name=name,
            description=description,
            timezone=timezone,
            enabled=enabled,
            max_iterations=max_iterations
        )

    def get_workflow_schedule(self, schedule_id: str) -> Optional[WorkflowSchedule]:
        """
        Get a workflow schedule by ID.

        Args:
            schedule_id: The ID of the schedule to retrieve

        Returns:
            The schedule if found, None otherwise
        """
        return self.workflow_scheduler.get_schedule(schedule_id)

    def update_workflow_schedule(self, schedule: WorkflowSchedule) -> None:
        """
        Update a workflow schedule.

        Args:
            schedule: The schedule to update
        """
        self.workflow_scheduler.update_schedule(schedule)

    def delete_workflow_schedule(self, schedule_id: str) -> bool:
        """
        Delete a workflow schedule.

        Args:
            schedule_id: The ID of the schedule to delete

        Returns:
            True if the schedule was deleted, False otherwise
        """
        return self.workflow_scheduler.delete_schedule(schedule_id)

    def list_workflow_schedules(self, workflow_id: Optional[str] = None) -> Dict[str, WorkflowSchedule]:
        """
        List all workflow schedules, optionally filtered by workflow ID.

        Args:
            workflow_id: Optional workflow ID to filter by

        Returns:
            Dict mapping schedule IDs to schedules
        """
        return self.workflow_scheduler.list_schedules(workflow_id)

    def get_next_schedule_run_time(self, schedule_id: str) -> Optional[datetime]:
        """
        Get the next run time for a schedule.

        Args:
            schedule_id: The ID of the schedule

        Returns:
            The next run time, or None if the schedule doesn't exist or is disabled
        """
        return self.workflow_scheduler.get_next_run_time(schedule_id)

    def get_next_n_schedule_run_times(self, schedule_id: str, n: int) -> List[datetime]:
        """
        Get the next n run times for a schedule.

        Args:
            schedule_id: The ID of the schedule
            n: Number of run times to get

        Returns:
            List of the next n run times
        """
        return self.workflow_scheduler.get_next_n_run_times(schedule_id, n)

    async def start_scheduler(self) -> None:
        """
        Start the workflow scheduler.
        """
        await self.workflow_scheduler.start()

    def stop_scheduler(self) -> None:
        """
        Stop the workflow scheduler.
        """
        self.workflow_scheduler.stop()

    # Advanced Node Types

    def add_conditional_node(self,
                           workflow_id: str,
                           name: str,
                           condition: str,
                           description: Optional[str] = None,
                           config: Dict[str, Any] = None) -> Optional[WorkflowNode]:
        """
        Add a conditional node to a workflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the node
            condition: The condition to evaluate
            description: Optional description of the node
            config: Optional additional configuration for the node

        Returns:
            The created node if successful, None otherwise
        """
        node_config = config or {}
        node_config['condition'] = condition

        return self.workflow_service.add_node(
            workflow_id=workflow_id,
            name=name,
            node_type=NodeType.CONDITIONAL,
            config=node_config,
            description=description
        )

    def add_loop_node(self,
                    workflow_id: str,
                    name: str,
                    loop_type: str,
                    body_nodes: List[str],
                    condition: Optional[str] = None,
                    collection_key: Optional[str] = None,
                    item_key: Optional[str] = 'item',
                    max_iterations: int = 100,
                    description: Optional[str] = None,
                    config: Dict[str, Any] = None) -> Optional[WorkflowNode]:
        """
        Add a loop node to a workflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the node
            loop_type: The type of loop ('while', 'do_while', or 'for')
            body_nodes: List of node IDs that form the loop body
            condition: The condition to evaluate (for 'while' and 'do_while' loops)
            collection_key: The key of the collection to iterate over (for 'for' loops)
            item_key: The key to use for the current item in each iteration (for 'for' loops)
            max_iterations: Maximum number of iterations to prevent infinite loops
            description: Optional description of the node
            config: Optional additional configuration for the node

        Returns:
            The created node if successful, None otherwise
        """
        node_config = config or {}
        node_config['loop_type'] = loop_type
        node_config['body_nodes'] = body_nodes
        node_config['max_iterations'] = max_iterations

        if loop_type in ('while', 'do_while'):
            if not condition:
                raise ValueError(f"Condition is required for {loop_type} loops")
            node_config['condition'] = condition
        elif loop_type == 'for':
            if not collection_key:
                raise ValueError("Collection key is required for 'for' loops")
            node_config['collection_key'] = collection_key
            node_config['item_key'] = item_key
        else:
            raise ValueError(f"Unsupported loop type: {loop_type}")

        return self.workflow_service.add_node(
            workflow_id=workflow_id,
            name=name,
            node_type=NodeType.LOOP,
            config=node_config,
            description=description
        )

    def add_parallel_node(self,
                        workflow_id: str,
                        name: str,
                        branches: Dict[str, List[str]],
                        description: Optional[str] = None,
                        config: Dict[str, Any] = None) -> Optional[WorkflowNode]:
        """
        Add a parallel node to a workflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the node
            branches: Dictionary mapping branch IDs to lists of node IDs
            description: Optional description of the node
            config: Optional additional configuration for the node

        Returns:
            The created node if successful, None otherwise
        """
        node_config = config or {}
        node_config['branches'] = branches

        return self.workflow_service.add_node(
            workflow_id=workflow_id,
            name=name,
            node_type=NodeType.PARALLEL,
            config=node_config,
            description=description
        )

    def add_foreach_node(self,
                       workflow_id: str,
                       name: str,
                       collection_key: str,
                       body_nodes: List[str],
                       item_key: str = 'item',
                       parallel: bool = False,
                       description: Optional[str] = None,
                       config: Dict[str, Any] = None) -> Optional[WorkflowNode]:
        """
        Add a foreach node to a workflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the node
            collection_key: The key of the collection to iterate over
            body_nodes: List of node IDs that form the foreach body
            item_key: The key to use for the current item in each iteration
            parallel: Whether to execute iterations in parallel
            description: Optional description of the node
            config: Optional additional configuration for the node

        Returns:
            The created node if successful, None otherwise
        """
        node_config = config or {}
        node_config['collection_key'] = collection_key
        node_config['body_nodes'] = body_nodes
        node_config['item_key'] = item_key
        node_config['parallel'] = parallel

        return self.workflow_service.add_node(
            workflow_id=workflow_id,
            name=name,
            node_type=NodeType.FOREACH,
            config=node_config,
            description=description
        )

    def add_try_catch_node(self,
                         workflow_id: str,
                         name: str,
                         try_nodes: List[str],
                         catch_nodes: Optional[List[str]] = None,
                         finally_nodes: Optional[List[str]] = None,
                         description: Optional[str] = None,
                         config: Dict[str, Any] = None) -> Optional[WorkflowNode]:
        """
        Add a try-catch node to a workflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the node
            try_nodes: List of node IDs that form the try block
            catch_nodes: Optional list of node IDs that form the catch block
            finally_nodes: Optional list of node IDs that form the finally block
            description: Optional description of the node
            config: Optional additional configuration for the node

        Returns:
            The created node if successful, None otherwise
        """
        node_config = config or {}
        node_config['try_nodes'] = try_nodes

        if catch_nodes:
            node_config['catch_nodes'] = catch_nodes

        if finally_nodes:
            node_config['finally_nodes'] = finally_nodes

        return self.workflow_service.add_node(
            workflow_id=workflow_id,
            name=name,
            node_type=NodeType.TRY_CATCH,
            config=node_config,
            description=description
        )

    def add_set_variable_node(self,
                            workflow_id: str,
                            name: str,
                            variable_name: str,
                            value_source: str = 'input',
                            value_key: Optional[str] = 'value',
                            expression: Optional[str] = None,
                            description: Optional[str] = None,
                            config: Dict[str, Any] = None) -> Optional[WorkflowNode]:
        """
        Add a set variable node to a workflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the node
            variable_name: The name of the variable to set
            value_source: The source of the value ('input' or 'expression')
            value_key: The key in the input data to get the value from (for 'input' source)
            expression: The expression to evaluate to get the value (for 'expression' source)
            description: Optional description of the node
            config: Optional additional configuration for the node

        Returns:
            The created node if successful, None otherwise
        """
        node_config = config or {}
        node_config['variable_name'] = variable_name
        node_config['value_source'] = value_source

        if value_source == 'input':
            node_config['value_key'] = value_key
        elif value_source == 'expression':
            if not expression:
                raise ValueError("Expression is required for 'expression' value source")
            node_config['expression'] = expression
        else:
            raise ValueError(f"Unsupported value source: {value_source}")

        return self.workflow_service.add_node(
            workflow_id=workflow_id,
            name=name,
            node_type=NodeType.SET_VARIABLE,
            config=node_config,
            description=description
        )

    def add_get_variable_node(self,
                            workflow_id: str,
                            name: str,
                            variable_name: str,
                            output_key: Optional[str] = None,
                            description: Optional[str] = None,
                            config: Dict[str, Any] = None) -> Optional[WorkflowNode]:
        """
        Add a get variable node to a workflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the node
            variable_name: The name of the variable to get
            output_key: The key to use for the variable in the output (defaults to variable_name)
            description: Optional description of the node
            config: Optional additional configuration for the node

        Returns:
            The created node if successful, None otherwise
        """
        node_config = config or {}
        node_config['variable_name'] = variable_name

        if output_key:
            node_config['output_key'] = output_key

        return self.workflow_service.add_node(
            workflow_id=workflow_id,
            name=name,
            node_type=NodeType.GET_VARIABLE,
            config=node_config,
            description=description
        )

    def add_filter_node(self,
                      workflow_id: str,
                      name: str,
                      collection_key: str,
                      filter_condition: str,
                      output_key: str = 'filtered_collection',
                      description: Optional[str] = None,
                      config: Dict[str, Any] = None) -> Optional[WorkflowNode]:
        """
        Add a filter node to a workflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the node
            collection_key: The key of the collection to filter
            filter_condition: The condition to evaluate for each item
            output_key: The key to use for the filtered collection in the output
            description: Optional description of the node
            config: Optional additional configuration for the node

        Returns:
            The created node if successful, None otherwise
        """
        node_config = config or {}
        node_config['collection_key'] = collection_key
        node_config['filter_condition'] = filter_condition
        node_config['output_key'] = output_key

        return self.workflow_service.add_node(
            workflow_id=workflow_id,
            name=name,
            node_type=NodeType.FILTER,
            config=node_config,
            description=description
        )

    def add_map_node(self,
                   workflow_id: str,
                   name: str,
                   collection_key: str,
                   mapping_expression: str,
                   output_key: str = 'mapped_collection',
                   description: Optional[str] = None,
                   config: Dict[str, Any] = None) -> Optional[WorkflowNode]:
        """
        Add a map node to a workflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the node
            collection_key: The key of the collection to map
            mapping_expression: The expression to evaluate for each item
            output_key: The key to use for the mapped collection in the output
            description: Optional description of the node
            config: Optional additional configuration for the node

        Returns:
            The created node if successful, None otherwise
        """
        node_config = config or {}
        node_config['collection_key'] = collection_key
        node_config['mapping_expression'] = mapping_expression
        node_config['output_key'] = output_key

        return self.workflow_service.add_node(
            workflow_id=workflow_id,
            name=name,
            node_type=NodeType.MAP,
            config=node_config,
            description=description
        )

    def add_webhook_node(self,
                       workflow_id: str,
                       name: str,
                       url: str,
                       method: str = 'POST',
                       headers: Optional[Dict[str, str]] = None,
                       data_key: str = 'data',
                       description: Optional[str] = None,
                       config: Dict[str, Any] = None) -> Optional[WorkflowNode]:
        """
        Add a webhook node to a workflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the node
            url: The URL to send the request to
            method: The HTTP method to use
            headers: Optional headers to include in the request
            data_key: The key in the input data to get the request data from
            description: Optional description of the node
            config: Optional additional configuration for the node

        Returns:
            The created node if successful, None otherwise
        """
        node_config = config or {}
        node_config['url'] = url
        node_config['method'] = method
        node_config['data_key'] = data_key

        if headers:
            node_config['headers'] = headers

        return self.workflow_service.add_node(
            workflow_id=workflow_id,
            name=name,
            node_type=NodeType.WEBHOOK,
            config=node_config,
            description=description
        )
