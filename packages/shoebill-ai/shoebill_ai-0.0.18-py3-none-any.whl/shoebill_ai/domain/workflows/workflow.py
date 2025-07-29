import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from .workflow_edge import WorkflowEdge
from .workflow_node import WorkflowNode


@dataclass
class Workflow:
    """
    Represents a workflow composed of nodes and edges.

    A workflow is a directed graph where nodes represent processing steps (agents, functions, etc.)
    and edges represent the flow of data between nodes.

    Enhanced features:
    - Subworkflows: Support for parent-child relationships between workflows
    - Versioning: Track workflow versions
    - UI Metadata: Support for visual representation in UI tools
    """
    workflow_id: str
    name: str
    description: Optional[str] = None
    nodes: Dict[str, WorkflowNode] = field(default_factory=dict)
    edges: Dict[str, WorkflowEdge] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    # Enhanced fields
    parent_workflow_id: Optional[str] = None
    ui_metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        """
        Get the workflow ID.

        This property provides a more intuitive way to access the workflow ID.
        It returns the same value as workflow_id.

        Returns:
            str: The workflow ID
        """
        return self.workflow_id

    @classmethod
    def create(cls, name: str, description: Optional[str] = None, parent_workflow_id: Optional[str] = None) -> 'Workflow':
        """
        Create a new workflow with a generated ID.

        Args:
            name: The name of the workflow
            description: Optional description of the workflow
            parent_workflow_id: Optional ID of the parent workflow (for subworkflows)

        Returns:
            Workflow: The created workflow
        """
        return cls(
            workflow_id=str(uuid.uuid4()),
            name=name,
            description=description,
            parent_workflow_id=parent_workflow_id
        )

    def add_node(self, node: WorkflowNode) -> None:
        """
        Add a node to the workflow.

        Args:
            node: The node to add
        """
        self.nodes[node.node_id] = node

    def remove_node(self, node_id: str) -> None:
        """
        Remove a node from the workflow.

        Args:
            node_id: The ID of the node to remove
        """
        if node_id in self.nodes:
            # Remove the node
            del self.nodes[node_id]

            # Remove any edges connected to this node
            edges_to_remove = []
            for edge_id, edge in self.edges.items():
                if edge.source_node_id == node_id or edge.target_node_id == node_id:
                    edges_to_remove.append(edge_id)

            for edge_id in edges_to_remove:
                del self.edges[edge_id]

    def add_edge(self, edge: WorkflowEdge) -> None:
        """
        Add an edge to the workflow.

        Args:
            edge: The edge to add
        """
        # Validate that the source and target nodes exist
        if edge.source_node_id not in self.nodes:
            raise ValueError(f"Source node {edge.source_node_id} does not exist in the workflow")
        if edge.target_node_id not in self.nodes:
            raise ValueError(f"Target node {edge.target_node_id} does not exist in the workflow")

        self.edges[edge.edge_id] = edge

    def remove_edge(self, edge_id: str) -> None:
        """
        Remove an edge from the workflow.

        Args:
            edge_id: The ID of the edge to remove
        """
        if edge_id in self.edges:
            del self.edges[edge_id]

    def get_node(self, node_id: str) -> Optional[WorkflowNode]:
        """
        Get a node by its ID.

        Args:
            node_id: The ID of the node to retrieve

        Returns:
            The node if found, None otherwise
        """
        return self.nodes.get(node_id)

    def get_edge(self, edge_id: str) -> Optional[WorkflowEdge]:
        """
        Get an edge by its ID.

        Args:
            edge_id: The ID of the edge to retrieve

        Returns:
            The edge if found, None otherwise
        """
        return self.edges.get(edge_id)

    def get_node_inputs(self, node_id: str) -> List[WorkflowEdge]:
        """
        Get all edges that have the specified node as their target.

        Args:
            node_id: The ID of the node

        Returns:
            List of edges that have the specified node as their target
        """
        return [edge for edge in self.edges.values() if edge.target_node_id == node_id]

    def get_node_outputs(self, node_id: str) -> List[WorkflowEdge]:
        """
        Get all edges that have the specified node as their source.

        Args:
            node_id: The ID of the node

        Returns:
            List of edges that have the specified node as their source
        """
        return [edge for edge in self.edges.values() if edge.source_node_id == node_id]

    def get_start_nodes(self) -> List[WorkflowNode]:
        """
        Get all nodes that have no incoming edges (start nodes).

        Returns:
            List of nodes that have no incoming edges
        """
        nodes_with_inputs = {edge.target_node_id for edge in self.edges.values()}
        start_node_ids = set(self.nodes.keys()) - nodes_with_inputs
        return [self.nodes[node_id] for node_id in start_node_ids]

    def get_end_nodes(self) -> List[WorkflowNode]:
        """
        Get all nodes that have no outgoing edges (end nodes).

        Returns:
            List of nodes that have no outgoing edges
        """
        nodes_with_outputs = {edge.source_node_id for edge in self.edges.values()}
        end_node_ids = set(self.nodes.keys()) - nodes_with_outputs
        return [self.nodes[node_id] for node_id in end_node_ids]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the workflow to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the workflow
        """
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "edges": {edge_id: edge.to_dict() for edge_id, edge in self.edges.items()},
            "metadata": self.metadata,
            "version": self.version,
            # Enhanced fields
            "parent_workflow_id": self.parent_workflow_id,
            "ui_metadata": self.ui_metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workflow':
        """
        Create a workflow from a dictionary representation.

        Args:
            data: Dictionary representation of the workflow

        Returns:
            Workflow: The created workflow
        """
        workflow = cls(
            workflow_id=data["workflow_id"],
            name=data["name"],
            description=data.get("description"),
            metadata=data.get("metadata", {}),
            version=data.get("version", "1.0.0"),
            # Enhanced fields
            parent_workflow_id=data.get("parent_workflow_id"),
            ui_metadata=data.get("ui_metadata", {})
        )

        # Add nodes
        for node_data in data.get("nodes", {}).values():
            workflow.add_node(WorkflowNode.from_dict(node_data))

        # Add edges
        for edge_data in data.get("edges", {}).values():
            workflow.add_edge(WorkflowEdge.from_dict(edge_data))

        return workflow

    def validate(self) -> List[str]:
        """
        Validate the workflow for correctness.

        Returns:
            List[str]: List of validation errors, empty if the workflow is valid
        """
        errors = []

        # Check for cycles
        if self._has_cycles():
            errors.append("Workflow contains cycles")

        # Check for disconnected nodes
        disconnected_nodes = self._get_disconnected_nodes()
        if disconnected_nodes:
            errors.append(f"Workflow contains disconnected nodes: {', '.join(disconnected_nodes)}")

        # Check for missing nodes referenced by edges
        for edge_id, edge in self.edges.items():
            if edge.source_node_id not in self.nodes:
                errors.append(f"Edge {edge_id} references non-existent source node {edge.source_node_id}")
            if edge.target_node_id not in self.nodes:
                errors.append(f"Edge {edge_id} references non-existent target node {edge.target_node_id}")

        return errors

    def _has_cycles(self) -> bool:
        """
        Check if the workflow contains cycles.

        Returns:
            bool: True if the workflow contains cycles, False otherwise
        """
        # Implementation of cycle detection algorithm
        visited = set()
        rec_stack = set()

        def dfs(node_id):
            visited.add(node_id)
            rec_stack.add(node_id)

            for edge in self.get_node_outputs(node_id):
                neighbor = edge.target_node_id
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                if dfs(node_id):
                    return True

        return False

    def _get_disconnected_nodes(self) -> List[str]:
        """
        Get all nodes that are disconnected from the rest of the workflow.

        Returns:
            List[str]: List of IDs of disconnected nodes
        """
        connected_nodes = set()

        # Start with nodes that have edges
        for edge in self.edges.values():
            connected_nodes.add(edge.source_node_id)
            connected_nodes.add(edge.target_node_id)

        # Find nodes that are not connected
        disconnected_nodes = set(self.nodes.keys()) - connected_nodes

        return list(disconnected_nodes)
