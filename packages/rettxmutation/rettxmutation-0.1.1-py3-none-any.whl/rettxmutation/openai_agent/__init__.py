"""
OpenAI Agent Component

Semantic Kernel-based agents for genetic report analysis and mutation extraction.

This component provides modular AI agents for:
- Mutation extraction from genetic reports
- Report summarization and correction
- Document validation
- Text embeddings

Usage:
    from rettxmutation.openai_agent import (
        MutationExtractionAgent,
        SummarizationAgent,
        ValidationAgent,
        EmbeddingClient
    )
    
    # Initialize agents with Azure OpenAI credentials
    mutation_agent = MutationExtractionAgent(
        api_key="your-api-key",
        api_version="2024-02-01",
        azure_endpoint="https://your-endpoint.openai.azure.com/",
        model_name="gpt-4",
        embedding_deployment="text-embedding-ada-002"
    )
    
    # Extract mutations from document
    mutations = await mutation_agent.extract_mutations(
        audit_context=audit_context,
        document_text=cleaned_text,
        mecp2_keywords=keywords,
        variant_list=variants
    )
"""

from .base_agent import BaseAgent
from .mutation_extraction_agent import MutationExtractionAgent
from .summarization_agent import SummarizationAgent
from .validation_agent import ValidationAgent
from .embedding_client import EmbeddingClient
from .exceptions import (
    OpenAIAgentException,
    InvalidResponse,
    AgentConfigurationError,
    PromptTemplateError
)
from .utils import (
    check_genetic_info,
    load_latest_transcripts,
    validate_response_format
)

__all__ = [
    # Core agents
    "BaseAgent",
    "MutationExtractionAgent", 
    "SummarizationAgent",
    "ValidationAgent",
    "EmbeddingClient",
    
    # Exceptions
    "OpenAIAgentException",
    "InvalidResponse",
    "AgentConfigurationError", 
    "PromptTemplateError",
    
    # Utilities
    "check_genetic_info",
    "load_latest_transcripts",
    "validate_response_format"
]
