from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable, Optional


class FunctionRegistry(ABC):
    """
    Interface for the function registry, which manages custom functions that can be used in workflows.
    """
    
    @abstractmethod
    def register(self, 
                 function_id: str, 
                 function: Callable, 
                 name: str = None, 
                 description: str = None,
                 input_schema: Dict[str, Any] = None,
                 output_schema: Dict[str, Any] = None,
                 tags: List[str] = None) -> None:
        """
        Register a function with the registry.
        
        Args:
            function_id: Unique identifier for the function
            function: The function to register
            name: Human-readable name for the function
            description: Description of the function's purpose
            input_schema: JSON schema describing the function's input parameters
            output_schema: JSON schema describing the function's output
            tags: Optional tags for categorizing the function
        """
        pass
    
    @abstractmethod
    def unregister(self, function_id: str) -> None:
        """
        Unregister a function from the registry.
        
        Args:
            function_id: The ID of the function to unregister
        """
        pass
    
    @abstractmethod
    def get(self, function_id: str) -> Optional[Callable]:
        """
        Get a function by its ID.
        
        Args:
            function_id: The ID of the function to retrieve
            
        Returns:
            The function if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_metadata(self, function_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a function.
        
        Args:
            function_id: The ID of the function
            
        Returns:
            Dict containing function metadata, or None if not found
        """
        pass
    
    @abstractmethod
    def list_functions(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered functions with their metadata.
        
        Returns:
            Dict mapping function IDs to their metadata
        """
        pass
    
    @abstractmethod
    def get_by_tags(self, tags: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get functions by tags.
        
        Args:
            tags: The tags to filter by
            
        Returns:
            Dict mapping function IDs to their metadata for functions that have all the specified tags
        """
        pass
    
    @abstractmethod
    def execute(self, function_id: str, *args, **kwargs) -> Any:
        """
        Execute a function with the given arguments.
        
        Args:
            function_id: The ID of the function to execute
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            The result of the function execution
            
        Raises:
            ValueError: If the function is not found
        """
        pass