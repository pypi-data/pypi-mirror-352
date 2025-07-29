# Shoebill AI - AI Agent Framework

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.0.63-green.svg)](https://pypi.org/project/shoebill-ai/)

Shoebill AI is a powerful framework for creating, orchestrating, and executing workflows with AI agents. It provides a flexible and extensible architecture for building complex AI applications by connecting multiple agents and functions together.

## 🚀 Features

- **Agent Management**: Create and manage different types of AI agents (text, vision, multimodal, embedding)
- **Workflow Orchestration**: Build complex workflows by connecting agents and functions
- **Function Integration**: Incorporate custom Python functions into your workflows
- **Conditional Logic**: Implement branching, loops, and other control flow patterns
- **Parallel Execution**: Run workflow branches in parallel for improved performance
- **Error Handling**: Use try-catch nodes to handle exceptions in workflows
- **Variable Management**: Set and get variables within workflows
- **Webhook Integration**: Connect workflows to external systems via webhooks
- **Workflow Scheduling**: Schedule workflows to run at specific times using cron syntax

## 📦 Installation

```bash
pip install shoebill_ai
```

## 🔧 Requirements

- Python 3.10 or higher
- Dependencies:
  - requests~=2.32.3
  - pillow~=11.2.1
  - ollama~=0.5.0
  - h_message_bus~=0.0.41

## 🏁 Quick Start

```python
from shoebill_ai.application.workflows.agent_orchestrator import AgentOrchestrator

# Initialize the orchestrator
orchestrator = AgentOrchestrator(
    api_url="YOUR_API_URL",
    api_token="YOUR_API_TOKEN"
)

# Create a text agent
text_agent = orchestrator.create_text_agent(
    name="Simple Assistant",
    description="A helpful assistant that answers user queries",
    model_name="gpt-4",
    system_prompt="You are a helpful assistant that provides concise and accurate information."
)

# Create a workflow
workflow = orchestrator.create_workflow(
    name="Simple Query Workflow",
    description="A workflow that processes user queries and returns responses"
)

# Add nodes to the workflow
input_node = orchestrator.add_input_node(
    workflow_id=workflow.id,
    name="User Query Input"
)

agent_node = orchestrator.add_agent_node(
    workflow_id=workflow.id,
    name="Text Assistant",
    agent_id=text_agent.id
)

output_node = orchestrator.add_output_node(
    workflow_id=workflow.id,
    name="Assistant Response",
    output_key="response"
)

# Connect the nodes with edges
orchestrator.add_edge(
    workflow_id=workflow.id,
    source_node_id=input_node.id,
    target_node_id=agent_node.id,
    source_output="text",
    target_input="message"
)

orchestrator.add_edge(
    workflow_id=workflow.id,
    source_node_id=agent_node.id,
    target_node_id=output_node.id,
    source_output="response",
    target_input="result"
)

# Execute the workflow
result = orchestrator.execute_workflow(
    workflow_id=workflow.id,
    input_data={"text": "What is machine learning?"}
)

print(result)
```

## 📚 Documentation

### Package Structure

The Shoebill AI package is organized into three main layers:

```
shoebill_ai/
├── application/     # Application layer - services and orchestration
├── domain/          # Domain layer - core business logic and entities
├── infrastructure/  # Infrastructure layer - external integrations and implementations
└── resources/       # Resources - configuration files and other assets
```

### Application Layer

The application layer contains services that coordinate the use of domain entities to perform specific tasks or workflows. This layer acts as a bridge between the domain layer and the external world.

#### Agent Services

The agent services provide high-level APIs for creating and interacting with different types of AI agents:

- **TextService**: Service for creating and interacting with text-based agents
- **VisionService**: Service for creating and interacting with vision-based agents
- **MultimodalService**: Service for creating and interacting with multimodal agents (text + vision)
- **EmbeddingService**: Service for creating and interacting with embedding agents

#### Workflow Services

The workflow services provide APIs for creating, managing, and executing workflows:

- **WorkflowService**: Service for creating and managing workflows
- **FunctionService**: Service for registering and executing functions within workflows
- **WorkflowQueueService**: Service for batch processing of workflows
- **WorkflowScheduler**: Service for scheduling workflow executions using cron syntax
- **AgentOrchestrator**: Main entry point that combines agent and workflow services

### Domain Layer

The domain layer contains the core business logic and entities of the framework. This includes the models, interfaces, and business rules that define what the system does, independent of how it's presented to the user or how it interacts with external systems.

#### Agent Models

The domain layer defines the core agent models that represent different types of AI agents:

- **BaseAgent**: Abstract base class for all agent types
- **TextAgent**: Agent that processes text inputs and produces text outputs
- **VisionAgent**: Agent that processes image inputs and produces text outputs
- **MultimodalAgent**: Agent that processes both text and image inputs
- **EmbeddingAgent**: Agent that generates vector embeddings from text

#### Workflow Models

The domain layer defines the core workflow models that represent workflows and their components:

- **Workflow**: Represents a complete workflow with nodes and edges
- **WorkflowNode**: Represents a node in a workflow (agent, function, input, output, etc.)
- **WorkflowEdge**: Represents a connection between nodes in a workflow

#### Messaging Models

The domain layer defines various message models for different types of communication:

- **Flow Messages**: Messages for controlling message flow
- **Graph Messages**: Messages related to graph operations
- **Telegram Messages**: Messages for Telegram integration
- **Twitter Messages**: Messages for Twitter integration
- **Vector Messages**: Messages for vector operations
- **Web Messages**: Messages for web integration

### Infrastructure Layer

The infrastructure layer provides concrete implementations of interfaces defined in the domain layer. This layer is responsible for technical concerns such as external system integrations, data persistence, and other implementation details.

#### Agent Implementations

The infrastructure layer provides concrete implementations of agent interfaces:

- **InMemoryAgentRegistry**: In-memory implementation of IAgentRegistry
- **OllamaAgentFactory**: Factory for creating agents that use Ollama models
- **OllamaTextAgent**: Implementation of TextAgent using Ollama
- **OllamaVisionAgent**: Implementation of VisionAgent using Ollama
- **OllamaMultimodalAgent**: Implementation of MultimodalAgent using Ollama
- **OllamaEmbeddingAgent**: Implementation of EmbeddingAgent using Ollama

#### Workflow Implementations

The infrastructure layer provides concrete implementations of workflow interfaces:

- **InMemoryWorkflowRepository**: In-memory implementation of IWorkflowRepository
- **InMemoryFunctionRegistry**: In-memory implementation of IFunctionRegistry
- **InMemoryWorkflowScheduleRepository**: In-memory implementation of IWorkflowScheduleRepository
- **AdvancedWorkflowExecutionEngine**: Implementation of IWorkflowExecutionEngine that supports advanced workflow features
- **WorkflowScheduler**: Service for scheduling workflow executions using cron syntax
- **CronParser**: Utility for parsing and validating cron expressions

### For LLM agents and AI assistants:

- [LLM Guide](llm.txt) - Comprehensive guide for LLM agents to use the Shoebill AI framework

## 🧪 Examples

The examples directory contains sample code demonstrating various features of the framework:

### 1. Basic Workflow (`basic_workflow.py`)

A simple workflow that demonstrates the fundamental concepts of the Agent Orchestrator:
- Creating a text agent
- Setting up a basic workflow with input, agent, and output nodes
- Connecting nodes with edges
- Executing the workflow
- Retrieving execution status

### 2. Multi-Agent Workflow (`multi_agent_workflow.py`)

A more complex workflow that demonstrates how to chain multiple agents together:
- Creating different types of agents (text, vision, multimodal)
- Connecting multiple agents in a workflow
- Passing data between agents
- Executing a multi-step workflow

### 3. Function Workflow (`function_workflow.py`)

A workflow that incorporates custom Python functions alongside AI agents:
- Registering custom Python functions with the orchestrator
- Adding function nodes to a workflow
- Connecting function nodes with agent nodes
- Passing data between functions and agents

### 4. Conditional Workflow (`conditional_workflow.py`)

A workflow that uses conditional edges to implement branching logic:
- Creating conditional edges in a workflow
- Implementing branching logic
- Using conditions to route data to different nodes
- Handling multiple possible execution paths

### 5. Loop Workflow (`loop_workflow.py`)

A workflow that demonstrates how to use Loop nodes for iterative logic:
- Creating different types of loops (while, do_while, for)
- Defining body nodes to execute in each iteration
- Implementing condition-based loops
- Iterating over collections with for loops
- Understanding how body nodes work in loops

### 6. Foreach Workflow (`foreach_workflow.py`)

A workflow that demonstrates how to use Foreach nodes for collection processing:
- Iterating over collections with foreach nodes
- Comparing sequential vs. parallel execution
- Understanding how body nodes work in foreach nodes
- Choosing between Loop and Foreach nodes
- Processing collections efficiently

### 7. Transformation Workflow (`transformation_workflow.py`)

A workflow that demonstrates how to use transformation edges to modify data between nodes:
- Using Python expressions as transformations
- Using custom functions as transformations
- Applying complex transformations to extract and format data
- Combining data with context variables
- Best practices for effective transformations

### 8. Scheduled Workflow (`scheduled_workflow.py`)

A workflow that demonstrates how to schedule recurring executions using cron syntax:
- Creating a workflow schedule with cron expressions
- Setting up a workflow to run on a recurring schedule
- Managing and monitoring scheduled workflows
- Updating and deleting schedules

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
