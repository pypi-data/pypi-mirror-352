"""
Validation Agent

Handles document validation using Semantic Kernel and regex-based checks.
"""

import logging
import backoff
from typing import Tuple
from pathlib import Path
from openai import RateLimitError
import semantic_kernel as sk
from semantic_kernel.functions import KernelArguments

from .base_agent import BaseAgent
from .exceptions import InvalidResponse
from .utils import validate_response_format, check_genetic_info

logger = logging.getLogger(__name__)


class ValidationAgent(BaseAgent):
    """Agent for validating genetic documents using Semantic Kernel."""

    def __init__(self, *args, **kwargs):
        """Initialize the validation agent."""
        super().__init__(*args, **kwargs)        # Load the validation function
        prompt_template = self._load_prompt_template("validation/validate_document.skprompt.txt")

        self._validate_function = self._kernel.add_function(
            plugin_name="validation",
            function_name="validate_document",
            description="Validate if document is a valid MECP2 mutation report",
            prompt=prompt_template
        )

        logger.debug("Validation agent initialized")

    @backoff.on_exception(
        backoff.expo,
        (RateLimitError),
        max_tries=5
    )
    async def validate_document(
        self,
        document_text: str,
        language: str = "en"
    ) -> Tuple[bool, float]:
        """
        Validate whether a document is a valid mutation report by combining regex 
        checks with Semantic Kernel-based evaluation.
        
        Args:
            document_text: The document text to validate
            language: The document language (default: "en")
            
        Returns:
            Tuple[bool, float]: (is_valid, confidence_score)
        """
        try:
            logger.debug("Running document validation with Semantic Kernel")

            # Step 1: Rule-based check using regex
            regex_result = check_genetic_info(document_text)

            # Prepare context message about the regex result
            regex_context = (
                "The initial regex check indicates that the document "
                + ("contains" if regex_result else "does not contain")
                + " obvious mutation patterns and transcript identifiers."
            )

            # Step 2: Use Semantic Kernel for nuanced evaluation
            arguments = KernelArguments(
                document_text=document_text,
                regex_context=regex_context,
                language=language
            )

            # Execute the semantic function
            result = await self._kernel.invoke(
                plugin_name="validation",
                function_name="validate_document", 
                arguments=arguments
            )
            response_content = str(result).strip()
            if not response_content:
                logger.error("No response provided by Semantic Kernel")
                return False, 0.0

            logger.debug(f"SK validation response: {response_content}")

            # Parse the response
            is_valid, confidence = self._parse_validation_response(response_content)

            return is_valid, confidence

        except Exception as e:
            logger.error(f"Error during document validation: {e}")

            # Return conservative result on error
            return False, 0.0

    def _parse_validation_response(self, response_content: str) -> Tuple[bool, float]:
        """
        Parse the validation response to extract decision and confidence.

        Args:
            response_content: Raw response from the AI model

        Returns:
            Tuple[bool, float]: (is_valid, confidence_score)
        """
        try:
            # Expected format: "True, confidence=0.8" or "False, confidence=0.3"
            decision, conf_part = response_content.split(",")
            is_valid = decision.strip() == "True"
            confidence = float(conf_part.split("=")[1].strip())

            # Validate confidence range
            if not (0.0 <= confidence <= 1.0):
                logger.warning(f"Confidence out of range: {confidence}, clamping to [0,1]")
                confidence = max(0.0, min(1.0, confidence))

            logger.debug(f"Parsed validation: is_valid={is_valid}, confidence={confidence}")
            
            return is_valid, confidence

        except Exception as e:
            logger.error(f"Failed to parse validation response '{response_content}': {e}")
            return False, 0.0
