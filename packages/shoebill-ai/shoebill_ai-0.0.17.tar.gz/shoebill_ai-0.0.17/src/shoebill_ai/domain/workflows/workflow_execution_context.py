import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional


@dataclass
class WorkflowExecutionContext:
    """
    Represents the execution context for a workflow.

    This class tracks the state of a workflow execution, including the results of each node,
    the execution status, and any errors that occurred.

    Enhanced features:
    - Variables: Store and retrieve workflow variables
    - Subworkflows: Track execution of nested workflows
    - Execution hooks: Register callbacks for workflow lifecycle events
    - Retry tracking: Track retry attempts for nodes
    """
    execution_id: str
    workflow_id: str
    status: str = "pending"  # pending, running, completed, failed, cancelled
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    node_results: Dict[str, Any] = field(default_factory=dict)
    node_errors: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    execution_path: List[str] = field(default_factory=list)
    current_node_id: Optional[str] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Enhanced fields
    variables: Dict[str, Any] = field(default_factory=dict)
    subworkflow_contexts: Dict[str, str] = field(default_factory=dict)  # node_id -> execution_id
    execution_hooks: Dict[str, List[Any]] = field(default_factory=dict)  # event -> [callbacks]
    retry_counts: Dict[str, int] = field(default_factory=dict)  # node_id -> retry count

    @classmethod
    def create(cls, workflow_id: str, input_data: Dict[str, Any] = None) -> 'WorkflowExecutionContext':
        """
        Create a new execution context with a generated ID.

        Args:
            workflow_id: The ID of the workflow being executed
            input_data: Optional input data for the workflow

        Returns:
            WorkflowExecutionContext: The created execution context
        """
        return cls(
            execution_id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            input_data=input_data or {},
            start_time=time.time()
        )

    def start_execution(self) -> None:
        """
        Mark the execution as started.
        """
        self.status = "running"
        self.start_time = time.time()

    def complete_execution(self, status: str) -> None:
        """
        Mark the execution as completed with the given status.

        Args:
            status: The final status of the execution (completed, failed, cancelled)
        """
        self.status = status
        self.end_time = time.time()

    def set_current_node(self, node_id: str) -> None:
        """
        Set the current node being executed.

        Args:
            node_id: The ID of the current node
        """
        self.current_node_id = node_id
        self.execution_path.append(node_id)

    def set_node_result(self, node_id: str, result: Any) -> None:
        """
        Set the result for a node.

        Args:
            node_id: The ID of the node
            result: The result of the node execution
        """
        self.node_results[node_id] = result

    def get_node_result(self, node_id: str) -> Optional[Any]:
        """
        Get the result for a node.

        Args:
            node_id: The ID of the node

        Returns:
            The result of the node execution, or None if not available
        """
        return self.node_results.get(node_id)

    def set_error(self, node_id: str, error: Exception, traceback: str = None) -> None:
        """
        Set an error for a node.

        Args:
            node_id: The ID of the node
            error: The error that occurred
            traceback: Optional traceback information
        """
        self.node_errors[node_id] = {
            "error": str(error),
            "error_type": type(error).__name__,
            "traceback": traceback,
            "timestamp": time.time()
        }

    def has_error(self, node_id: str) -> bool:
        """
        Check if a node has an error.

        Args:
            node_id: The ID of the node

        Returns:
            True if the node has an error, False otherwise
        """
        return node_id in self.node_errors

    def get_error(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the error for a node.

        Args:
            node_id: The ID of the node

        Returns:
            The error information, or None if no error occurred
        """
        return self.node_errors.get(node_id)

    def set_result(self, key: str, value: Any) -> None:
        """
        Set a result value.

        Args:
            key: The result key
            value: The result value
        """
        self.results[key] = value

    def get_result(self, key: str) -> Optional[Any]:
        """
        Get a result value.

        Args:
            key: The result key

        Returns:
            The result value, or None if not available
        """
        return self.results.get(key)

    def set_variable(self, name: str, value: Any) -> None:
        """
        Set a variable in the workflow context.

        Args:
            name: The name of the variable
            value: The value to set
        """
        self.variables[name] = value

    def get_variable(self, name: str, default: Any = None) -> Any:
        """
        Get a variable from the workflow context.

        Args:
            name: The name of the variable
            default: The default value to return if the variable doesn't exist

        Returns:
            The variable value, or the default if not found
        """
        return self.variables.get(name, default)

    def get_execution_time(self) -> Optional[float]:
        """
        Get the execution time in seconds.

        Returns:
            The execution time in seconds, or None if the execution is not complete
        """
        if self.start_time is None:
            return None

        end_time = self.end_time or time.time()
        return end_time - self.start_time

    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the execution.

        Returns:
            Dict[str, Any]: Summary of the execution
        """
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "status": self.status,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            "execution_time": self.get_execution_time(),
            "nodes_executed": len(self.execution_path),
            "execution_path": self.execution_path,
            "error_count": len(self.node_errors),
            "has_errors": len(self.node_errors) > 0
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the execution context to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the execution context
        """
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "node_results": self.node_results,
            "node_errors": self.node_errors,
            "execution_path": self.execution_path,
            "current_node_id": self.current_node_id,
            "input_data": self.input_data,
            "results": self.results,
            "metadata": self.metadata,
            # Enhanced fields
            "variables": self.variables,
            "subworkflow_contexts": self.subworkflow_contexts,
            "retry_counts": self.retry_counts
            # Note: execution_hooks are not serialized as they contain callable objects
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowExecutionContext':
        """
        Create an execution context from a dictionary representation.

        Args:
            data: Dictionary representation of the execution context

        Returns:
            WorkflowExecutionContext: The created execution context
        """
        return cls(
            execution_id=data["execution_id"],
            workflow_id=data["workflow_id"],
            status=data["status"],
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            node_results=data.get("node_results", {}),
            node_errors=data.get("node_errors", {}),
            execution_path=data.get("execution_path", []),
            current_node_id=data.get("current_node_id"),
            input_data=data.get("input_data", {}),
            results=data.get("results", {}),
            metadata=data.get("metadata", {}),
            # Enhanced fields
            variables=data.get("variables", {}),
            subworkflow_contexts=data.get("subworkflow_contexts", {}),
            retry_counts=data.get("retry_counts", {})
            # Note: execution_hooks are initialized as empty since they can't be serialized
        )
