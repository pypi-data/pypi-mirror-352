from typing import Dict, Optional, Type, ClassVar

from .workflow_node import NodeType
from ..agents.base_agent import BaseAgent
from ..agents.embedding_agent import EmbeddingAgent
from ..agents.multimodal_agent import MultimodalAgent
from ..agents.text_agent import TextAgent
from ..agents.vision_agent import VisionAgent


class NodeIORegistry:
    """
    Registry for standard input/output keys for different node types.
    
    This registry stores the default input and output keys for different node types,
    allowing the workflow execution engine to automatically determine the appropriate
    keys when they are not explicitly specified in edge connections.
    """
    
    # Default input/output keys for different agent types
    _agent_io_keys: ClassVar[Dict[Type[BaseAgent], Dict[str, str]]] = {
        TextAgent: {
            "input": "message",
            "output": "response"
        },
        VisionAgent: {
            "input": "image",
            "output": "response"
        },
        MultimodalAgent: {
            "input": "message",
            "output": "response"
        },
        EmbeddingAgent: {
            "input": "text",
            "output": "embeddings"
        }
    }
    
    # Default input/output keys for different node types
    _node_io_keys: ClassVar[Dict[NodeType, Dict[str, str]]] = {
        NodeType.INPUT: {
            "output": "text"  # Default output key for input nodes
        },
        NodeType.OUTPUT: {
            "input": "result"  # Default input key for output nodes
        },
        NodeType.FUNCTION: {
            "input": "input",  # Default input key for function nodes
            "output": "result"  # Default output key for function nodes
        }
    }
    
    @classmethod
    def get_default_input_key(cls, node_type: NodeType, agent_type: Optional[Type[BaseAgent]] = None) -> Optional[str]:
        """
        Get the default input key for a node type.
        
        Args:
            node_type: The type of the node
            agent_type: Optional agent type for agent nodes
            
        Returns:
            The default input key, or None if not found
        """
        if node_type == NodeType.AGENT and agent_type:
            return cls._agent_io_keys.get(agent_type, {}).get("input")
        return cls._node_io_keys.get(node_type, {}).get("input")
    
    @classmethod
    def get_default_output_key(cls, node_type: NodeType, agent_type: Optional[Type[BaseAgent]] = None) -> Optional[str]:
        """
        Get the default output key for a node type.
        
        Args:
            node_type: The type of the node
            agent_type: Optional agent type for agent nodes
            
        Returns:
            The default output key, or None if not found
        """
        if node_type == NodeType.AGENT and agent_type:
            return cls._agent_io_keys.get(agent_type, {}).get("output")
        return cls._node_io_keys.get(node_type, {}).get("output")
    
    @classmethod
    def register_agent_io_keys(cls, agent_type: Type[BaseAgent], input_key: str, output_key: str) -> None:
        """
        Register input/output keys for an agent type.
        
        Args:
            agent_type: The agent type
            input_key: The input key
            output_key: The output key
        """
        cls._agent_io_keys[agent_type] = {
            "input": input_key,
            "output": output_key
        }
    
    @classmethod
    def register_node_io_keys(cls, node_type: NodeType, input_key: Optional[str] = None, output_key: Optional[str] = None) -> None:
        """
        Register input/output keys for a node type.
        
        Args:
            node_type: The node type
            input_key: Optional input key
            output_key: Optional output key
        """
        if node_type not in cls._node_io_keys:
            cls._node_io_keys[node_type] = {}
            
        if input_key:
            cls._node_io_keys[node_type]["input"] = input_key
            
        if output_key:
            cls._node_io_keys[node_type]["output"] = output_key