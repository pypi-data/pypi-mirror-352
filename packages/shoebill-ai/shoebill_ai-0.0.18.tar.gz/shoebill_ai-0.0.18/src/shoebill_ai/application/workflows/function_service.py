from typing import Dict, List, Any, Callable, Optional
import uuid
import inspect

from ...domain.agents.interfaces.function_registry import FunctionRegistry


class FunctionService:
    """
    Application service for managing custom functions.
    
    This service provides high-level operations for registering, retrieving, and executing custom functions.
    """
    
    def __init__(self, function_registry: FunctionRegistry):
        """
        Initialize the function service.
        
        Args:
            function_registry: Registry for storing and retrieving functions
        """
        self.function_registry = function_registry
    
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
        # Generate a function ID if not provided
        if not function_id:
            function_id = str(uuid.uuid4())
        
        # Use the function name if name is not provided
        if not name:
            name = function.__name__
        
        # Generate input schema from function signature if not provided
        if not input_schema:
            input_schema = self._generate_input_schema(function)
        
        self.function_registry.register(
            function_id=function_id,
            function=function,
            name=name,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema,
            tags=tags
        )
        
        return function_id
    
    def unregister_function(self, function_id: str) -> None:
        """
        Unregister a function from the registry.
        
        Args:
            function_id: The ID of the function to unregister
        """
        self.function_registry.unregister(function_id)
    
    def get_function(self, function_id: str) -> Optional[Callable]:
        """
        Get a function by its ID.
        
        Args:
            function_id: The ID of the function to retrieve
            
        Returns:
            The function if found, None otherwise
        """
        return self.function_registry.get(function_id)
    
    def get_function_metadata(self, function_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a function.
        
        Args:
            function_id: The ID of the function
            
        Returns:
            Dict containing function metadata, or None if not found
        """
        return self.function_registry.get_metadata(function_id)
    
    def list_functions(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered functions with their metadata.
        
        Returns:
            Dict mapping function IDs to their metadata
        """
        return self.function_registry.list_functions()
    
    def get_functions_by_tags(self, tags: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get functions by tags.
        
        Args:
            tags: The tags to filter by
            
        Returns:
            Dict mapping function IDs to their metadata for functions that have all the specified tags
        """
        return self.function_registry.get_by_tags(tags)
    
    def execute_function(self, function_id: str, *args, **kwargs) -> Any:
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
        return self.function_registry.execute(function_id, *args, **kwargs)
    
    def _generate_input_schema(self, function: Callable) -> Dict[str, Any]:
        """
        Generate an input schema from a function's signature.
        
        Args:
            function: The function to generate a schema for
            
        Returns:
            Dict representing the input schema
        """
        signature = inspect.signature(function)
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for name, param in signature.parameters.items():
            # Skip self parameter for methods
            if name == "self":
                continue
                
            # Add parameter to properties
            schema["properties"][name] = {"type": "any"}
            
            # If the parameter has no default value, it's required
            if param.default == inspect.Parameter.empty:
                schema["required"].append(name)
        
        return schema