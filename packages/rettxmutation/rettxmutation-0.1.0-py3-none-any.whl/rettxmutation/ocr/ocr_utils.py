"""
OCR Text Processing Utilities

Combines text cleaning and gene variant detection functionality.
This consolidates the TextCleaner and GeneVariantDetector classes 
from the original analysis module.
"""

import re
import ftfy
import logging
from typing import List, BinaryIO
from collections import Counter
from rettxmutation.models.document import Document, Keyword
from .ocr_service import OcrService
from .exceptions import OcrProcessingError, OcrConfidenceError


logger = logging.getLogger(__name__)


class OcrTextProcessor:
    """
    Combines OCR extraction, text cleaning, and gene variant detection
    into a unified processing pipeline.
    """

    def __init__(self, doc_analysis_endpoint: str, doc_analysis_key: str):
        """
        Initialize the OCR text processor.

        Args:
            doc_analysis_endpoint (str): Azure Document Analysis endpoint
            doc_analysis_key (str): Azure Document Analysis key
        """
        self.ocr_service = OcrService(doc_analysis_endpoint, doc_analysis_key)
        logger.debug("OCR Text Processor initialized successfully")

    def extract_and_process_text(self, file_stream: BinaryIO) -> Document:
        """
        Complete OCR processing pipeline: extract, clean, detect variants, validate confidence.
        This replaces the original extract_text method from RettXDocumentAnalysis.

        Args:
            file_stream (BinaryIO): Binary stream of the document

        Returns:
            Document: Fully processed document with cleaned text and detected keywords

        Raises:
            OcrProcessingError: If processing fails
        """
        try:
            # Step 1: Extract text using OCR
            document = self.ocr_service.extract_text(file_stream)

            # Step 2: Clean the extracted text
            document.cleaned_text = self.clean_ocr_text(document.raw_text)

            # Step 3: Detect gene variants and keywords
            document.keywords = self.detect_mecp2_keywords(document.cleaned_text)

            # Step 4: Validate OCR confidence scores for detected keywords
            self._validate_keyword_confidence(document)

            logger.debug(f"OCR processing completed successfully. Found {len(document.keywords)} keywords")
            return document

        except Exception as e:
            error_msg = f"OCR text processing failed: {e}"
            logger.error(error_msg)
            raise OcrProcessingError(error_msg)

    def clean_ocr_text(self, raw_text: str) -> str:
        """
        Takes raw text (e.g. from OCR) and normalizes / cleans it up:
        1. Fix common Unicode issues (ftfy).
        2. Collapse whitespace.
        3. Fix typical HGVS-like patterns.
        4. Additional checks for missing '.' after 'c', etc.

        Args:
            raw_text (str): Raw text from OCR

        Returns:
            str: Cleaned and normalized text
        """
        try:
            # 1) Fix garbled Unicode with ftfy
            text = ftfy.fix_text(raw_text)            # 2) Collapse all whitespace into a single space
            text = re.sub(r"\s+", " ", text).strip()

            # 3) Remove line breaks
            text = text.replace("\n", " ")

            # 3a) Normalizing c. patterns (e.g., c. 123A > G -> c.123A>G)
            text = re.sub(
                r"(c\.)\s*(\d+)\s*([ACGTacgt])\s*>\s*([ACGTacgt])",
                r"\1\2\3>\4",
                text
            )            # 3b) Normalizing p. patterns (e.g., p. Arg306 Cys -> p.Arg306Cys)
            text = re.sub(
                r"(p\.)\s*([A-Za-z]+)\s*(\d+)\s*([A-Za-z]+)",
                r"\1\2\3\4",
                text
            )

            # 3c) Collapsing single-letter amino-acid changes (e.g., R 306 C -> R306C)
            text = re.sub(
                r"\b([A-Za-z])\s*(\d+)\s*([A-Za-z])\b",
                r"\1\2\3",
                text
            )

            # 3d) Normalize reference sequences like NM_ or NP_ (e.g., N M_ 123. 4 -> NM_123.4)
            text = re.sub(
                r"(N[M|P]_)\s*([0-9]+)\s*\.\s*([0-9]+)",
                r"\1\2.\3",
                text
            )

            # 3e) Add a missing dot if we see "c" directly followed by digits and variant pattern
            text = re.sub(
                r"\bc(\d+[ACGTacgt]\s*>\s*[ACGTacgt])",
                r"c.\1",
                text
            )

            # 3f) Remove extraneous spaces after "c." (e.g., "c.  123A>G" -> "c.123A>G")
            text = re.sub(
                r"(c\.)\s+(\d)",
                r"\1\2",
                text
            )

            # 3g) Convert "->" to ">" if flanked by nucleotides (e.g., "A -> T" -> "A>T")
            text = re.sub(
                r"([ACGTacgt])\s*->\s*([ACGTacgt])",
                r"\1>\2",
                text
            )

            # 5) Convert "473C-T" -> "c.473C>T"
            text = re.sub(
                r"\b(\d+)([ACGTacgt])\s*-\s*([ACGTacgt])\b",
                r"c.\1\2>\3",
                text
            )

            # Pattern for 3-4 digits followed by nucleotide change
            text = re.sub(
                r"\b(\d{3,4})\s*([ACGTacgt])\s*>\s*([ACGTacgt])\b",
                r"\1\2>\3",
                text
            )

            # Add "c." prefix if missing for nucleotide changes
            text = re.sub(
                r"(?<!c\.)\b(\d{3,4})([ACGTacgt])>([ACGTacgt])\b",
                r"c.\1\2>\3",
                text
            )

            return text

        except Exception as e:
            logger.warning(f"Text cleaning failed, returning original text: {e}")
            return raw_text

    def detect_mecp2_keywords(self, text: str) -> List[Keyword]:
        """
        Looks for MECP2 gene mentions and common variant patterns within the cleaned text.
        Returns a single list of unique Keyword models, with counts for repeated occurrences.

        Args:
            text (str): Cleaned text to analyze

        Returns:
            List[Keyword]: List of detected keywords with their types and counts
        """
        try:
            detected_keywords = []
            logger.debug("Detecting MECP2 keywords and variants")            # 1. Detect "MECP2" (case-insensitive)
            mecp2_mentions = re.findall(r"\bMECP2\b", text, flags=re.IGNORECASE)
            mecp2_count = len(mecp2_mentions)
            if mecp2_count > 0:
                detected_keywords.append(Keyword(value="MECP2", type="gene_name", count=mecp2_count))

            # 2. Detect c. variants: e.g., "c.1035A>G" or "c.[473C>T]"
            variants_c = re.findall(r"(c\.\[?\d+[ACGTacgt>]+\]?)", text)
            variants_c_counter = Counter(variants_c)
            detected_keywords.extend(
                [Keyword(value=variant, type="variant_c", count=count) 
                 for variant, count in variants_c_counter.items()]
            )

            # 2a. Detect c. variants with deletion: e.g., "c.1040_1047del"
            variants_c_del = re.findall(r"(c\.\d+_\d+del)", text)
            variants_c_del_counter = Counter(variants_c_del)
            detected_keywords.extend(
                [Keyword(value=variant, type="variant_c", count=count) 
                 for variant, count in variants_c_del_counter.items()]
            )

            # 3. Detect p. variants: e.g., "p.Arg306Cys" or "p.[Thr158Met]"
            variants_p = re.findall(r"(p\.\[?[A-Za-z]{1,3}\d+[A-Za-z]{1,3}\]?)", text)
            variants_p_counter = Counter(variants_p)
            detected_keywords.extend(
                [Keyword(value=variant, type="variant_p", count=count) 
                 for variant, count in variants_p_counter.items()]
            )

            # 4. Detect reference sequences like NM_####.# or NP_####.#
            refs = re.findall(r"(NM_\d+|NP_\d+)", text)
            refs_counter = Counter(refs)
            detected_keywords.extend(
                [Keyword(value=ref, type="reference_sequence", count=count) 
                 for ref, count in refs_counter.items()]
            )

            # 4a. Detect reference sequences like NM_######
            refs_no_version = re.findall(r"(NM_\d+|NP_\d+)", text)
            refs_no_version_counter = Counter(refs_no_version)
            detected_keywords.extend(
                [Keyword(value=ref, type="reference_sequence", count=count) 
                 for ref, count in refs_no_version_counter.items()]
            )

            logger.debug(f"Detected {len(detected_keywords)} unique keywords")
            return detected_keywords

        except Exception as e:
            logger.warning(f"Keyword detection failed: {e}")
            return []

    def _validate_keyword_confidence(self, document: Document) -> None:
        """
        Validate OCR confidence scores for detected keywords.
        Updates the confidence scores in the keyword objects.

        Args:
            document (Document): Document with keywords to validate

        Raises:
            OcrConfidenceError: If confidence validation fails critically
        """
        try:
            logger.debug("Validating OCR confidence for detected keywords")

            for keyword in document.keywords:
                confidence_value = document.find_word_confidence(keyword.value)
                if confidence_value is not None:
                    logger.debug(f"Found {keyword} with confidence {confidence_value}")
                    keyword.confidence = confidence_value
                else:
                    logger.warning(f"{keyword} was not found in OCR results")
                    keyword.confidence = 0.0

            logger.debug(f"MECP2 keyword confidence validation completed: {document.keywords}")

        except Exception as e:
            # Don't fail the entire process for confidence validation issues
            logger.error(f"Confidence validation failed: {e}")
            # Set all confidences to 0.0 as fallback
            for keyword in document.keywords:
                keyword.confidence = 0.0
