"""
Base Agent for Semantic Kernel Integration

Provides common functionality for initializing Semantic Kernel and Azure OpenAI services.
"""

import logging
from openai import AzureOpenAI
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
from importlib.resources import files


logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for Semantic Kernel-based agents."""

    def __init__(self,
                 api_key: str,
                 api_version: str,
                 azure_endpoint: str,
                 model_name: str,
                 embedding_deployment: str = None):
        """
        Initialize the base agent with Azure OpenAI configuration.
        
        Args:
            api_key: Azure OpenAI API key
            api_version: Azure OpenAI API version
            azure_endpoint: Azure OpenAI endpoint URL
            model_name: Chat model deployment name
            embedding_deployment: Embedding model deployment name (optional)
        """
        self._api_key = api_key
        self._api_version = api_version
        self._azure_endpoint = azure_endpoint
        self._model_name = model_name
        self._embedding_deployment = embedding_deployment

        # Initialize Semantic Kernel
        self._kernel = sk.Kernel()

        # Add Azure OpenAI chat service
        self._chat_service = AzureChatCompletion(
            deployment_name=model_name,
            endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self._kernel.add_service(self._chat_service)

        # Add Azure OpenAI embedding service (if deployment name provided)
        self._embedding_service = None
        if embedding_deployment:
            self._embedding_service = AzureTextEmbedding(
                deployment_name=embedding_deployment,
                endpoint=azure_endpoint,
                api_key=api_key,
                api_version=api_version
            )
            self._kernel.add_service(self._embedding_service)

        # Initialize direct OpenAI client for non-SK operations
        self._openai_client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )

        embedding_info = f" and embedding model: {embedding_deployment}" if embedding_deployment else ""
        logger.debug(f"{self.__class__.__name__} initialized with chat model: {model_name}{embedding_info}")

    @property
    def kernel(self) -> sk.Kernel:
        """Get the Semantic Kernel instance."""
        return self._kernel

    @property
    def chat_service(self) -> AzureChatCompletion:
        """Get the Azure Chat Completion service."""
        return self._chat_service

    @property
    def embedding_service(self) -> AzureTextEmbedding:
        """Get the Azure Embedding service."""
        return self._embedding_service

    @property
    def openai_client(self) -> AzureOpenAI:
        """Direct Azure OpenAI client (for non-SK calls)."""
        return self._openai_client

    def _load_prompt_yaml(self, yaml_path: str) -> str:
        """Load a prompt YAML configuration from the prompts directory using importlib.resources."""
        try:
            # Use importlib.resources to properly access package data
            prompt_files = files('rettxmutation.openai_agent').joinpath('prompts')
            yaml_file = prompt_files.joinpath(yaml_path)
            
            if yaml_file.is_file():
                return yaml_file.read_text(encoding='utf-8')
            else:
                raise FileNotFoundError(f"Prompt YAML not found: {yaml_path}")
        except Exception as e:
            # Fallback to the old method if importlib.resources fails
            logger.warning(f"importlib.resources failed, falling back to filesystem: {e}")
            from pathlib import Path
            prompts_dir = Path(__file__).parent / "prompts"
            yaml_file = prompts_dir / yaml_path
            
            if yaml_file.exists():
                return yaml_file.read_text(encoding='utf-8')
            else:
                raise FileNotFoundError(f"Prompt YAML not found: {yaml_file}")

    def _load_prompt_template(self, template_path: str) -> str:
        """Load a prompt template from the prompts directory using multiple fallback methods."""
        # Method 1: Try importlib.resources first
        try:
            prompt_files = files('rettxmutation.openai_agent').joinpath('prompts')
            template_file = prompt_files.joinpath(template_path)
            
            if template_file.is_file():
                return template_file.read_text(encoding='utf-8')
        except Exception as e:
            logger.debug(f"importlib.resources method failed: {e}")
        
        # Method 2: Try relative to current file
        try:
            from pathlib import Path
            prompts_dir = Path(__file__).parent / "prompts"
            template_file = prompts_dir / template_path
            
            if template_file.exists():
                return template_file.read_text(encoding='utf-8')
        except Exception as e:
            logger.debug(f"Filesystem method failed: {e}")
        
        # Method 3: Try to find prompts directory in package installation
        try:
            import rettxmutation.openai_agent
            from pathlib import Path
            package_dir = Path(rettxmutation.openai_agent.__file__).parent
            prompts_dir = package_dir / "prompts"
            template_file = prompts_dir / template_path
            
            if template_file.exists():
                return template_file.read_text(encoding='utf-8')
        except Exception as e:
            logger.debug(f"Package directory method failed: {e}")
        
        # If all methods fail, raise a descriptive error
        raise FileNotFoundError(
            f"Prompt template not found: {template_path}. "
            f"Tried importlib.resources, filesystem relative path, and package directory."
        )
