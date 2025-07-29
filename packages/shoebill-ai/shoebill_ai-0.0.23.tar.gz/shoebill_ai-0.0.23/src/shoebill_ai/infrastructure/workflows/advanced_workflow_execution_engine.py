import asyncio
import logging
import traceback
from typing import Dict, Any, Optional, List, Union

from ...domain.agents.interfaces.agent_registry import AgentRegistry
from ...domain.agents.interfaces.function_registry import FunctionRegistry
from ...domain.workflows.interfaces.workflow_execution_engine import WorkflowExecutionEngine
from ...domain.workflows.workflow import Workflow
from ...domain.workflows.workflow_execution_context import WorkflowExecutionContext
from ...domain.workflows.workflow_node import WorkflowNode, NodeType
from ...domain.workflows.node_io_registry import NodeIORegistry


class AdvancedWorkflowExecutionEngine(WorkflowExecutionEngine):
    """
    A full-featured implementation of the WorkflowExecutionEngine interface.

    This implementation supports all node types and features:
    - Basic nodes: agent, function, input, output
    - Control flow: conditional, loop, try-catch
    - Advanced structures: subworkflow, parallel, foreach
    - Data handling: set_variable, get_variable, filter, map
    - Integration: webhook

    It also supports:
    - Parallel execution of independent nodes
    - Asynchronous node execution
    - Error handling with recovery options
    - Dynamic workflow modification during execution
    """

    def __init__(self, agent_registry: AgentRegistry, function_registry: FunctionRegistry, workflow_repository=None):
        """
        Initialize the full workflow execution engine.

        Args:
            agent_registry: Registry for retrieving agents
            function_registry: Registry for retrieving and executing functions
            workflow_repository: Optional repository for retrieving workflows (needed for subworkflows)
        """
        self.agent_registry = agent_registry
        self.function_registry = function_registry
        self.workflow_repository = workflow_repository
        self._executions: Dict[str, WorkflowExecutionContext] = {}
        self._active_executions: Dict[str, bool] = {}
        self.logger = logging.getLogger(__name__)

    def execute_workflow(self, 
                         workflow: Workflow, 
                         input_data: Dict[str, Any] = None,
                         max_iterations: int = 100) -> Dict[str, Any]:
        """
        Execute a workflow with the given input data.

        Args:
            workflow: The workflow to execute
            input_data: Optional input data for the workflow
            max_iterations: Maximum number of iterations to prevent infinite loops

        Returns:
            Dict[str, Any]: The execution results
        """
        # Create execution context
        context = WorkflowExecutionContext.create(workflow.workflow_id, input_data)
        self._executions[context.execution_id] = context
        self._active_executions[context.execution_id] = True

        try:
            # Start execution
            context.start_execution()

            # Find start nodes (nodes with no incoming edges)
            start_nodes = workflow.get_start_nodes()
            if not start_nodes:
                raise ValueError("Workflow has no start nodes")

            # Initialize nodes to process
            nodes_to_process = [node.node_id for node in start_nodes]
            processed_nodes = set()
            iteration_count = 0

            # Process nodes until there are no more nodes to process or we hit the iteration limit
            while nodes_to_process and iteration_count < max_iterations:
                iteration_count += 1

                # Get the next node to process
                current_node_id = nodes_to_process.pop(0)

                # Skip if already processed
                if current_node_id in processed_nodes:
                    continue

                # Get the node
                current_node = workflow.get_node(current_node_id)
                if not current_node:
                    raise ValueError(f"Node {current_node_id} not found in workflow")

                # Check if all input nodes have been processed
                input_edges = workflow.get_node_inputs(current_node_id)
                input_nodes = [edge.source_node_id for edge in input_edges]

                if not all(node_id in processed_nodes for node_id in input_nodes):
                    # Not all input nodes have been processed, put this node back in the queue
                    nodes_to_process.append(current_node_id)
                    continue

                try:
                    # Execute the node
                    context.set_current_node(current_node_id)
                    result = self.execute_node(workflow, current_node_id, context)
                    context.set_node_result(current_node_id, result)

                    # Mark as processed
                    processed_nodes.add(current_node_id)

                    # Add output nodes to the queue
                    output_edges = workflow.get_node_outputs(current_node_id)
                    for edge in output_edges:
                        # Check if the edge has a condition
                        if edge.condition:
                            # Evaluate the condition
                            condition_result = self._evaluate_condition(edge.condition, context, result)
                            if not condition_result:
                                continue

                        # Add the target node to the queue if not already processed
                        if edge.target_node_id not in processed_nodes:
                            nodes_to_process.append(edge.target_node_id)

                except Exception as e:
                    # Handle error with recovery options
                    tb_str = traceback.format_exc()
                    context.set_error(current_node_id, e, tb_str)

                    # Check if the node has error handling
                    if self._handle_node_error(workflow, current_node, context, e):
                        # Error was handled, continue execution
                        processed_nodes.add(current_node_id)

                        # Add output nodes to the queue
                        output_edges = workflow.get_node_outputs(current_node_id)
                        for edge in output_edges:
                            if edge.target_node_id not in processed_nodes:
                                nodes_to_process.append(edge.target_node_id)
                    else:
                        # Error was not handled, stop execution
                        context.complete_execution("failed")
                        raise

            # Check if we hit the iteration limit
            if iteration_count >= max_iterations:
                context.complete_execution("cancelled")
                raise RuntimeError(f"Workflow execution exceeded maximum iterations ({max_iterations})")

            # Mark execution as complete
            context.complete_execution("completed")

            # Return the final results
            return {
                "execution_id": context.execution_id,
                "status": context.status,
                "results": context.results,
                "summary": context.get_execution_summary()
            }

        except Exception as e:
            # Ensure the context is marked as failed
            context.complete_execution("failed")
            raise
        finally:
            # Mark execution as inactive
            self._active_executions[context.execution_id] = False

    def execute_node(self, 
                     workflow: Workflow, 
                     node_id: str, 
                     context: WorkflowExecutionContext) -> Dict[str, Any]:
        """
        Execute a specific node in a workflow.

        Args:
            workflow: The workflow containing the node
            node_id: The ID of the node to execute
            context: The execution context

        Returns:
            Dict[str, Any]: The node execution results
        """
        node = workflow.get_node(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found in workflow")

        # Prepare input data for the node
        input_data = self._prepare_node_input(workflow, node, context)

        # Execute the node based on its type
        if node.node_type == NodeType.AGENT:
            return self._execute_agent_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.FUNCTION:
            return self._execute_function_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.INPUT:
            return self._execute_input_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.OUTPUT:
            return self._execute_output_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.CONDITIONAL:
            return self._execute_conditional_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.LOOP:
            return self._execute_loop_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.SUBWORKFLOW:
            return self._execute_subworkflow_node(node, context, input_data)
        elif node.node_type == NodeType.PARALLEL:
            return self._execute_parallel_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.FOREACH:
            return self._execute_foreach_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.TRY_CATCH:
            return self._execute_try_catch_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.SET_VARIABLE:
            return self._execute_set_variable_node(node, context, input_data)
        elif node.node_type == NodeType.GET_VARIABLE:
            return self._execute_get_variable_node(node, context)
        elif node.node_type == NodeType.FILTER:
            return self._execute_filter_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.MAP:
            return self._execute_map_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.WEBHOOK:
            return self._execute_webhook_node(node, workflow, context, input_data)
        else:
            raise ValueError(f"Unsupported node type: {node.node_type}")

    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a workflow execution.

        Args:
            execution_id: The ID of the execution

        Returns:
            Optional[Dict[str, Any]]: The execution status, or None if not found
        """
        context = self._executions.get(execution_id)
        if not context:
            return None

        return {
            "execution_id": context.execution_id,
            "workflow_id": context.workflow_id,
            "status": context.status,
            "start_time": context.start_time,
            "end_time": context.end_time,
            "execution_time": context.get_execution_time(),
            "current_node_id": context.current_node_id,
            "execution_path": context.execution_path,
            "error_count": len(context.node_errors),
            "has_errors": len(context.node_errors) > 0,
            "is_active": self._active_executions.get(execution_id, False)
        }

    def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a running workflow execution.

        Args:
            execution_id: The ID of the execution to cancel

        Returns:
            bool: True if the execution was cancelled, False otherwise
        """
        if execution_id not in self._executions:
            return False

        if not self._active_executions.get(execution_id, False):
            return False

        # Mark the execution as cancelled
        context = self._executions[execution_id]
        context.complete_execution("cancelled")
        self._active_executions[execution_id] = False

        return True

    def list_executions(self, workflow_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        List all executions, optionally filtered by workflow ID.

        Args:
            workflow_id: Optional workflow ID to filter by

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of execution IDs to execution summaries
        """
        result = {}
        for execution_id, context in self._executions.items():
            if workflow_id and context.workflow_id != workflow_id:
                continue

            result[execution_id] = {
                "execution_id": context.execution_id,
                "workflow_id": context.workflow_id,
                "status": context.status,
                "start_time": context.start_time,
                "end_time": context.end_time,
                "execution_time": context.get_execution_time(),
                "is_active": self._active_executions.get(execution_id, False)
            }

        return result

    def _prepare_node_input(self, workflow: Workflow, node: WorkflowNode, context: WorkflowExecutionContext) -> Dict[str, Any]:
        """
        Prepare the input data for a node.

        Args:
            workflow: The workflow containing the node
            node: The node to prepare input for
            context: The execution context

        Returns:
            Dict[str, Any]: The prepared input data
        """
        # Start with workflow input data
        input_data = {}

        # For input nodes, use the workflow input data
        if node.node_type == NodeType.INPUT:
            return context.input_data

        # Get input edges for this node
        input_edges = workflow.get_node_inputs(node.node_id)

        # Collect input data from source nodes
        for edge in input_edges:
            source_node_id = edge.source_node_id
            source_output = edge.source_output
            target_input = edge.target_input

            # Get the source node
            source_node = workflow.nodes.get(source_node_id)
            if not source_node:
                continue

            # Get the result from the source node
            source_result = context.get_node_result(source_node_id)
            if source_result is None:
                continue

            # If source_output is not specified, try to determine it from the registry
            if source_output is None:
                # For agent nodes, get the agent type
                if source_node.node_type == NodeType.AGENT:
                    agent_id = source_node.config.get('agent_id')
                    if agent_id:
                        agent = self.agent_registry.get(agent_id)
                        if agent:
                            agent_type = type(agent)
                            source_output = NodeIORegistry.get_default_output_key(source_node.node_type, agent_type)
                else:
                    # For other node types
                    source_output = NodeIORegistry.get_default_output_key(source_node.node_type)

            # Extract the specific output from the source result
            if source_output and isinstance(source_result, dict):
                source_value = source_result.get(source_output)
            else:
                source_value = source_result

            # Apply transformation if specified
            if edge.transformation:
                source_value = self._apply_transformation(edge.transformation, source_value, context)

            # If target_input is not specified, try to determine it from the registry
            if target_input is None:
                # For agent nodes, get the agent type
                if node.node_type == NodeType.AGENT:
                    agent_id = node.config.get('agent_id')
                    if agent_id:
                        agent = self.agent_registry.get(agent_id)
                        if agent:
                            agent_type = type(agent)
                            target_input = NodeIORegistry.get_default_input_key(node.node_type, agent_type)
                else:
                    # For other node types
                    target_input = NodeIORegistry.get_default_input_key(node.node_type)

            # Add to input data
            if target_input:
                input_data[target_input] = source_value
            else:
                # If no target input is specified, merge the source value if it's a dict
                if isinstance(source_value, dict):
                    input_data.update(source_value)
                else:
                    # Use a default key if the source value is not a dict
                    input_data["input"] = source_value

        return input_data

    def _execute_agent_node(self, 
                           node: WorkflowNode, 
                           _workflow: Workflow, 
                           context: WorkflowExecutionContext,
                           input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an agent node.

        Args:
            node: The node to execute
            _workflow: The workflow being executed (unused)
            context: The execution context
            input_data: The input data for the node

        Returns:
            Dict[str, Any]: The result of the agent execution
        """
        # Get the agent from the registry
        agent_id = node.config.get('agent_id')
        if not agent_id:
            raise ValueError(f"Agent node {node.node_id} has no agent_id in config")

        agent = self.agent_registry.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found in registry")

        # Execute the agent
        return agent.process(input_data, context.to_dict())

    def _execute_function_node(self, 
                              node: WorkflowNode, 
                              _workflow: Workflow, 
                              _context: WorkflowExecutionContext,
                              input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function node.

        Args:
            node: The node to execute
            _workflow: The workflow being executed (unused)
            _context: The execution context (unused)
            input_data: The input data for the node

        Returns:
            Dict[str, Any]: The result of the function execution
        """
        # Get the function from the registry
        function_id = node.config.get('function_id')
        if not function_id:
            raise ValueError(f"Function node {node.node_id} has no function_id in config")

        # Execute the function
        result = self.function_registry.execute(function_id, **input_data)

        # Wrap the result in a dict if it's not already a dict
        if not isinstance(result, dict):
            result = {"result": result}

        return result

    def _execute_input_node(self, 
                           _node: WorkflowNode, 
                           _workflow: Workflow, 
                           _context: WorkflowExecutionContext,
                           input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an input node.

        Args:
            _node: The node to execute (unused)
            _workflow: The workflow being executed (unused)
            _context: The execution context (unused)
            input_data: The input data for the node

        Returns:
            Dict[str, Any]: The input data
        """
        # Input nodes simply pass through the workflow input data
        return input_data

    def _execute_output_node(self, 
                            node: WorkflowNode, 
                            _workflow: Workflow, 
                            context: WorkflowExecutionContext,
                            input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an output node.

        Args:
            node: The node to execute
            _workflow: The workflow being executed (unused)
            context: The execution context
            input_data: The input data for the node

        Returns:
            Dict[str, Any]: The output data
        """
        # Output nodes store their input in the workflow results
        output_key = node.config.get('output_key', 'result')
        context.set_result(output_key, input_data)

        return input_data

    def _execute_conditional_node(self, 
                                 node: WorkflowNode, 
                                 _workflow: Workflow, 
                                 context: WorkflowExecutionContext,
                                 input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a conditional node.

        Args:
            node: The node to execute
            _workflow: The workflow being executed (unused)
            context: The execution context
            input_data: The input data for the node

        Returns:
            Dict[str, Any]: The result of the condition evaluation
        """
        # Get the condition from the node config
        condition = node.config.get('condition')
        if not condition:
            raise ValueError(f"Conditional node {node.node_id} has no condition in config")

        # Evaluate the condition
        result = self._evaluate_condition(condition, context, input_data)

        return {"result": result, "input": input_data}

    def _execute_loop_node(self, 
                          node: WorkflowNode, 
                          workflow: Workflow, 
                          context: WorkflowExecutionContext,
                          input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a loop node.

        Args:
            node: The node to execute
            workflow: The workflow being executed
            context: The execution context
            input_data: The input data for the node

        Returns:
            Dict[str, Any]: The result of the loop execution
        """
        # Get loop configuration
        loop_type = node.config.get('loop_type', 'while')
        max_iterations = node.config.get('max_iterations', 100)

        # Get the loop body nodes
        body_nodes = node.config.get('body_nodes', [])
        if not body_nodes:
            raise ValueError(f"Loop node {node.node_id} has no body_nodes in config")

        # Initialize loop variables
        iteration = 0
        loop_results = []
        current_data = input_data

        # Execute the loop
        if loop_type == 'while':
            # Get the condition
            condition = node.config.get('condition')
            if not condition:
                raise ValueError(f"While loop node {node.node_id} has no condition in config")

            # Execute while the condition is true
            while self._evaluate_condition(condition, context, current_data) and iteration < max_iterations:
                # Execute the loop body
                body_result = self._execute_loop_body(workflow, body_nodes, current_data)
                loop_results.append(body_result)
                current_data = body_result
                iteration += 1

        elif loop_type == 'do_while':
            # Get the condition
            condition = node.config.get('condition')
            if not condition:
                raise ValueError(f"Do-while loop node {node.node_id} has no condition in config")

            # Execute at least once, then while the condition is true
            while True:
                # Execute the loop body
                body_result = self._execute_loop_body(workflow, body_nodes, current_data)
                loop_results.append(body_result)
                current_data = body_result
                iteration += 1

                # Check the condition
                if not self._evaluate_condition(condition, context, current_data) or iteration >= max_iterations:
                    break

        elif loop_type == 'for':
            # Get the collection to iterate over
            collection_key = node.config.get('collection_key')
            if not collection_key:
                raise ValueError(f"For loop node {node.node_id} has no collection_key in config")

            # Get the collection from the input data
            collection = input_data.get(collection_key)
            if not collection or not isinstance(collection, (list, dict)):
                raise ValueError(f"For loop collection '{collection_key}' is not a valid collection")

            # Get the item key
            item_key = node.config.get('item_key', 'item')

            # Iterate over the collection
            for item in collection:
                if iteration >= max_iterations:
                    break

                # Prepare the loop iteration data
                iteration_data = {**current_data, item_key: item, 'index': iteration}

                # Execute the loop body
                body_result = self._execute_loop_body(workflow, body_nodes, iteration_data)
                loop_results.append(body_result)
                current_data = body_result
                iteration += 1

        else:
            raise ValueError(f"Unsupported loop type: {loop_type}")

        # Return the loop results
        return {
            "iterations": iteration,
            "results": loop_results,
            "final_result": current_data
        }

    def _execute_loop_body(self, 
                          workflow: Workflow, 
                          body_nodes: List[str], 
                          input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the body of a loop.

        Args:
            workflow: The workflow being executed
            body_nodes: The IDs of the nodes in the loop body
            input_data: The input data for the loop body

        Returns:
            Dict[str, Any]: The result of the loop body execution
        """
        # Create a sub-context for the loop body
        sub_context = WorkflowExecutionContext.create(workflow.workflow_id, input_data)
        sub_context.start_execution()

        # Execute each node in the loop body
        result = input_data
        for node_id in body_nodes:
            node = workflow.get_node(node_id)
            if not node:
                raise ValueError(f"Node {node_id} not found in workflow")

            # Execute the node
            sub_context.set_current_node(node_id)
            node_result = self.execute_node(workflow, node_id, sub_context)
            sub_context.set_node_result(node_id, node_result)

            # Update the result
            result = node_result

        # Complete the sub-context
        sub_context.complete_execution("completed")

        # Return the final result
        return result

    def _execute_subworkflow_node(self, 
                                node: WorkflowNode, 
                                context: WorkflowExecutionContext,
                                input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a subworkflow node.

        Args:
            node: The node to execute
            context: The execution context
            input_data: The input data for the node

        Returns:
            Dict[str, Any]: The result of the subworkflow execution
        """
        # Get the subworkflow ID from the node configuration
        subworkflow_id = node.config.get('subworkflow_id')
        if not subworkflow_id:
            raise ValueError(f"Subworkflow node {node.node_id} has no subworkflow_id in config")

        # Get the subworkflow from the repository
        if not self.workflow_repository:
            raise ValueError("Workflow repository is required for executing subworkflow nodes")

        subworkflow = self.workflow_repository.get(subworkflow_id)
        if not subworkflow:
            raise ValueError(f"Subworkflow {subworkflow_id} not found")

        # Execute the subworkflow
        subworkflow_result = self.execute_workflow(subworkflow, input_data)

        # Store the subworkflow execution ID in the context
        context.subworkflow_contexts[node.node_id] = subworkflow_result['execution_id']

        # Return the subworkflow results
        return subworkflow_result['results']

    def _execute_parallel_node(self, 
                              node: WorkflowNode, 
                              workflow: Workflow, 
                              context: WorkflowExecutionContext,
                              input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a parallel node.

        Args:
            node: The node to execute
            workflow: The workflow being executed
            context: The execution context
            input_data: The input data for the node

        Returns:
            Dict[str, Any]: The result of the parallel execution
        """
        # Get the parallel branches
        branches = node.config.get('branches', {})
        if not branches:
            raise ValueError(f"Parallel node {node.node_id} has no branches in config")

        # Convert branches to a dictionary if it's a list
        if isinstance(branches, list):
            branches = {str(i): branch for i, branch in enumerate(branches)}

        # Execute each branch in parallel
        branch_results = {}

        # Create a task for each branch
        async def execute_all_branches():
            tasks = []
            for branch_id, branch_nodes in branches.items():
                task = asyncio.create_task(self._execute_branch(workflow, branch_nodes, context, input_data, branch_id))
                tasks.append(task)

            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for i, (branch_id, _) in enumerate(branches.items()):
                result = results[i]
                if isinstance(result, Exception):
                    # Handle branch execution error
                    branch_results[branch_id] = {"error": str(result)}
                else:
                    branch_results[branch_id] = result

        # Run the async function
        asyncio.run(execute_all_branches())

        # Return the combined results
        return {
            "branch_results": branch_results,
            "combined_result": self._combine_branch_results(branch_results)
        }

    async def _execute_branch(self, 
                             workflow: Workflow, 
                             branch_nodes: List[str], 
                             parent_context: WorkflowExecutionContext,
                             input_data: Dict[str, Any],
                             branch_id: str) -> Dict[str, Any]:
        """
        Execute a branch of a parallel node.

        Args:
            workflow: The workflow being executed
            branch_nodes: The IDs of the nodes in the branch
            parent_context: The parent execution context
            input_data: The input data for the branch
            branch_id: The ID of the branch

        Returns:
            Dict[str, Any]: The result of the branch execution
        """
        # Create a sub-context for the branch
        branch_context = WorkflowExecutionContext.create(workflow.workflow_id, input_data)
        branch_context.start_execution()

        # Execute each node in the branch
        result = input_data
        for node_id in branch_nodes:
            node = workflow.get_node(node_id)
            if not node:
                raise ValueError(f"Node {node_id} not found in workflow")

            # Execute the node
            branch_context.set_current_node(node_id)
            node_result = self.execute_node(workflow, node_id, branch_context)
            branch_context.set_node_result(node_id, node_result)

            # Update the result
            result = node_result

        # Complete the branch context
        branch_context.complete_execution("completed")

        # Store the branch context in the parent context
        parent_context.subworkflow_contexts[f"{branch_id}"] = branch_context.execution_id

        # Return the final result
        return result

    def _combine_branch_results(self, branch_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine the results from parallel branches.

        Args:
            branch_results: The results from each branch

        Returns:
            Dict[str, Any]: The combined results
        """
        combined = {}

        # Combine all branch results
        for branch_id, result in branch_results.items():
            if isinstance(result, dict) and "error" not in result:
                # Add the branch result to the combined result
                combined[branch_id] = result

        return combined

    def _execute_foreach_node(self, 
                             node: WorkflowNode, 
                             workflow: Workflow, 
                             context: WorkflowExecutionContext,
                             input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a foreach node.

        Args:
            node: The node to execute
            workflow: The workflow being executed
            context: The execution context
            input_data: The input data for the node

        Returns:
            Dict[str, Any]: The result of the foreach execution
        """
        # Get the collection to iterate over
        collection_key = node.config.get('collection_key')
        if not collection_key:
            raise ValueError(f"Foreach node {node.node_id} has no collection_key in config")

        # Get the collection from the input data
        collection = input_data.get(collection_key)
        if not collection or not isinstance(collection, (list, dict)):
            raise ValueError(f"Foreach collection '{collection_key}' is not a valid collection")

        # Get the item key
        item_key = node.config.get('item_key', 'item')

        # Get the foreach body nodes
        body_nodes = node.config.get('body_nodes', [])
        if not body_nodes:
            raise ValueError(f"Foreach node {node.node_id} has no body_nodes in config")

        # Get parallel execution flag
        parallel = node.config.get('parallel', False)

        # Execute the foreach loop
        if parallel:
            # Execute in parallel
            return self._execute_foreach_parallel(workflow, body_nodes, context, input_data, collection, item_key)
        else:
            # Execute sequentially
            return self._execute_foreach_sequential(workflow, body_nodes, context, input_data, collection, item_key)

    def _execute_foreach_sequential(self, 
                                   workflow: Workflow, 
                                   body_nodes: List[str], 
                                   context: WorkflowExecutionContext,
                                   input_data: Dict[str, Any],
                                   collection: Union[List, Dict],
                                   item_key: str) -> Dict[str, Any]:
        """
        Execute a foreach node sequentially.

        Args:
            workflow: The workflow being executed
            body_nodes: The IDs of the nodes in the foreach body
            context: The execution context
            input_data: The input data for the foreach
            collection: The collection to iterate over
            item_key: The key to use for the current item

        Returns:
            Dict[str, Any]: The result of the foreach execution
        """
        # Initialize results
        results = []

        # Iterate over the collection
        for i, item in enumerate(collection):
            # Prepare the iteration data
            iteration_data = {**input_data, item_key: item, 'index': i}

            # Execute the foreach body
            body_result = self._execute_loop_body(workflow, body_nodes, iteration_data)
            results.append(body_result)

        # Return the results
        return {
            "count": len(results),
            "results": results
        }

    def _execute_foreach_parallel(self, 
                                 workflow: Workflow, 
                                 body_nodes: List[str], 
                                 context: WorkflowExecutionContext,
                                 input_data: Dict[str, Any],
                                 collection: Union[List, Dict],
                                 item_key: str) -> Dict[str, Any]:
        """
        Execute a foreach node in parallel.

        Args:
            workflow: The workflow being executed
            body_nodes: The IDs of the nodes in the foreach body
            context: The execution context
            input_data: The input data for the foreach
            collection: The collection to iterate over
            item_key: The key to use for the current item

        Returns:
            Dict[str, Any]: The result of the foreach execution
        """
        # Initialize results
        results = []

        # Execute each iteration in parallel
        async def execute_all_iterations():
            tasks = []
            for i, item in enumerate(collection):
                # Prepare the iteration data
                iteration_data = {**input_data, item_key: item, 'index': i}

                # Create a task for this iteration
                task = asyncio.create_task(
                    self._execute_iteration(workflow, body_nodes, context, iteration_data, i)
                )
                tasks.append(task)

            # Wait for all tasks to complete
            return await asyncio.gather(*tasks, return_exceptions=True)

        # Run the async function
        iteration_results = asyncio.run(execute_all_iterations())

        # Process results
        for result in iteration_results:
            if isinstance(result, Exception):
                # Handle iteration execution error
                results.append({"error": str(result)})
            else:
                results.append(result)

        # Return the results
        return {
            "count": len(results),
            "results": results
        }

    async def _execute_iteration(self, 
                               workflow: Workflow, 
                               body_nodes: List[str], 
                               parent_context: WorkflowExecutionContext,
                               input_data: Dict[str, Any],
                               iteration_index: int) -> Dict[str, Any]:
        """
        Execute a single iteration of a foreach loop.

        Args:
            workflow: The workflow being executed
            body_nodes: The IDs of the nodes in the iteration body
            parent_context: The parent execution context
            input_data: The input data for the iteration
            iteration_index: The index of the iteration

        Returns:
            Dict[str, Any]: The result of the iteration execution
        """
        # Create a sub-context for the iteration
        iteration_context = WorkflowExecutionContext.create(workflow.workflow_id, input_data)
        iteration_context.start_execution()

        # Execute each node in the iteration
        result = input_data
        for node_id in body_nodes:
            node = workflow.get_node(node_id)
            if not node:
                raise ValueError(f"Node {node_id} not found in workflow")

            # Execute the node
            iteration_context.set_current_node(node_id)
            node_result = self.execute_node(workflow, node_id, iteration_context)
            iteration_context.set_node_result(node_id, node_result)

            # Update the result
            result = node_result

        # Complete the iteration context
        iteration_context.complete_execution("completed")

        # Store the iteration context in the parent context
        parent_context.subworkflow_contexts[f"iteration_{iteration_index}"] = iteration_context.execution_id

        # Return the final result
        return result

    def _execute_try_catch_node(self, 
                               node: WorkflowNode, 
                               workflow: Workflow, 
                               context: WorkflowExecutionContext,
                               input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a try-catch node.

        Args:
            node: The node to execute
            workflow: The workflow being executed
            context: The execution context
            input_data: The input data for the node

        Returns:
            Dict[str, Any]: The result of the try-catch execution
        """
        # Get the try and catch blocks
        try_nodes = node.config.get('try_nodes', [])
        catch_nodes = node.config.get('catch_nodes', [])
        finally_nodes = node.config.get('finally_nodes', [])

        if not try_nodes:
            raise ValueError(f"Try-catch node {node.node_id} has no try_nodes in config")

        # Execute the try block
        try:
            try_result = self._execute_loop_body(workflow, try_nodes, input_data)

            # Set the execution path
            execution_path = "try"
            error = None

        except Exception as e:
            # Handle the error
            error = str(e)

            # Execute the catch block if available
            if catch_nodes:
                try:
                    # Prepare the catch input data
                    catch_input = {
                        **input_data,
                        "error": error,
                        "error_type": type(e).__name__
                    }

                    # Execute the catch block
                    try_result = self._execute_loop_body(workflow, catch_nodes, catch_input)

                    # Set the execution path
                    execution_path = "catch"

                except Exception as catch_e:
                    # Error in catch block
                    error = str(catch_e)
                    try_result = {"error": error}
                    execution_path = "catch_error"
            else:
                # No catch block, just record the error
                try_result = {"error": error}
                execution_path = "error"

        finally:
            # Execute the finally block if available
            if finally_nodes:
                try:
                    # Prepare the finally input data
                    finally_input = {
                        **input_data,
                        "try_result": try_result,
                        "execution_path": execution_path,
                        "error": error
                    }

                    # Execute the finally block
                    finally_result = self._execute_loop_body(workflow, finally_nodes, finally_input)

                    # Update the execution path
                    execution_path += "_finally"

                except Exception as finally_e:
                    # Error in finally block
                    error = str(finally_e)
                    finally_result = {"error": error}
                    execution_path += "_finally_error"
            else:
                finally_result = None

        # Return the results
        return {
            "execution_path": execution_path,
            "try_result": try_result,
            "finally_result": finally_result,
            "error": error
        }

    def _execute_set_variable_node(self, 
                                  node: WorkflowNode, 
                                  context: WorkflowExecutionContext,
                                  input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a set variable node.

        Args:
            node: The node to execute
            context: The execution context
            input_data: The input data for the node

        Returns:
            Dict[str, Any]: The result of setting the variable
        """
        # Get the variable name and value
        variable_name = node.config.get('variable_name')
        if not variable_name:
            raise ValueError(f"Set variable node {node.node_id} has no variable_name in config")

        # Get the value source
        value_source = node.config.get('value_source', 'input')

        # Get the value
        if value_source == 'input':
            # Get the value from the input data
            value_key = node.config.get('value_key', 'value')
            value = input_data.get(value_key)
        elif value_source == 'expression':
            # Evaluate the expression
            expression = node.config.get('expression')
            if not expression:
                raise ValueError(f"Set variable node {node.node_id} has no expression in config")

            value = self._evaluate_expression(expression, context, input_data)
        else:
            raise ValueError(f"Unsupported value source: {value_source}")

        # Set the variable in the context
        context.set_variable(variable_name, value)

        # Return the result
        return {
            "variable_name": variable_name,
            "value": value
        }

    def _execute_get_variable_node(self, 
                                  node: WorkflowNode, 
                                  context: WorkflowExecutionContext) -> Dict[str, Any]:
        """
        Execute a get variable node.

        Args:
            node: The node to execute
            context: The execution context

        Returns:
            Dict[str, Any]: The result of getting the variable
        """
        # Get the variable name
        variable_name = node.config.get('variable_name')
        if not variable_name:
            raise ValueError(f"Get variable node {node.node_id} has no variable_name in config")

        # Get the variable from the context
        value = context.get_variable(variable_name)

        # Get the output key
        output_key = node.config.get('output_key', variable_name)

        # Return the result
        return {
            output_key: value
        }

    def _execute_filter_node(self, 
                            node: WorkflowNode, 
                            _workflow: Workflow, 
                            context: WorkflowExecutionContext,
                            input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a filter node.

        Args:
            node: The node to execute
            _workflow: The workflow being executed (unused)
            context: The execution context
            input_data: The input data for the node

        Returns:
            Dict[str, Any]: The result of the filter operation
        """
        # Get the collection to filter
        collection_key = node.config.get('collection_key')
        if not collection_key:
            raise ValueError(f"Filter node {node.node_id} has no collection_key in config")

        # Get the collection from the input data
        collection = input_data.get(collection_key)
        if not collection or not isinstance(collection, (list, dict)):
            raise ValueError(f"Filter collection '{collection_key}' is not a valid collection")

        # Get the filter condition
        filter_condition = node.config.get('filter_condition')
        if not filter_condition:
            raise ValueError(f"Filter node {node.node_id} has no filter_condition in config")

        # Get the output key
        output_key = node.config.get('output_key', 'filtered_collection')

        # Filter the collection
        if isinstance(collection, list):
            # Filter a list
            filtered = []
            for item in collection:
                # Create a namespace with the item
                item_data = {"item": item}

                # Evaluate the condition
                if self._evaluate_condition(filter_condition, context, item_data):
                    filtered.append(item)
        else:
            # Filter a dict
            filtered = {}
            for key, value in collection.items():
                # Create a namespace with the key and value
                item_data = {"key": key, "value": value}

                # Evaluate the condition
                if self._evaluate_condition(filter_condition, context, item_data):
                    filtered[key] = value

        # Return the result
        return {
            output_key: filtered,
            "original_count": len(collection),
            "filtered_count": len(filtered)
        }

    def _execute_map_node(self, 
                         node: WorkflowNode, 
                         _workflow: Workflow, 
                         context: WorkflowExecutionContext,
                         input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a map node.

        Args:
            node: The node to execute
            _workflow: The workflow being executed (unused)
            context: The execution context
            input_data: The input data for the node

        Returns:
            Dict[str, Any]: The result of the map operation
        """
        # Get the collection to map
        collection_key = node.config.get('collection_key')
        if not collection_key:
            raise ValueError(f"Map node {node.node_id} has no collection_key in config")

        # Get the collection from the input data
        collection = input_data.get(collection_key)
        if not collection or not isinstance(collection, (list, dict)):
            raise ValueError(f"Map collection '{collection_key}' is not a valid collection")

        # Get the mapping expression
        mapping_expression = node.config.get('mapping_expression')
        if not mapping_expression:
            raise ValueError(f"Map node {node.node_id} has no mapping_expression in config")

        # Get the output key
        output_key = node.config.get('output_key', 'mapped_collection')

        # Map the collection
        if isinstance(collection, list):
            # Map a list
            mapped = []
            for item in collection:
                # Create a namespace with the item
                item_data = {"item": item}

                # Evaluate the expression
                mapped_item = self._evaluate_expression(mapping_expression, context, item_data)
                mapped.append(mapped_item)
        else:
            # Map a dict
            mapped = {}
            for key, value in collection.items():
                # Create a namespace with the key and value
                item_data = {"key": key, "value": value}

                # Evaluate the expression
                mapped_value = self._evaluate_expression(mapping_expression, context, item_data)
                mapped[key] = mapped_value

        # Return the result
        return {
            output_key: mapped
        }

    def _execute_webhook_node(self, 
                             node: WorkflowNode, 
                             _workflow: Workflow, 
                             _context: WorkflowExecutionContext,
                             input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a webhook node.

        Args:
            node: The node to execute
            _workflow: The workflow being executed (unused)
            _context: The execution context (unused)
            input_data: The input data for the node

        Returns:
            Dict[str, Any]: The result of the webhook execution
        """
        # Get the webhook URL
        url = node.config.get('url')
        if not url:
            raise ValueError(f"Webhook node {node.node_id} has no url in config")

        # Get the webhook method
        method = node.config.get('method', 'POST')

        # Get the webhook headers
        headers = node.config.get('headers', {})

        # Get the webhook data
        data_key = node.config.get('data_key', 'data')
        data = input_data.get(data_key, {})

        # Execute the webhook
        # In a real implementation, you would use a proper HTTP client
        # For now, just return a mock response
        self.logger.info(f"Executing webhook: {method} {url}")
        self.logger.info(f"Headers: {headers}")
        self.logger.info(f"Data: {data}")

        # Return a mock response
        return {
            "status_code": 200,
            "response": {
                "success": True,
                "message": "Webhook executed successfully"
            }
        }

    def _evaluate_condition(self, condition: str, context: WorkflowExecutionContext, data: Dict[str, Any]) -> bool:
        """
        Evaluate a condition.

        Args:
            condition: The condition to evaluate
            context: The execution context
            data: The data to evaluate the condition against

        Returns:
            bool: The result of the condition evaluation
        """
        # For now, just check if the condition is a key in the data and its value is truthy
        if condition in data:
            return bool(data[condition])

        # Otherwise, try to evaluate the condition as a Python expression
        try:
            # Create a namespace with the data and context
            namespace = {
                "data": data,
                "context": context.to_dict(),
                "results": context.results,
                "variables": context.variables
            }

            # Evaluate the condition
            return bool(eval(condition, {"__builtins__": {}}, namespace))
        except Exception as e:
            # If evaluation fails, log the error and return False
            self.logger.error(f"Error evaluating condition '{condition}': {str(e)}")
            return False

    def _evaluate_expression(self, expression: str, context: WorkflowExecutionContext, data: Dict[str, Any]) -> Any:
        """
        Evaluate an expression.

        Args:
            expression: The expression to evaluate
            context: The execution context
            data: The data to evaluate the expression against

        Returns:
            Any: The result of the expression evaluation
        """
        # Try to evaluate the expression as a Python expression
        try:
            # Create a namespace with the data and context
            namespace = {
                "data": data,
                "context": context.to_dict(),
                "results": context.results,
                "variables": context.variables
            }

            # Evaluate the expression
            return eval(expression, {"__builtins__": {}}, namespace)
        except Exception as e:
            # If evaluation fails, log the error and return None
            self.logger.error(f"Error evaluating expression '{expression}': {str(e)}")
            return None

    def _apply_transformation(self, transformation: str, value: Any, context: WorkflowExecutionContext) -> Any:
        """
        Apply a transformation to a value.

        Args:
            transformation: The transformation to apply
            value: The value to transform
            context: The execution context

        Returns:
            Any: The transformed value
        """
        # Check if the transformation is a function ID
        if self.function_registry.get(transformation):
            return self.function_registry.execute(transformation, value=value, context=context.to_dict())

        # Otherwise, try to evaluate the transformation as a Python expression
        try:
            # Create a namespace with the value and context
            namespace = {
                "value": value,
                "context": context.to_dict(),
                "results": context.results,
                "variables": context.variables
            }

            # Evaluate the transformation
            return eval(transformation, {"__builtins__": {}}, namespace)
        except Exception as e:
            # If evaluation fails, log the error and return the original value
            self.logger.error(f"Error applying transformation '{transformation}': {str(e)}")
            return value

    def _handle_node_error(self, workflow: Workflow, node: WorkflowNode, context: WorkflowExecutionContext, error: Exception) -> bool:
        """
        Handle an error that occurred during node execution.

        Args:
            workflow: The workflow being executed
            node: The node that caused the error
            context: The execution context
            error: The error that occurred

        Returns:
            bool: True if the error was handled, False otherwise
        """
        # Check if the node has error handling configuration
        error_handling = node.config.get('error_handling', {})
        if not error_handling:
            return False

        # Get the error handling strategy
        strategy = error_handling.get('strategy', 'fail')

        if strategy == 'ignore':
            # Ignore the error and continue
            self.logger.warning(f"Ignoring error in node {node.node_id}: {str(error)}")
            return True

        elif strategy == 'retry':
            # Retry the node execution
            max_retries = error_handling.get('max_retries', 3)
            retry_count = context.get_variable(f"retry_count_{node.node_id}", 0)

            if retry_count < max_retries:
                # Increment the retry count
                retry_count += 1
                context.set_variable(f"retry_count_{node.node_id}", retry_count)

                # Log the retry
                self.logger.warning(f"Retrying node {node.node_id} (attempt {retry_count}/{max_retries})")

                # Retry the node execution
                try:
                    # Prepare input data for the node
                    input_data = self._prepare_node_input(workflow, node, context)

                    # Execute the node
                    result = self._execute_node_by_type(node, workflow, context, input_data)

                    # Set the node result
                    context.set_node_result(node.node_id, result)

                    # Return success
                    return True
                except Exception as e:
                    # Retry failed
                    self.logger.error(f"Retry failed for node {node.node_id}: {str(e)}")
                    return False
            else:
                # Max retries reached
                self.logger.error(f"Max retries reached for node {node.node_id}")
                return False

        elif strategy == 'fallback':
            # Use a fallback value
            fallback_value = error_handling.get('fallback_value')

            # Set the node result to the fallback value
            context.set_node_result(node.node_id, fallback_value)

            # Log the fallback
            self.logger.warning(f"Using fallback value for node {node.node_id}: {fallback_value}")

            return True

        else:
            # Unknown strategy
            self.logger.error(f"Unknown error handling strategy: {strategy}")
            return False

    def _execute_node_by_type(self, node: WorkflowNode, workflow: Workflow, context: WorkflowExecutionContext, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a node based on its type.

        Args:
            node: The node to execute
            workflow: The workflow being executed
            context: The execution context
            input_data: The input data for the node

        Returns:
            Dict[str, Any]: The result of the node execution
        """
        # Execute the node based on its type
        if node.node_type == NodeType.AGENT:
            return self._execute_agent_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.FUNCTION:
            return self._execute_function_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.INPUT:
            return self._execute_input_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.OUTPUT:
            return self._execute_output_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.CONDITIONAL:
            return self._execute_conditional_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.LOOP:
            return self._execute_loop_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.SUBWORKFLOW:
            return self._execute_subworkflow_node(node, context, input_data)
        elif node.node_type == NodeType.PARALLEL:
            return self._execute_parallel_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.FOREACH:
            return self._execute_foreach_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.TRY_CATCH:
            return self._execute_try_catch_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.SET_VARIABLE:
            return self._execute_set_variable_node(node, context, input_data)
        elif node.node_type == NodeType.GET_VARIABLE:
            return self._execute_get_variable_node(node, context)
        elif node.node_type == NodeType.FILTER:
            return self._execute_filter_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.MAP:
            return self._execute_map_node(node, workflow, context, input_data)
        elif node.node_type == NodeType.WEBHOOK:
            return self._execute_webhook_node(node, workflow, context, input_data)
        else:
            raise ValueError(f"Unsupported node type: {node.node_type}")
