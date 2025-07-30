"""
OCR Component Exceptions

Custom exceptions for the OCR component of RettXMutation library.
"""


class OcrException(Exception):
    """Base exception for OCR-related errors."""
    pass


class OcrExtractionError(OcrException):
    """Raised when OCR text extraction fails."""
    pass


class OcrProcessingError(OcrException):
    """Raised when OCR text processing (cleaning, variant detection) fails."""
    pass


class OcrConfidenceError(OcrException):
    """Raised when OCR confidence validation fails."""
    pass
