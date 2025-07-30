"""
OpenAI Agent Exceptions

Custom exceptions for the OpenAI Agent component of RettXMutation library.
"""


class OpenAIAgentException(Exception):
    """Base exception for OpenAI Agent-related errors."""
    pass


class InvalidResponse(OpenAIAgentException):
    """Custom exception for invalid OpenAI response."""
    def __init__(self, message: str = "Invalid OpenAI response."):
        self.message = message
        super().__init__(f"{message}")


class AgentConfigurationError(OpenAIAgentException):
    """Raised when agent configuration is invalid."""
    pass


class PromptTemplateError(OpenAIAgentException):
    """Raised when prompt template loading or parsing fails."""
    pass


class PromptExecutionError(OpenAIAgentException):
    """Raised when semantic function execution fails."""
    pass


class EmbeddingGenerationError(OpenAIAgentException):
    """Raised when embedding generation fails."""
    pass
