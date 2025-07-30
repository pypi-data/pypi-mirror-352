"""
Test suite for Pipeline components

Tests the RettxPipeline, pipeline factory, and pipeline integration.
"""

import pytest
import os
import asyncio
import io
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "examples" / ".env")

from rettxmutation.pipeline import (
    create_default_pipeline,
    RettxPipeline,
    RettxPipelineConfig
)
from rettxmutation.services.mutation_validator import MutationValidator
from rettxmutation.models.document import Document
from rettxmutation.models.gene_models import GeneMutation, RawMutation


class TestPipelineConfig:
    """Test cases for pipeline configuration."""
    
    @pytest.fixture
    def env_config(self):
        """Create configuration from environment variables."""
        class EnvConfig:
            def __init__(self):
                self.RETTX_DOCUMENT_ANALYSIS_ENDPOINT = os.getenv('RETTX_DOCUMENT_ANALYSIS_ENDPOINT')
                self.RETTX_DOCUMENT_ANALYSIS_KEY = os.getenv('RETTX_DOCUMENT_ANALYSIS_KEY')
                self.RETTX_OPENAI_KEY = os.getenv('RETTX_OPENAI_KEY')
                self.RETTX_OPENAI_MODEL_VERSION = os.getenv('RETTX_OPENAI_MODEL_VERSION', '2024-02-01')
                self.RETTX_OPENAI_ENDPOINT = os.getenv('RETTX_OPENAI_ENDPOINT')
                self.RETTX_OPENAI_MODEL_NAME = os.getenv('RETTX_OPENAI_MODEL_NAME', 'gpt-4o')
                self.RETTX_EMBEDDING_DEPLOYMENT = os.getenv('RETTX_EMBEDDING_DEPLOYMENT', 'text-embedding-ada-002')
        return EnvConfig()
    
    def test_config_has_required_attributes(self, env_config):
        """Test that configuration has all required attributes."""
        required_attrs = [
            'RETTX_DOCUMENT_ANALYSIS_ENDPOINT',
            'RETTX_DOCUMENT_ANALYSIS_KEY',
            'RETTX_OPENAI_KEY',
            'RETTX_OPENAI_MODEL_VERSION',
            'RETTX_OPENAI_ENDPOINT',
            'RETTX_OPENAI_MODEL_NAME',
            'RETTX_EMBEDDING_DEPLOYMENT'
        ]
        
        for attr in required_attrs:
            assert hasattr(env_config, attr), f"Missing configuration attribute: {attr}"
    
    def test_config_validation(self, env_config):
        """Test configuration validation."""
        # Test that critical values are not None (if environment is configured)
        if env_config.RETTX_OPENAI_KEY and env_config.RETTX_OPENAI_KEY != 'test_key':
            assert env_config.RETTX_OPENAI_KEY is not None
            assert env_config.RETTX_OPENAI_ENDPOINT is not None
            assert len(env_config.RETTX_OPENAI_KEY) > 10  # Basic validation


class TestRettxPipeline:
    """Test cases for RettxPipeline."""
    
    @pytest.fixture
    def mock_components(self):
        """Create mock pipeline components."""
        ocr_processor = Mock()
        validation_agent = Mock()
        extraction_agent = Mock()
        summarization_agent = Mock()
        mutation_validator = Mock()
        
        return {
            'ocr_processor': ocr_processor,
            'validation_agent': validation_agent,
            'extraction_agent': extraction_agent,
            'summarization_agent': summarization_agent,
            'mutation_validator': mutation_validator
        }
    
    @pytest.fixture
    def pipeline(self, mock_components):
        """Create pipeline with mock components."""
        return RettxPipeline(**mock_components)
    def test_pipeline_initialization(self, mock_components):
        """Test pipeline initialization with components."""
        pipeline = RettxPipeline(**mock_components)
        
        assert pipeline.ocr_processor is mock_components['ocr_processor']
        assert pipeline.validation_agent is mock_components['validation_agent']
        assert pipeline.extraction_agent is mock_components['extraction_agent']
        assert pipeline.summarization_agent is mock_components['summarization_agent']
        assert pipeline.mutation_validator is mock_components['mutation_validator']
    
    def test_pipeline_has_required_methods(self, pipeline):
        """Test that pipeline has all required methods."""
        assert hasattr(pipeline, 'run_pipeline')
        assert hasattr(pipeline, '_build_text_analytics_summary')
        assert hasattr(pipeline, 'close')
        
        # Check that run_pipeline is async
        assert asyncio.iscoroutinefunction(pipeline.run_pipeline)
    
    def test_build_text_analytics_summary_empty(self, pipeline):
        """Test _build_text_analytics_summary with empty mutations."""
        summary = pipeline._build_text_analytics_summary([])
        assert "No mutations detected" in summary
    
    def test_build_text_analytics_summary_with_mutations(self, pipeline):
        """Test _build_text_analytics_summary with mutations."""
        class MockMutation:
            def __init__(self, mutation, confidence):
                self.mutation = mutation
                self.confidence = confidence
        
        mutations = [
            MockMutation("c.916C>T", 0.95),
            MockMutation("p.Arg306Cys", 0.90)
        ]
        
        summary = pipeline._build_text_analytics_summary(mutations)
        assert "High confidence mutations detected" in summary
        assert "c.916C>T" in summary
        assert "p.Arg306Cys" in summary
        assert "0.95" in summary
        assert "0.90" in summary
    
    @pytest.mark.asyncio
    async def test_run_pipeline_success(self, pipeline, mock_components):
        """Test successful pipeline execution."""
        # Mock document from OCR
        mock_document = Mock(spec=Document)
        mock_document.cleaned_text = "Medical report with MECP2 mutation c.916C>T."
        mock_document.language = "en"
        mock_document.dump_keywords.return_value = "MECP2, c.916C>T"
        mock_document.dump_text_analytics_keywords.return_value = "MECP2 (gene), c.916C>T (mutation)"
        
        # Mock raw mutations from extraction
        mock_raw_mutations = [
            Mock(spec=RawMutation, mutation="NM_004992.4:c.916C>T", confidence=0.95)
        ]
        
        # Mock validated GeneMutation objects
        mock_gene_mutation = Mock(spec=GeneMutation)
        mock_gene_mutation.variant_type = "SNV"
        mock_gene_mutation.primary_transcript = Mock()
        mock_gene_mutation.primary_transcript.hgvs_transcript_variant = "NM_004992.4:c.916C>T"
        mock_validated_mutations = [mock_gene_mutation]
        
        # Set up mocks
        mock_components['ocr_processor'].extract_and_process_text.return_value = mock_document
        mock_components['validation_agent'].validate_document = AsyncMock(return_value=(True, 0.95))
        mock_components['extraction_agent'].extract_mutations = AsyncMock(return_value=mock_raw_mutations)
        mock_components['mutation_validator'].validate_mutations = AsyncMock(return_value=mock_validated_mutations)
        
        # Run pipeline
        mock_file = io.BytesIO(b"mock file content")
        document, validated_mutations = await pipeline.run_pipeline(mock_file)

        # Verify result structure - now returns tuple instead of dict
        assert isinstance(document, Mock)  # Should be Document object
        assert isinstance(validated_mutations, list)
        assert len(validated_mutations) == 1
        assert validated_mutations[0] is mock_gene_mutation
        
        # Verify mocks were called correctly
        mock_components['ocr_processor'].extract_and_process_text.assert_called_once()
        mock_components['validation_agent'].validate_document.assert_called_once()
        mock_components['extraction_agent'].extract_mutations.assert_called_once()
        mock_components['mutation_validator'].validate_mutations.assert_called_once_with(
            raw_mutations=mock_raw_mutations
        )
    
    @pytest.mark.asyncio
    async def test_run_pipeline_validation_failure(self, pipeline, mock_components):
        """Test pipeline execution when validation fails."""
        # Mock document from OCR
        mock_document = Mock()
        mock_document.cleaned_text = "Not a medical report"
        
        # Set up mocks - validation fails
        mock_components['ocr_processor'].extract_and_process_text.return_value = mock_document
        mock_components['validation_agent'].validate_document = AsyncMock(return_value=(False, 0.20))
        
        # Run pipeline and expect exception
        mock_file = io.BytesIO(b"mock file content")
        
        with pytest.raises(Exception) as exc_info:
            await pipeline.run_pipeline(mock_file)
        
        assert "Document failed validation" in str(exc_info.value)
        assert "confidence=0.20" in str(exc_info.value)
    

class TestPipelineFactory:
    """Test cases for pipeline factory functions."""
    
    @pytest.fixture
    def config(self):
        """Provide test configuration."""
        class TestConfig:
            RETTX_DOCUMENT_ANALYSIS_ENDPOINT = os.getenv('RETTX_DOCUMENT_ANALYSIS_ENDPOINT', 'https://test.cognitiveservices.azure.com/')
            RETTX_DOCUMENT_ANALYSIS_KEY = os.getenv('RETTX_DOCUMENT_ANALYSIS_KEY', 'test_key')
            RETTX_OPENAI_KEY = os.getenv('RETTX_OPENAI_KEY', 'test_key')
            RETTX_OPENAI_MODEL_VERSION = os.getenv('RETTX_OPENAI_MODEL_VERSION', '2024-02-01')
            RETTX_OPENAI_ENDPOINT = os.getenv('RETTX_OPENAI_ENDPOINT', 'https://test.openai.azure.com/')
            RETTX_OPENAI_MODEL_NAME = os.getenv('RETTX_OPENAI_MODEL_NAME', 'gpt-4o')
            RETTX_EMBEDDING_DEPLOYMENT = os.getenv('RETTX_EMBEDDING_DEPLOYMENT', 'text-embedding-ada-002')
        return TestConfig()
    
    def test_create_default_pipeline_success(self, config):
        """Test successful creation of default pipeline."""
        pipeline = create_default_pipeline(config)
        
        assert isinstance(pipeline, RettxPipeline)
        assert pipeline.ocr_processor is not None
        assert pipeline.validation_agent is not None
        assert pipeline.extraction_agent is not None
        assert pipeline.summarization_agent is not None
        assert pipeline.mutation_validator is not None

    def test_create_default_pipeline_invalid_config(self):
        """Test pipeline creation with invalid configuration."""
        from rettxmutation.ocr.exceptions import OcrExtractionError
        
        class InvalidConfig:
            RETTX_DOCUMENT_ANALYSIS_ENDPOINT = None
            RETTX_DOCUMENT_ANALYSIS_KEY = None
            RETTX_OPENAI_KEY = None
            RETTX_OPENAI_MODEL_VERSION = None
            RETTX_OPENAI_ENDPOINT = None
            RETTX_OPENAI_MODEL_NAME = None
            RETTX_EMBEDDING_DEPLOYMENT = None
        
        # This might still create the pipeline but components will fail on usage
        # The exact behavior depends on the implementation
        with pytest.raises((ValueError, TypeError, AttributeError, OcrExtractionError)):
            create_default_pipeline(InvalidConfig())
    
    def test_pipeline_components_are_properly_configured(self, config):
        """Test that pipeline components are properly configured."""
        pipeline = create_default_pipeline(config)
        
        # Verify OCR processor has correct configuration
        assert hasattr(pipeline.ocr_processor, 'extract_and_process_text')
        
        # Verify agents have required methods
        assert hasattr(pipeline.validation_agent, 'validate_document')
        assert hasattr(pipeline.extraction_agent, 'extract_mutations')
        assert hasattr(pipeline.summarization_agent, 'summarize_report')
        assert hasattr(pipeline.summarization_agent, 'correct_summary_mistakes')


class TestPipelineIntegration:
    """Integration tests for the complete pipeline."""
    
    @pytest.fixture
    def config(self):
        """Provide test configuration."""
        class TestConfig:
            RETTX_DOCUMENT_ANALYSIS_ENDPOINT = os.getenv('RETTX_DOCUMENT_ANALYSIS_ENDPOINT')
            RETTX_DOCUMENT_ANALYSIS_KEY = os.getenv('RETTX_DOCUMENT_ANALYSIS_KEY')
            RETTX_OPENAI_KEY = os.getenv('RETTX_OPENAI_KEY')
            RETTX_OPENAI_MODEL_VERSION = os.getenv('RETTX_OPENAI_MODEL_VERSION', '2024-02-01')
            RETTX_OPENAI_ENDPOINT = os.getenv('RETTX_OPENAI_ENDPOINT')
            RETTX_OPENAI_MODEL_NAME = os.getenv('RETTX_OPENAI_MODEL_NAME', 'gpt-4o')
            RETTX_EMBEDDING_DEPLOYMENT = os.getenv('RETTX_EMBEDDING_DEPLOYMENT', 'text-embedding-ada-002')
        return TestConfig()
    
    def test_end_to_end_pipeline_creation(self, config):
        """Test end-to-end pipeline creation and structure."""
        # Skip if no configuration available
        if not config.RETTX_OPENAI_KEY or config.RETTX_OPENAI_KEY == 'test_key':
            pytest.skip("No API configuration available")
        
        pipeline = create_default_pipeline(config)
        
        # Verify pipeline structure
        assert isinstance(pipeline, RettxPipeline)
        assert pipeline.ocr_processor is not None
        assert pipeline.validation_agent is not None
        assert pipeline.extraction_agent is not None
        assert pipeline.summarization_agent is not None
        
        # Verify pipeline methods
        assert hasattr(pipeline, 'run_pipeline')
        assert asyncio.iscoroutinefunction(pipeline.run_pipeline)
    
    @pytest.mark.asyncio
    async def test_mock_pipeline_workflow(self, config):
        """Test complete pipeline workflow with mocked components."""
        # Skip if no configuration available
        if not config.RETTX_OPENAI_KEY:
            pytest.skip("No API configuration available")
        
        pipeline = create_default_pipeline(config)
          # Mock all the async calls to avoid actual API usage
        with patch.object(pipeline.ocr_processor, 'extract_and_process_text') as mock_ocr, \
             patch.object(pipeline.validation_agent, 'validate_document', new_callable=AsyncMock) as mock_validate, \
             patch.object(pipeline.extraction_agent, 'extract_mutations', new_callable=AsyncMock) as mock_extract, \
             patch.object(pipeline.mutation_validator, 'validate_mutations', new_callable=AsyncMock) as mock_mutation_validator, \
             patch.object(pipeline.summarization_agent, 'summarize_report', new_callable=AsyncMock) as mock_summarize, \
             patch.object(pipeline.summarization_agent, 'correct_summary_mistakes', new_callable=AsyncMock) as mock_correct:
            
            # Set up mock returns
            mock_document = Mock(spec=Document)
            mock_document.cleaned_text = "Patient report with MECP2 mutation c.916C>T."
            mock_document.language = "en"
            mock_document.dump_keywords.return_value = "MECP2, c.916C>T"
            mock_document.dump_text_analytics_keywords.return_value = "MECP2 (gene), c.916C>T (mutation)"
            
            class MockRawMutation:
                def __init__(self, mutation, confidence):
                    self.mutation = mutation
                    self.confidence = confidence
                def model_dump(self):
                    return {'mutation': self.mutation, 'confidence': self.confidence}
            
            # Mock validated GeneMutation objects
            mock_gene_mutation = Mock(spec=GeneMutation)
            mock_gene_mutation.variant_type = "SNV"
            mock_gene_mutation.primary_transcript = Mock()
            mock_gene_mutation.primary_transcript.hgvs_transcript_variant = "NM_004992.4:c.916C>T"
            
            mock_ocr.return_value = mock_document
            mock_validate.return_value = (True, 0.95)
            mock_extract.return_value = [MockRawMutation("c.916C>T", 0.95)]
            mock_mutation_validator.return_value = [mock_gene_mutation]
            mock_summarize.return_value = "Patient has MECP2 mutation."
            mock_correct.return_value = "Patient has MECP2 mutation c.916C>T (p.Arg306Cys)."
            
            # Run the pipeline
            mock_file = io.BytesIO(b"mock medical report pdf")
            document, validated_mutations = await pipeline.run_pipeline(mock_file)
            
            # Verify the workflow was executed
            mock_ocr.assert_called_once()
            mock_validate.assert_called_once_with("Patient report with MECP2 mutation c.916C>T.", "en")
            mock_extract.assert_called_once()
            mock_mutation_validator.assert_called_once()
            # Note: summarization functionality is currently commented out
            # mock_summarize.assert_called_once()
            # mock_correct.assert_called_once()
            
            # Verify the result - now returns tuple instead of dict
            assert isinstance(document, Mock)  # Should be Document object
            assert isinstance(validated_mutations, list)
            assert len(validated_mutations) == 1
            assert validated_mutations[0] is mock_gene_mutation
            # Note: summary functionality is currently commented out
            # assert "MECP2" in result['summary']
            # assert "c.916C>T" in result['corrected_summary']


if __name__ == "__main__":
    pytest.main([__file__])
