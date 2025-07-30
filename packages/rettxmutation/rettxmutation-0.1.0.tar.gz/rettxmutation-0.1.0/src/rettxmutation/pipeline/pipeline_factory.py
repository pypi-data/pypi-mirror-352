"""
RettX Pipeline Factory

Provides helper functions to create fully configured pipeline instances.
"""

import logging
from rettxmutation.pipeline.rettx_pipeline import RettxPipeline
from rettxmutation.pipeline.config_types import RettxPipelineConfig
from rettxmutation.ocr import OcrTextProcessor
from rettxmutation.openai_agent import ValidationAgent, MutationExtractionAgent, SummarizationAgent
from rettxmutation.services.text_analytics import HealthcareTextAnalyzer

logger = logging.getLogger(__name__)

def create_default_pipeline(config: RettxPipelineConfig) -> RettxPipeline:
    """
    Creates a fully configured RettXPipeline (with all agents).

    Args:
    config: An object with the following attributes:
        - RETTX_DOCUMENT_ANALYSIS_ENDPOINT
        - RETTX_DOCUMENT_ANALYSIS_KEY
        - RETTX_OPENAI_KEY
        - RETTX_OPENAI_MODEL_VERSION
        - RETTX_OPENAI_ENDPOINT
        - RETTX_OPENAI_MODEL_NAME
        - RETTX_EMBEDDING_DEPLOYMENT
    Optional:
        - RETTX_COGNITIVE_SERVICES_ENDPOINT (if using text analytics)
        - RETTX_COGNITIVE_SERVICES_KEY (if using text analytics)
        - RETTX_AI_SEARCH_SERVICE (if using AI search)

    Returns:
        RettxPipeline
    """
    logger.info("🔧 Creating default RettX pipeline")

    # Initialize OCR processor
    ocr_processor = OcrTextProcessor(
        doc_analysis_endpoint=config.RETTX_DOCUMENT_ANALYSIS_ENDPOINT,
        doc_analysis_key=config.RETTX_DOCUMENT_ANALYSIS_KEY
    )

    # Shared agent config
    agent_config = {
        'api_key': config.RETTX_OPENAI_KEY,
        'api_version': config.RETTX_OPENAI_MODEL_VERSION,
        'azure_endpoint': config.RETTX_OPENAI_ENDPOINT,
        'model_name': config.RETTX_OPENAI_MODEL_NAME,
        'embedding_deployment': config.RETTX_EMBEDDING_DEPLOYMENT
    }

    # Initialize agents
    validation_agent = ValidationAgent(**agent_config)
    extraction_agent = MutationExtractionAgent(**agent_config)
    summarization_agent = SummarizationAgent(**agent_config)

    # Add optional cognitive services and AI search services if provided
    if hasattr(config, 'RETTX_COGNITIVE_SERVICES_ENDPOINT') and config.RETTX_COGNITIVE_SERVICES_ENDPOINT:
        text_analytics_service = HealthcareTextAnalyzer(
            endpoint=config.RETTX_COGNITIVE_SERVICES_ENDPOINT,
            key=config.RETTX_COGNITIVE_SERVICES_KEY
        )
    else:
        text_analytics_service = None

    if hasattr(config, 'RETTX_AI_SEARCH_SERVICE') and config.RETTX_AI_SEARCH_SERVICE:
        ai_search_service = config.RETTX_AI_SEARCH_SERVICE
    else:
        ai_search_service = None

    # Build pipeline
    pipeline = RettxPipeline(
        ocr_processor=ocr_processor,
        validation_agent=validation_agent,
        extraction_agent=extraction_agent,
        summarization_agent=summarization_agent,
        text_analytics_service=text_analytics_service,
        ai_search_service=ai_search_service
    )

    logger.info("✅ Default RettX pipeline created")

    return pipeline
