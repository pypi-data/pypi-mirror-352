"""
OCR Service

Handles extraction of text from documents via Azure Form Recognizer (Document Analysis).
This is a refactored version of the original OcrExtractor from analysis/ocr_extractor.py
"""

import logging
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from typing import BinaryIO, Optional, List
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeResult
from rettxmutation.models.document import Document, WordData, LineData
from .exceptions import OcrExtractionError


logger = logging.getLogger(__name__)


class OcrService:
    """
    Handles extraction of text from documents via Azure Form Recognizer
    (a.k.a. Document Analysis).
    """
    
    def __init__(self, endpoint: str, key: str):
        """
        Initialize the OCR service with Azure Document Analysis credentials.
        
        Args:
            endpoint (str): Azure Document Analysis endpoint
            key (str): Azure Document Analysis key
        """
        try:
            self._client = DocumentAnalysisClient(
                endpoint=endpoint,
                credential=AzureKeyCredential(key)
            )
            logger.debug("OCR Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OCR Service: {e}")
            raise OcrExtractionError(f"Failed to initialize OCR Service: {e}")

    def extract_text(self, file_stream: BinaryIO) -> Document:
        """
        Extracts text from a document and infers language (if available).
        
        Args:
            file_stream (BinaryIO): Binary stream of the document
            
        Returns:
            Document: Document object containing extracted text and metadata
            
        Raises:
            OcrExtractionError: If extraction fails
        """
        try:
            logger.debug("Processing stream with Form Recognizer")

            poller = self._client.begin_analyze_document(
                "prebuilt-read",
                document=file_stream,
                features=[DocumentAnalysisFeature.LANGUAGES]
            )
            result: AnalyzeResult = poller.result()

            if not result:
                error_msg = "No valid document found by Form Recognizer"
                logger.error(error_msg)
                raise OcrExtractionError(error_msg)

            # Infer language
            inferred_language = None
            if result.languages:
                inferred_language = self._infer_language(result.languages)
                logger.debug(f"Detected language: {inferred_language}")

            # Save the words data in a structured format (using WordData model)
            words = self._extract_words(result)
            # Save the lines data in a structured format (using LineData model)
            lines = self._extract_lines(result)

            logger.debug(f"Words processed: {len(words)}")
            logger.debug(f"Lines processed: {len(lines)}")
            logger.debug(f"Pages processed: {len(result.pages)}")

            return Document(
                raw_text=result.content, 
                language=inferred_language, 
                words=words, 
                lines=lines
            )

        except OcrExtractionError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            error_msg = f"Error processing file: {e}"
            logger.error(error_msg)
            raise OcrExtractionError(error_msg)

    def _extract_words(self, result: AnalyzeResult) -> List[WordData]:
        """
        Private helper to extract words data from an AnalyzeResult object.
        
        Args:
            result (AnalyzeResult): Azure Document Analysis result
            
        Returns:
            List[WordData]: List of word data objects
        """
        words_data = []
        for page in result.pages:
            for word in page.words:
                words_data.append(
                    WordData(
                        word=word.content,
                        confidence=word.confidence,
                        page_number=page.page_number,
                        offset=word.span.offset if word.span else None,
                        length=word.span.length if word.span else None
                    )
                )
        logger.debug(f"Extracted {len(words_data)} words across {len(result.pages)} pages.")
        return words_data

    def _extract_lines(self, result: AnalyzeResult) -> List[LineData]:
        """
        Private helper to extract lines data from an AnalyzeResult object.
        
        Args:
            result (AnalyzeResult): Azure Document Analysis result
            
        Returns:
            List[LineData]: List of line data objects
        """
        lines_data = []
        for page in result.pages:
            for line in page.lines:
                lines_data.append(
                    LineData(
                        line=line.content,
                        page_number=page.page_number,
                        length=len(line.content)
                    )
                )
        return lines_data

    def _infer_language(self, languages) -> Optional[str]:
        """
        Private helper to infer the most likely language from a list of language detections.
        
        Args:
            languages: Language detection results from Azure Document Analysis
            
        Returns:
            Optional[str]: Most likely language code or None
        """
        language_confidences = {}
        for language in languages:
            lang = language.locale
            conf = language.confidence
            language_confidences[lang] = language_confidences.get(lang, 0) + conf
        if not language_confidences:
            return None
        return max(language_confidences, key=language_confidences.get)
