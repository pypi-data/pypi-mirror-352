from typing import Dict, List, Any, Optional
import uuid
from dataclasses import dataclass, field

from .base_agent import BaseAgent
from ...application.agents.vision_service import VisionService


@dataclass
class VisionAgent(BaseAgent):
    """
    An agent that wraps a VisionService to provide vision-based AI capabilities.

    This agent directly uses the VisionService's methods for processing requests,
    eliminating the need for an intermediate AgentService.
    """
    service: VisionService = field(default=None, repr=False, compare=False)

    @classmethod
    def create(cls, 
               name: str, 
               description: str,
               model_name: str,
               api_url: str,
               system_prompt: Optional[str] = None,
               tags: List[str] = None,
               config: Dict[str, Any] = None,
               api_token: str = None,
               temperature: float = 0.6,
               max_tokens: int = 2500) -> 'VisionAgent':
        """
        Create a new VisionAgent with a VisionService.

        Args:
            name: The name of the agent
            description: Description of the agent's purpose and capabilities
            model_name: The name of the model to use
            api_url: The base URL of the API
            system_prompt: Optional system prompt to guide the agent's behavior
            tags: Optional tags for categorizing the agent
            config: Optional configuration for the agent
            api_token: Optional API token for authentication
            temperature: The temperature to use for generation
            max_tokens: The maximum number of tokens to generate

        Returns:
            The created VisionAgent
        """
        # Create the VisionService
        service = VisionService(
            api_url=api_url,
            api_token=api_token,
            temperature=temperature,
            max_tokens=max_tokens,
            model_name=model_name
        )

        # Create and return the VisionAgent
        return cls(
            agent_id=str(uuid.uuid4()),
            name=name,
            description=description,
            service=service,
            system_prompt=system_prompt,
            tools=[],  # Vision service doesn't support tools
            tags=tags or [],
            config=config or {}
        )

    def process(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None, use_generate: bool = False) -> Dict[str, Any]:
        """
        Process input data and return results.

        This method determines which VisionService method to call based on the input data.

        Args:
            input_data: The input data for the agent to process
            context: Optional context information
            use_generate: If True, use the generate method instead of chat (default: False)

        Returns:
            Dict[str, Any]: The processing results
        """
        # Extract relevant parameters from input_data
        message = input_data.get('message', input_data.get('query', ''))
        session_id = input_data.get('session_id', self.agent_id)
        image_path = input_data.get('image_path')
        chat_history = input_data.get('chat_history')
        max_tokens = input_data.get('max_tokens')

        # Determine which method to use based on the use_generate parameter
        if use_generate:
            # Use the VisionService's generate method
            result = self.service.generate(
                prompt=message,
                system_prompt=self.system_prompt,
                max_tokens=max_tokens
            )
        else:
            # Use the VisionService's chat method
            result = self.service.chat(
                message=message,
                session_id=session_id,
                image_path=image_path,
                chat_history=chat_history,
                system_prompt=self.system_prompt
            )

        # Format the result
        if isinstance(result, dict):
            # Add agent information to the result
            result['agent_id'] = self.agent_id
            result['agent_name'] = self.name
            return result
        else:
            # If result is not a dict, wrap it
            return {
                'result': result,
                'agent_id': self.agent_id,
                'agent_name': self.name
            }

    def chat(self, message: str, image_path: str = None, session_id: str = None, 
             chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Chat with the agent.

        This method directly calls the VisionService's chat method.

        Args:
            message: The user's message
            image_path: Optional path to an image to analyze
            session_id: Optional session ID (defaults to agent_id)
            chat_history: Optional chat history

        Returns:
            Dict[str, Any]: The chat response
        """
        return self.service.chat(
            message=message,
            session_id=session_id or self.agent_id,
            image_path=image_path,
            chat_history=chat_history,
            system_prompt=self.system_prompt
        )

    def generate(self, prompt: str, max_tokens: int = None) -> Dict[str, Any]:
        """
        Generate text using the agent.

        This method directly calls the VisionService's generate method.

        Args:
            prompt: The prompt to generate text from
            max_tokens: Optional maximum number of tokens to generate

        Returns:
            Dict[str, Any]: The generation response
        """
        return self.service.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=max_tokens
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the agent
        """
        base_dict = super().to_dict()
        base_dict.update({
            "model_name": self.service.model_name,
            "api_url": self.service.api_url
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any], api_url: str = None, api_token: str = None) -> 'VisionAgent':
        """
        Create a VisionAgent from a dictionary representation.

        Args:
            data: Dictionary representation of the agent
            api_url: The base URL of the API (if not included in data)
            api_token: Optional API token for authentication

        Returns:
            VisionAgent: The created agent
        """
        # Get API URL from data or parameter
        agent_api_url = data.get("api_url", api_url)
        if not agent_api_url:
            raise ValueError("API URL must be provided either in data or as a parameter")

        # Create the VisionService
        service = VisionService(
            api_url=agent_api_url,
            api_token=api_token,
            temperature=data.get("config", {}).get("temperature", 0.6),
            max_tokens=data.get("config", {}).get("max_tokens", 2500),
            model_name=data.get("model_name")
        )

        # Create and return the VisionAgent
        return cls(
            agent_id=data["agent_id"],
            name=data["name"],
            description=data["description"],
            service=service,
            system_prompt=data.get("system_prompt"),
            tools=[],  # Vision service doesn't support tools
            tags=data.get("tags", []),
            config=data.get("config", {})
        )
