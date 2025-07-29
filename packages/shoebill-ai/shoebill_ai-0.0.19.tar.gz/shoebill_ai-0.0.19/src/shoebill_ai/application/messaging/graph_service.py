import logging
from typing import Optional, Any, Dict

from h_message_bus import NatsPublisherAdapter

from ...domain.messaging.graph.graph_get_all_request_message import GraphGetAllRequestMessage
from ...domain.messaging.graph.graph_get_all_result_response_message import GraphGetAllResultResponseMessage
from ...domain.messaging.graph.graph_node_add_request_message import GraphNodeAddRequestMessage
from ...domain.messaging.graph.graph_query_operation_request_message import GraphQueryOperationRequestMessage
from ...domain.messaging.graph.graph_query_operation_response_message import GraphQueryOperationResponseMessage
from ...domain.messaging.graph.graph_relationship_added_request_message import GraphRelationshipAddRequestMessage


class GraphService:
    def __init__(self, nats_publisher_adapter: NatsPublisherAdapter):
        self.nats_publisher_adapter = nats_publisher_adapter
        self.logger = logging.getLogger(__name__)

    async def query_operation(self, operation_type: str,
                              anchor_node: str,
                              relationship_type: str = None,
                              relationship_direction: str = None,
                              limit: int = None,
                              traversal_depth: int = None,
                              timeout: float = 30.0
                              ) -> Optional[Dict[str, Any]]:
        try:
            # Create the request message
            request_message = GraphQueryOperationRequestMessage.create_message(
                operation_type=operation_type,
                anchor_node=anchor_node,
                relationship_type=relationship_type,
                relationship_direction=relationship_direction,
                limit=limit,
                traversal_depth=traversal_depth
            )

            # Send the request and await the response
            response = await self.nats_publisher_adapter.request(
                request_message,
                timeout=timeout
            )

            # Parse the response
            if response:
                response_message = GraphQueryOperationResponseMessage.from_hai_message(response)

                if response_message.success:
                    self.logger.info(f"Successfully processed {operation_type} operation for node '{anchor_node}'")
                    return response_message.result
                else:
                    self.logger.error(f"Error processing {operation_type} operation: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for {operation_type} operation (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Failed to send or process {operation_type} operation: {str(e)}")
            return None

    async def get_all_nodes(self, timeout: float = 30.0):
        try:
            # Create a request to get all nodes
            request = GraphGetAllRequestMessage.create_message()

            # Publish the request and await the response
            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            alldata=GraphGetAllResultResponseMessage.from_hai_message(response)
            #print(alldata.nodes)
            return alldata.nodes

        except Exception as e:
            self.logger.error(f"Error creating documents from graph nodes: {str(e)}")
            return 0

    async def add_node(self, node_id: str, label: str, description: str, properties: dict[str, str]):
        try:
            request = GraphNodeAddRequestMessage.create_message(
                node_id=node_id,
                label=label,
                properties=properties,
                description=description)

            await self.nats_publisher_adapter.publish(request)

        except Exception as e:
            self.logger.error(f"Error adding node: {str(e)}")

    async def add_relation(self, source_node_id: str, target_node_id: str, relationship: str):
        try:

            request = GraphRelationshipAddRequestMessage.create_message(
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                relationship_type=relationship)

            await self.nats_publisher_adapter.publish(request)
        except Exception as e:
            self.logger.error(f"Error adding relation: {str(e)}")
