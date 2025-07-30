"""
OpenAI Agent Utilities

Common utility functions for the OpenAI Agent component.
"""

import re
import json
import logging
import pkg_resources
from typing import Dict, Any, Optional
from pathlib import Path

try:
    # Python 3.9+
    from importlib.resources import files
except ImportError:
    # Python 3.8 fallback
    from importlib_resources import files


logger = logging.getLogger(__name__)


def check_genetic_info(document_text: str) -> bool:
    """
    Check if document contains genetic information using regex patterns.
    
    Args:
        document_text (str): The document text to check
        
    Returns:
        bool: True if genetic patterns are found, False otherwise
    """
    mutation_pattern = re.compile(
        r'c\.\d+'
        r'(?:_\d+)?'
        r'(?:[ACGT]>[ACGT]|del|ins[ACGT]+|dup[ACGT]*)',
        flags=re.IGNORECASE
    )
    
    transcript_pattern = re.compile(r'NM_\d+\.\d+')
    
    # Normalizing whitespace
    text = ' '.join(document_text.split())

    regex_has_mutation = bool(mutation_pattern.search(text))
    regex_has_transcript = bool(transcript_pattern.search(text))
    
    return regex_has_mutation or regex_has_transcript


def load_latest_transcripts() -> Dict[str, Any]:
    """
    Loads the latest transcripts configuration from a JSON file using importlib.resources.

    Returns:
        dict: Mapping of base transcript IDs to latest versions.
    """
    try:
        # Try to load from the new location using importlib.resources
        prompt_files = files('rettxmutation.openai_agent').joinpath('prompts').joinpath('shared')
        transcript_path = prompt_files.joinpath('latest_transcripts.json')
        
        if transcript_path.is_file():
            content = transcript_path.read_text(encoding='utf-8')
            latest_transcripts = json.loads(content)
            return latest_transcripts
        else:
            # Fallback to filesystem approach
            current_dir = Path(__file__).parent
            transcript_path = current_dir / "prompts" / "shared" / "latest_transcripts.json"
            
            if transcript_path.exists():
                with open(transcript_path, 'r') as file:
                    latest_transcripts = json.load(file)
                return latest_transcripts
            else:
                # Final fallback to original location
                resource_path = pkg_resources.resource_filename(
                    'rettxmutation.analysis', 
                    "data/latest_transcript_version.json"
                )
                
                with open(resource_path, 'r') as file:
                    latest_transcripts = json.load(file)
                return latest_transcripts
    except Exception as e:
        logger.warning(f"Could not load latest transcripts: {e}")
        return {}


def validate_response_format(response, expected_format: str = "default") -> bool:
    """
    Validate that the OpenAI response has the expected format.
    
    Args:
        response: The OpenAI response object
        expected_format (str): The expected format type
        
    Returns:
        bool: True if response format is valid, False otherwise
    """
    if not response or not response.choices:
        return False
        
    if not response.choices[0].message or response.choices[0].message.content is None:
        return False
        
    return True
