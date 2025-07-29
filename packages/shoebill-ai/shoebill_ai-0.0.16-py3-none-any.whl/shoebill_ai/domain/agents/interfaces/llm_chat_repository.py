from abc import abstractmethod
from typing import Optional, List, Dict, Any, Protocol

from .base_repository import BaseRepository


class ChatMessage(Protocol):
    """Protocol for chat messages."""
    role: str
    content: str


class LlmChatRepository(BaseRepository):
    """
    Repository for chat interactions with an LLM.
    """

    @abstractmethod
    def chat(self, user_message: str = None, session_id: str = None, chat_history: List[Dict[str, str]] = None, 
             format: Dict[str, Any] = None, system_prompt: str = None, 
             messages: List[Any] = None, tools: List[Dict[str, Any]] = None) -> Optional[str]:
        """
        Chat with the LLM.

        This is the main method for chatting with the model. It can handle simple chat scenarios,
        custom messages, and tools.

        Args:
            user_message: The user's message. Not required if messages is provided.
            session_id: The ID of the chat session. Not required if messages is provided.
            chat_history: Optional chat history to include in the conversation.
            format: Optional JSON schema defining the structure of the expected output.
            system_prompt: Optional system prompt to override the default.
            messages: Optional custom list of messages to send to the model. If provided, user_message,
                     session_id, and chat_history are ignored.
            tools: Optional list of tools to make available to the model for this chat session.

        Returns:
            Optional[str]: The model's response, or None if the request failed.
        """
        ...