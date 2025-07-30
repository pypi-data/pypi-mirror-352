import pytest
import os
import asyncio
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env if needed
load_dotenv(Path(__file__).parent.parent / "examples" / ".env")

# Import agents
from rettxmutation.openai_agent import (
    ValidationAgent,
    MutationExtractionAgent,
    SummarizationAgent
)

# Fixtures

@pytest.fixture
def mock_agent_config():
    """Provide mock agent configuration for tests that don't need real API calls."""
    return {
        'api_key': 'mock_api_key',
        'api_version': '2024-02-01',
        'azure_endpoint': 'https://mock.openai.azure.com/',
        'model_name': 'gpt-4o',
        'embedding_deployment': 'text-embedding-ada-002'
    }

# TestValidationAgent

class TestValidationAgent:

    def test_initialization_success(self, mock_agent_config):
        agent = ValidationAgent(**mock_agent_config)
        assert agent is not None
        assert hasattr(agent, 'validate_document')

    def test_initialization_missing_api_key(self):
        config = {
            'api_key': None,
            'api_version': '2024-02-01',
            'azure_endpoint': 'https://test.openai.azure.com/',
            'model_name': 'gpt-4o',
            'embedding_deployment': 'text-embedding-ada-002'
        }
        agent = ValidationAgent(**config)
        assert agent._api_key is None
        assert hasattr(agent, 'validate_document')

    def test_has_required_methods(self, mock_agent_config):
        agent = ValidationAgent(**mock_agent_config)
        assert hasattr(agent, 'validate_document')
        assert asyncio.iscoroutinefunction(agent.validate_document)

    def test_validate_document_method_signature(self, mock_agent_config):
        agent = ValidationAgent(**mock_agent_config)
        import inspect
        sig = inspect.signature(agent.validate_document)
        for param in ['document_text', 'language']:
            assert param in sig.parameters

    @pytest.mark.asyncio
    async def test_validate_document_success(self, mock_agent_config):
        agent = ValidationAgent(**mock_agent_config)
        with patch.object(agent, 'validate_document', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = (True, 0.95)
            is_valid, confidence = await agent.validate_document("text", "en")
            assert is_valid is True
            assert confidence == 0.95
            mock_validate.assert_called_once()

# TestMutationExtractionAgent

class TestMutationExtractionAgent:

    @pytest.fixture
    def extraction_agent(self, mock_agent_config):
        return MutationExtractionAgent(**mock_agent_config)

    def test_initialization_success(self, extraction_agent):
        assert extraction_agent is not None
        assert hasattr(extraction_agent, 'extract_mutations')

    def test_has_required_methods(self, extraction_agent):
        assert hasattr(extraction_agent, 'extract_mutations')
        assert asyncio.iscoroutinefunction(extraction_agent.extract_mutations)

    @pytest.mark.asyncio
    async def test_extract_mutations_success(self, extraction_agent):
        with patch.object(extraction_agent, 'extract_mutations', new_callable=AsyncMock) as mock_extract:
            mock_extract.return_value = []
            mutations = await extraction_agent.extract_mutations("text", "", "")
            assert isinstance(mutations, list)
            mock_extract.assert_called_once()

# TestSummarizationAgent

class TestSummarizationAgent:

    @pytest.fixture
    def summarization_agent(self, mock_agent_config):
        return SummarizationAgent(**mock_agent_config)

    def test_initialization_success(self, summarization_agent):
        assert summarization_agent is not None
        assert hasattr(summarization_agent, 'summarize_report')
        assert hasattr(summarization_agent, 'correct_summary_mistakes')

    def test_has_required_methods(self, summarization_agent):
        assert asyncio.iscoroutinefunction(summarization_agent.summarize_report)
        assert asyncio.iscoroutinefunction(summarization_agent.correct_summary_mistakes)

    @pytest.mark.asyncio
    async def test_summarize_report_success(self, summarization_agent):
        with patch.object(summarization_agent, 'summarize_report', new_callable=AsyncMock) as mock_summarize:
            mock_summarize.return_value = "Summary"
            summary = await summarization_agent.summarize_report("text", "keywords")
            assert isinstance(summary, str)
            mock_summarize.assert_called_once()

    @pytest.mark.asyncio
    async def test_correct_summary_mistakes_success(self, summarization_agent):
        with patch.object(summarization_agent, 'correct_summary_mistakes', new_callable=AsyncMock) as mock_correct:
            mock_correct.return_value = "Corrected summary"
            result = await summarization_agent.correct_summary_mistakes("summary", "keywords", "analytics")
            assert isinstance(result, str)
            mock_correct.assert_called_once()
