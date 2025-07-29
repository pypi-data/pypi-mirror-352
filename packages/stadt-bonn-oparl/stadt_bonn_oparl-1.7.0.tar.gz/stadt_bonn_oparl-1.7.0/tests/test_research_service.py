"""Tests for the research service module."""

import pytest
from datetime import datetime

from stadt_bonn_oparl.research import ResearchService, ComprehensiveResearchResult
from stadt_bonn_oparl.research.models import DocumentType


class TestResearchService:
    """Test cases for ResearchService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.research_service = ResearchService()
    
    @pytest.mark.asyncio
    async def test_research_topic_comprehensive_basic(self):
        """Test basic comprehensive topic research."""
        result = await self.research_service.research_topic_comprehensive(
            subject="Klimaschutz",
            max_documents=10
        )
        
        assert isinstance(result, ComprehensiveResearchResult)
        assert result.subject == "Klimaschutz"
        assert result.research_timestamp is not None
        assert isinstance(result.research_timestamp, datetime)
        assert result.executive_summary is not None
        assert result.confidence_score >= 0.0
        assert result.confidence_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_research_topic_comprehensive_with_options(self):
        """Test comprehensive research with various options."""
        result = await self.research_service.research_topic_comprehensive(
            subject="Radverkehr",
            time_period="2024",
            include_meetings=False,
            include_protocols=False,
            include_stakeholders=False,
            max_documents=5
        )
        
        assert result.subject == "Radverkehr"
        assert result.research_scope.include_meetings is False
        assert result.research_scope.include_stakeholders is False
        assert result.research_scope.max_documents == 5
    
    @pytest.mark.asyncio
    async def test_search_chromadb(self):
        """Test ChromaDB search."""
        result = await self.research_service._search_chromadb("test query", 10)
        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_search_oparl_api(self):
        """Test OParl API search."""
        result = await self.research_service._search_oparl_api("test query", 5)
        # Should return a list, might be empty if API is not available
        assert isinstance(result, list)
    
    def test_analyze_documents(self):
        """Test document analysis."""
        chromadb_results = {
            "papers": [{"id": "1", "content": "test"}],
            "organizations": [],
            "persons": []
        }
        oparl_results = [{"id": "2", "name": "Test Paper"}]
        
        analysis = self.research_service._analyze_documents(chromadb_results, oparl_results)
        
        assert analysis.total_documents == 2
        assert analysis.document_types[DocumentType.PAPER] == 2  # 1 from chromadb + 1 from oparl
        assert len(analysis.key_documents) <= 5
    
    def test_analyze_stakeholders(self):
        """Test stakeholder analysis."""
        analysis = self.research_service._analyze_stakeholders()
        
        # Should return a valid StakeholderAnalysis object
        assert analysis.key_persons == []
        assert analysis.organizations == []
        assert analysis.influence_network == {}