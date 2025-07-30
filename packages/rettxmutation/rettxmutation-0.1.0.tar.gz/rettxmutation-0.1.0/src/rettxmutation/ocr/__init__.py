"""
RettX OCR Component

This module provides OCR functionality for the RettXMutation library.
It encapsulates text extraction, cleaning, gene variant detection, and confidence validation.
"""

from .ocr_service import OcrService
from .ocr_utils import OcrTextProcessor
from .exceptions import OcrException, OcrExtractionError, OcrProcessingError, OcrConfidenceError

__all__ = [
    'OcrService',
    'OcrTextProcessor', 
    'OcrException',
    'OcrExtractionError',
    'OcrProcessingError',
    'OcrConfidenceError'
]
