"""
Mutation Extraction Agent

Handles mutation extraction from genetic documents using Semantic Kernel.
"""

import logging
import backoff
from typing import Dict, List
from pathlib import Path
from openai import RateLimitError
import semantic_kernel as sk
from semantic_kernel.functions import KernelArguments

from .base_agent import BaseAgent
from .exceptions import InvalidResponse
from .utils import validate_response_format, load_latest_transcripts
from ..models.gene_models import RawMutation

logger = logging.getLogger(__name__)


class MutationExtractionAgent(BaseAgent):
    """Agent for extracting MECP2 mutations from genetic documents using Semantic Kernel."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the mutation extraction agent."""
        super().__init__(*args, **kwargs)
        
        # Load latest transcripts for mutation extraction
        self._latest_transcripts = load_latest_transcripts()
        
        # Load the mutation extraction function
        prompt_template = self._load_prompt_template("extraction/extract_mutations.skprompt.txt")
        
        self._extract_function = self._kernel.add_function(
            plugin_name="extraction",
            function_name="extract_mutations",
            description="Extract MECP2 mutations from genetic documents",
            prompt=prompt_template
        )
        
        logger.debug("Mutation extraction agent initialized")

    @backoff.on_exception(backoff.expo, (RateLimitError), max_tries=5)
    async def extract_mutations(
        self,
        document_text: str,
        mecp2_keywords: str,
        variant_list: str
    ) -> List[RawMutation]:
        """
        Extract MECP2 mutations from document text using Semantic Kernel.

        Args:
            document_text: The cleaned OCR text
            mecp2_keywords: Detected MECP2-related keywords
            variant_list: Detected variant patterns

        Returns:
            List[RawMutation]: List of extracted mutations
        """
        try:
            logger.debug("Running SK mutation extraction")

            arguments = KernelArguments(
                document_text=document_text,
                mecp2_keywords=mecp2_keywords,
                variant_list=variant_list
            )

            result = await self._kernel.invoke(
                plugin_name="extraction",
                function_name="extract_mutations",
                arguments=arguments
            )
            response_content = str(result).strip()

            if not response_content:
                raise InvalidResponse("No response provided by Semantic Kernel")

            logger.debug(f"SK extraction response: {response_content}")

            mutations = self._parse_mutations(response_content)

            logger.info(f"Extracted {len(mutations)} valid mutations")

            return mutations

        except Exception as e:
            logger.error(f"Error during mutation extraction: {e}")
            raise

    @staticmethod
    def _parse_mutations(response_content: str) -> List[RawMutation]:
        """
        Parse mutation objects from the response content.

        Args:
            response_content: Raw response from the AI model

        Returns:
            List[RawMutation]: List of parsed mutations
        """
        mutations = []

        # Check for "No mutation found" response
        if "no mutation found" in response_content.lower():
            logger.debug("No mutations found in response")
            return mutations

        # Parse each line for mutations
        for line in response_content.split("\n"):
            line = line.strip()
            if not line:
                continue

            try:
                components = line.split(";")
                if len(components) != 2:
                    logger.warning(f"Invalid mutation format: {line}")
                    continue

                mutation_info = components[0].strip()
                confidence_part = components[1].strip()

                if not confidence_part.startswith("confidence="):
                    logger.warning(f"Invalid confidence format: {confidence_part}")
                    continue

                confidence = float(confidence_part.split("=")[1])

                if not (0.0 <= confidence <= 1.0):
                    logger.warning(f"Confidence out of range: {confidence}")
                    continue

                logger.debug(f"Parsed mutation: {mutation_info}, confidence: {confidence}")

                mutation = RawMutation(
                    mutation=mutation_info,
                    confidence=confidence
                )

                mutations.append(mutation)

            except Exception as e:
                logger.warning(f"Failed to parse mutation line '{line}': {e}")
                continue

        return mutations
