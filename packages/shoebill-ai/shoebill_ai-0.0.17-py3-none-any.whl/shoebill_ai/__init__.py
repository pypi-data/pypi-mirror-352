"""
shoebill_ai package for interacting with LLM models.

This package provides a high-level API for interacting with LLM models.
Users should import from this package, not from the application, domain, or infrastructure layers directly.
"""

__all__ = [
    # Main orchestration class
    'AgentOrchestrator',

    # Agent services
    'EmbeddingService', 'TextService', 'MultimodalService', 'VisionService',

    # Workflow services
    'FunctionService', 'WorkflowService', 'WorkflowQueueService'
]

from .application import EmbeddingService, TextService, MultimodalService, VisionService, WorkflowQueueService, \
    WorkflowService, FunctionService
# Import the classes when they're actually used to avoid circular imports
from .application.workflows.agent_orchestrator import AgentOrchestrator
