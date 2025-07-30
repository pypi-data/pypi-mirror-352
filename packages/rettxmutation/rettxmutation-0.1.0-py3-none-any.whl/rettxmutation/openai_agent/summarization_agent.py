"""
Summarization Agent

Handles summarization and correction of genetic reports using Semantic Kernel.
"""

import logging
import backoff
from typing import Dict
from pathlib import Path
from openai import RateLimitError
import semantic_kernel as sk
from semantic_kernel.functions import KernelArguments

from .base_agent import BaseAgent
from .exceptions import InvalidResponse
from .utils import validate_response_format, load_latest_transcripts

logger = logging.getLogger(__name__)


class SummarizationAgent(BaseAgent):
    """Agent for summarizing and correcting genetic reports using Semantic Kernel."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the summarization agent."""
        super().__init__(*args, **kwargs)
        
        # Load latest transcripts for correction
        self._latest_transcripts = load_latest_transcripts()
        
        # Load the summarization function
        summarize_template = self._load_prompt_template("summarization/summarize_report.skprompt.txt")
        
        self._summarize_function = self._kernel.add_function(
            plugin_name="summarization",
            function_name="summarize_report",
            description="Summarize genetic clinical reports focusing on MECP2",
            prompt=summarize_template
        )
        
        # Load the correction function
        correct_template = self._load_prompt_template("summarization/correct_summary_mistakes.skprompt.txt")
        
        self._correct_function = self._kernel.add_function(
            plugin_name="summarization",
            function_name="correct_summary_mistakes",
            description="Correct mistakes in genetic report summaries",
            prompt=correct_template        )
        
        logger.debug("Summarization agent initialized")

    @backoff.on_exception(
        backoff.expo,
        (RateLimitError),
        max_tries=5
    )
    async def summarize_report(
        self,
        document_text: str,
        keywords: str
    ) -> str:
        """
        Summarize a genetic report using Semantic Kernel.
        
        Args:
            document_text: The cleaned OCR text
            keywords: Keywords to guide the summary
            
        Returns:
            str: The summarized text
        """
        try:
            logger.debug("Running report summarization with Semantic Kernel")
            
            # Prepare arguments
            arguments = KernelArguments(
                document_text=document_text,
                keywords=keywords
            )
              # Execute the semantic function
            result = await self._kernel.invoke(
                plugin_name="summarization",
                function_name="summarize_report",
                arguments=arguments
            )
            response_content = str(result).strip()
            
            if not response_content:
                raise InvalidResponse("No response provided by Semantic Kernel")
            
            logger.debug(f"SK summarization response: {response_content}")
            
            return response_content
        except Exception as e:
            logger.error(f"Error during report summarization: {e}")
            raise

    @backoff.on_exception(
        backoff.expo,
        (RateLimitError),
        max_tries=5
    )
    async def correct_summary_mistakes(
        self,
        document_text: str,
        keywords: str,
        text_analytics: str
    ) -> str:
        """
        Correct mistakes in a genetic report summary using Semantic Kernel.
        
        Args:
            document_text: The summary text to correct
            keywords: Keywords that guided the original summary
            text_analytics: Results from text analytics
            
        Returns:
            str: The corrected summary text
        """
        try:
            logger.debug("Running summary correction with Semantic Kernel")
            
            # Prepare arguments
            arguments = KernelArguments(
                document_text=document_text,
                keywords=keywords,
                text_analytics=text_analytics,
                latest_transcripts=str(self._latest_transcripts)
            )
              # Execute the semantic function
            result = await self._kernel.invoke(
                plugin_name="summarization",
                function_name="correct_summary_mistakes",
                arguments=arguments
            )
            response_content = str(result).strip()
            
            if not response_content:
                raise InvalidResponse("No response provided by Semantic Kernel")
            
            logger.debug(f"SK correction response: {response_content}")
            
            return response_content
            
        except Exception as e:
            logger.error(f"Error during summary correction: {e}")
            raise
