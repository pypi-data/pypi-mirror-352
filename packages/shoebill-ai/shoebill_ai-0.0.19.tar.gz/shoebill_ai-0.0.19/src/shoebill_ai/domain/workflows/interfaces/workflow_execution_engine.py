from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from ..workflow import Workflow
from ..workflow_execution_context import WorkflowExecutionContext


class WorkflowExecutionEngine(ABC):
    """
    Interface for the workflow execution engine, which is responsible for executing workflows.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a workflow execution.
        
        Args:
            execution_id: The ID of the execution
            
        Returns:
            Optional[Dict[str, Any]]: The execution status, or None if not found
        """
        pass
    
    @abstractmethod
    def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a running workflow execution.
        
        Args:
            execution_id: The ID of the execution to cancel
            
        Returns:
            bool: True if the execution was cancelled, False otherwise
        """
        pass
    
    @abstractmethod
    def list_executions(self, workflow_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        List all executions, optionally filtered by workflow ID.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of execution IDs to execution summaries
        """
        pass