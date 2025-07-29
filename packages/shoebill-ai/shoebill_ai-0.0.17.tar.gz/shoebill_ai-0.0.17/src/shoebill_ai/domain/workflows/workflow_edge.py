from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class WorkflowEdge:
    """
    Represents an edge in a workflow graph, connecting two nodes.

    An edge defines how data flows from one node to another, including any transformations
    that should be applied to the data.
    """
    edge_id: str
    source_node_id: str
    target_node_id: str
    source_output: Optional[str] = None  # If None, uses the default output
    target_input: Optional[str] = None   # If None, uses the default input
    condition: Optional[str] = None      # Optional condition for conditional edges
    transformation: Optional[str] = None # Optional transformation function to apply
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        """
        Get the edge ID.

        This property provides a more intuitive way to access the edge ID.
        It returns the same value as edge_id.

        Returns:
            str: The edge ID
        """
        return self.edge_id

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the edge to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the edge
        """
        return {
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "source_output": self.source_output,
            "target_input": self.target_input,
            "condition": self.condition,
            "transformation": self.transformation,
            "config": self.config,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowEdge':
        """
        Create an edge from a dictionary representation.

        Args:
            data: Dictionary representation of the edge

        Returns:
            WorkflowEdge: The created edge
        """
        return cls(
            edge_id=data["edge_id"],
            source_node_id=data["source_node_id"],
            target_node_id=data["target_node_id"],
            source_output=data.get("source_output"),
            target_input=data.get("target_input"),
            condition=data.get("condition"),
            transformation=data.get("transformation"),
            config=data.get("config", {}),
            metadata=data.get("metadata", {})
        )
