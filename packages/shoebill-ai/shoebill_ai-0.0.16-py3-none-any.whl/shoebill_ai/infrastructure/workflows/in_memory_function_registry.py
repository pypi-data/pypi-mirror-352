import logging
from typing import Dict, List, Any, Callable, Optional

from ...domain.agents.interfaces.function_registry import FunctionRegistry


class InMemoryFunctionRegistry(FunctionRegistry):
    """
    In-memory implementation of the FunctionRegistry interface.

    This implementation stores functions and their metadata in memory and is suitable for testing and development.
    """

    def __init__(self):
        """
        Initialize the in-memory function registry.
        """
        self._functions: Dict[str, Callable] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

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
        function_name = name or function.__name__
        self.logger.info(f"Registering function with ID: {function_id}, name: {function_name}")

        # Log tags if provided
        if tags:
            self.logger.debug(f"Function tags: {tags}")

        self._functions[function_id] = function
        self._metadata[function_id] = {
            "function_id": function_id,
            "name": function_name,
            "description": description,
            "input_schema": input_schema or {},
            "output_schema": output_schema or {},
            "tags": tags or []
        }

        self.logger.info(f"Function {function_id} registered successfully")

    def unregister(self, function_id: str) -> None:
        """
        Unregister a function from the registry.

        Args:
            function_id: The ID of the function to unregister
        """
        self.logger.info(f"Unregistering function with ID: {function_id}")

        function_removed = False
        metadata_removed = False

        if function_id in self._functions:
            del self._functions[function_id]
            function_removed = True
            self.logger.debug(f"Removed function {function_id} from functions dictionary")

        if function_id in self._metadata:
            del self._metadata[function_id]
            metadata_removed = True
            self.logger.debug(f"Removed metadata for function {function_id}")

        if function_removed or metadata_removed:
            self.logger.info(f"Function {function_id} unregistered successfully")
        else:
            self.logger.warning(f"Attempted to unregister non-existent function with ID: {function_id}")

    def get(self, function_id: str) -> Optional[Callable]:
        """
        Get a function by its ID.

        Args:
            function_id: The ID of the function to retrieve

        Returns:
            The function if found, None otherwise
        """
        self.logger.info(f"Getting function with ID: {function_id}")

        function = self._functions.get(function_id)
        if function:
            self.logger.info(f"Found function with ID: {function_id}")
            self.logger.debug(f"Function name: {function.__name__}")
        else:
            self.logger.info(f"Function with ID {function_id} not found")

        return function

    def get_metadata(self, function_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a function.

        Args:
            function_id: The ID of the function

        Returns:
            Dict containing function metadata, or None if not found
        """
        self.logger.info(f"Getting metadata for function with ID: {function_id}")

        metadata = self._metadata.get(function_id)
        if metadata:
            self.logger.info(f"Found metadata for function with ID: {function_id}")
            self.logger.debug(f"Function metadata: {metadata}")
        else:
            self.logger.info(f"Metadata for function with ID {function_id} not found")

        return metadata

    def list_functions(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered functions with their metadata.

        Returns:
            Dict mapping function IDs to their metadata
        """
        self.logger.info("Listing all registered functions")

        result = self._metadata.copy()
        self.logger.info(f"Found {len(result)} registered functions")
        self.logger.debug(f"Function IDs: {list(result.keys())}")

        return result

    def get_by_tags(self, tags: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get functions by tags.

        Args:
            tags: The tags to filter by

        Returns:
            Dict mapping function IDs to their metadata for functions that have all the specified tags
        """
        self.logger.info(f"Getting functions with tags: {tags}")

        if not tags:
            self.logger.info("Empty tags list provided, returning empty result")
            return {}

        result = {}
        for function_id, metadata in self._metadata.items():
            function_tags = metadata.get("tags", [])
            # Check if all specified tags are in the function's tags
            if all(tag in function_tags for tag in tags):
                self.logger.debug(f"Found matching function with ID: {function_id}, tags: {function_tags}")
                result[function_id] = metadata

        self.logger.info(f"Found {len(result)} functions matching tags: {tags}")
        if result:
            self.logger.debug(f"Matching function IDs: {list(result.keys())}")
        return result

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
        self.logger.info(f"Executing function with ID: {function_id}")
        self.logger.debug(f"Function arguments: args={args}, kwargs={kwargs}")

        function = self.get(function_id)
        if not function:
            self.logger.error(f"Function {function_id} not found in registry")
            raise ValueError(f"Function {function_id} not found in registry")

        try:
            self.logger.debug(f"Calling function {function.__name__}")
            result = function(*args, **kwargs)
            self.logger.info(f"Function {function_id} executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error executing function {function_id}: {str(e)}")
            raise
