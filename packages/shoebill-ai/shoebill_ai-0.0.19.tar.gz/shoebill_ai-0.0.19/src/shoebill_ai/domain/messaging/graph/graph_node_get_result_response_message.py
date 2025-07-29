from typing import TypeVar, Dict, Any, Type, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphNodeGetResultResponseMessage(HaiMessage):
    """Message containing a requested node from the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, node_id: str, label: str, properties: dict = None,
                       description: str = None, found: bool = True) -> 'GraphNodeGetResultResponseMessage':
        """Create a message with the requested node information"""
        if properties is None:
            properties = {}

        return cls.create(
            topic=RequestMessageTopic.GRAPH_NODE_GET_RESPONSE,
            payload={
                "node_id": node_id,
                "label": label,
                "properties": properties,
                "description": description,
                "found": found
            },
        )

    @property
    def node_id(self) -> str:
        """Get the node ID from the payload"""
        return self.payload.get("node_id")

    @property
    def label(self) -> str:
        """Get the label from the payload"""
        return self.payload.get("label")

    @property
    def properties(self) -> dict:
        """Get the properties from the payload"""
        return self.payload.get("properties", {})

    @property
    def description(self) -> Optional[str]:
        """Get the description from the payload"""
        return self.payload.get("description")

    @property
    def found(self) -> bool:
        """Check if the node was found"""
        return self.payload.get("found", False)

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphNodeGetResultResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            node_id=payload.get("node_id", ''),
            label=payload.get("label", ''),
            properties=payload.get("properties", {}),
            description=payload.get("description"),
            found=payload.get("found", False)
        )
