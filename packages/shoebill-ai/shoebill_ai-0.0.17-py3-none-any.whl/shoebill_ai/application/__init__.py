"""
Application layer for the shoebill_ai package.

This package contains the public API for the shoebill_ai package.
Users should only import from this package, not from the domain or infrastructure layers.
"""

__all__ = [
    # Agent services
    'EmbeddingService', 'TextService', 'MultimodalService', 'VisionService',

    # Workflow services
    'AgentOrchestrator', 'FunctionService', 'WorkflowService', 'WorkflowQueueService'
]

# Agent services
from .agents.embedding_service import EmbeddingService
from .agents.multimodal_service import MultimodalService
from .agents.text_service import TextService
from .agents.vision_service import VisionService

# Workflow services
from .workflows.agent_orchestrator import AgentOrchestrator
from .workflows.function_service import FunctionService
from .workflows.workflow_service import WorkflowService
from .workflows.workflow_queue_service import WorkflowQueueService
