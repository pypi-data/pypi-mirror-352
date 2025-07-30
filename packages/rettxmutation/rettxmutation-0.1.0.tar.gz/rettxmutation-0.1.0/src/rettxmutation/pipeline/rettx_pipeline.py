"""
RettX Pipeline

Defines the standard RettXPipeline that orchestrates:
1️⃣ OCR
2️⃣ Document validation
3️⃣ Mutation extraction
4️⃣ Report summarization
5️⃣ Summary correction
"""

import logging
from rettxmutation.ocr import OcrTextProcessor
from rettxmutation.openai_agent import ValidationAgent, MutationExtractionAgent, SummarizationAgent

logger = logging.getLogger(__name__)

class RettxPipeline:
    """Standard RettX processing pipeline."""

    def __init__(
        self,
        ocr_processor: OcrTextProcessor,
        validation_agent: ValidationAgent,
        extraction_agent: MutationExtractionAgent,
        summarization_agent: SummarizationAgent,
        text_analytics_service=None,  # Optional
        ai_search_service=None  # Optional
    ):
        self.ocr_processor = ocr_processor
        self.validation_agent = validation_agent
        self.extraction_agent = extraction_agent
        self.summarization_agent = summarization_agent
        # Optional services
        self.text_analytics_service = text_analytics_service
        self.ai_search_service = ai_search_service

        logger.debug(f"{self.__class__.__name__} initialized")

    async def run_pipeline(self, file_stream, language="en") -> dict:
        """
        Full pipeline:
        - OCR → Validate → Extract Mutations → Summarize → Correct Summary

        Args:
            file_stream: File-like object containing the document
            language: Document language (default: "en")

        Returns:
            dict: Pipeline results
        """
        logger.info("🚀 Starting RettX pipeline")

        # 1️⃣ OCR
        logger.info("📝 Running OCR processing")
        document = self.ocr_processor.extract_and_process_text(file_stream)

        # 2️⃣ Validation
        logger.info("🔍 Running document validation")
        is_valid, validation_conf = await self.validation_agent.validate_document(
            document.cleaned_text, language
        )

        if not is_valid:
            raise Exception(f"Document failed validation (confidence={validation_conf:.2f})")

        if self.text_analytics_service:
            # Perform text analytics if service is available
            logger.info("🔍 Running text analytics")
            document.text_analytics_result = self.text_analytics_service.identify_genetic_variants(
                document.cleaned_text
            )
            logger.info(f"Text analytics result: {document.text_analytics_result}")        # 3️⃣ Mutation extraction
        logger.info("🧬 Running mutation extraction")
        mutations = await self.extraction_agent.extract_mutations(
            document.cleaned_text,
            document.dump_keywords(),
            document.dump_text_analytics_keywords()
        )

        # 4️⃣ Report summarization
        # logger.info("📝 Running report summarization")
        # summary = await self.summarization_agent.summarize_report(
        #     document.cleaned_text,
        #     document.dump_keywords()
        # )

        # 5️⃣ Summary correction
        # logger.info("✏️ Running summary correction")
        # text_analytics_summary = self._build_text_analytics_summary(mutations)

        # corrected_summary = await self.summarization_agent.correct_summary_mistakes(
        #     summary,
        #     document.dump_keywords(),
        #     text_analytics_summary
        # )

        # Build result object
        result = {
            "validation": {"is_valid": is_valid, "confidence": validation_conf},
            "mutations": [m.model_dump() for m in mutations],
            # "summary": summary,
            # "corrected_summary": corrected_summary
        }

        logger.info("✅ RettX pipeline completed successfully")

        return result

    def _build_text_analytics_summary(self, mutations):
        """Summarize mutations for correction step."""
        if not mutations:
            return "No mutations detected."
        else:
            lines = [
                f"{m.mutation} (confidence={m.confidence:.2f})"
                for m in mutations
            ]
            return "High confidence mutations detected: " + "; ".join(lines)
