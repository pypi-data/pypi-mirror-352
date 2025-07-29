"""Core research service for orchestrating comprehensive municipal topic analysis."""

import asyncio
from datetime import datetime
from typing import List, Optional

import logfire

from stadt_bonn_oparl.oparl_fetcher import get_oparl_list_data

from .chromadb_service import ChromaDBResearchService
from .analyzers.stakeholder_tracker import StakeholderTracker

from .models import (
    ComprehensiveResearchResult,
    DocumentAnalysis,
    DocumentType,
    ResearchScope,
    SourceSummary,
    StakeholderAnalysis,
)


class ResearchService:
    """Core service for orchestrating comprehensive municipal research."""

    def __init__(self, chromadb_service: Optional[ChromaDBResearchService] = None):
        """Initialize the research service.

        Args:
            chromadb_service: Optional ChromaDB research service instance
        """
        self.chromadb_service = chromadb_service or ChromaDBResearchService()
        self.stakeholder_tracker = StakeholderTracker()

    async def research_topic_comprehensive(
        self,
        subject: str,
        time_period: Optional[str] = None,
        include_meetings: bool = True,
        include_protocols: bool = True,
        include_stakeholders: bool = True,
        max_documents: int = 50,
    ) -> ComprehensiveResearchResult:
        """Perform comprehensive research on a municipal topic.

        Args:
            subject: The topic to research (e.g., "Radverkehr", "Klimaschutz")
            time_period: Optional time period filter ("2024", "last_6_months", "2023-2024")
            include_meetings: Whether to analyze related meetings
            include_protocols: Whether to include meeting protocols
            include_stakeholders: Whether to perform stakeholder analysis
            max_documents: Maximum number of documents to analyze

        Returns:
            ComprehensiveResearchResult with complete analysis
        """
        logfire.info(f"Starting comprehensive research for topic: {subject}")

        # Create research scope
        research_scope = ResearchScope(
            document_types=[DocumentType.PAPER, DocumentType.MEETING_PROTOCOL, DocumentType.AGENDA_ITEM],
            include_meetings=include_meetings,
            include_stakeholders=include_stakeholders,
            max_documents=max_documents,
        )

        # Run parallel data collection
        chromadb_results, oparl_results = await asyncio.gather(
            self._search_chromadb(subject, max_documents),
            self._search_oparl_api(subject, max_documents),
            return_exceptions=True,
        )

        # Handle potential exceptions
        if isinstance(chromadb_results, Exception):
            logfire.warning(f"ChromaDB search failed: {chromadb_results}")
            chromadb_results = {}

        if isinstance(oparl_results, Exception):
            logfire.warning(f"OParl API search failed: {oparl_results}")
            oparl_results = []

        # Aggregate and analyze data (ensure chromadb_results is dict)
        chromadb_data = chromadb_results if isinstance(chromadb_results, dict) else {}
        document_analysis = self._analyze_documents(chromadb_data, oparl_results)
        
        # Enhanced stakeholder analysis
        if include_stakeholders:
            stakeholder_analysis = await self.stakeholder_tracker.create_stakeholder_map(subject)
        else:
            stakeholder_analysis = StakeholderAnalysis()

        # Generate executive summary (placeholder for now)
        executive_summary = f"Comprehensive analysis of '{subject}' covering {document_analysis.total_documents} documents."

        # Calculate total ChromaDB results
        chromadb_total = sum(len(results) for results in chromadb_data.values())

        # Create source summary
        source_summary = SourceSummary(
            total_sources=chromadb_total + len(oparl_results),
            oparl_documents=len(oparl_results),
            vector_db_results=chromadb_total,
            data_quality_score=0.8,  # Placeholder
        )

        result = ComprehensiveResearchResult(
            subject=subject,
            research_timestamp=datetime.now(),
            research_scope=research_scope,
            executive_summary=executive_summary,
            stakeholder_analysis=stakeholder_analysis,
            document_analysis=document_analysis,
            confidence_score=0.7,  # Placeholder
            data_completeness=0.8,  # Placeholder
            source_summary=source_summary,
        )

        logfire.info(f"Research completed for topic: {subject}")
        return result

    async def _search_chromadb(self, query: str, max_results: int) -> dict:
        """Search ChromaDB for relevant documents across all collections.

        Args:
            query: Search query
            max_results: Maximum number of results per collection

        Returns:
            Dictionary with results from all collections
        """
        try:
            logfire.info(f"Searching ChromaDB for: {query}")
            results = await self.chromadb_service.search_all_collections(
                query,
                n_results=max_results // 3,  # Distribute across collections
            )
            return results
        except Exception as e:
            logfire.error(f"ChromaDB search failed: {e}")
            return {}

    async def _search_oparl_api(self, query: str, max_results: int) -> List[dict]:
        """Search the OParl API for relevant documents.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of relevant documents from OParl API
        """
        try:
            logfire.info(f"Searching OParl API for: {query}")

            # Search papers first
            papers = await get_oparl_list_data("/papers", params={"limit": max_results})
            if papers is None:
                papers = []

            # For now, return the papers directly
            # In a real implementation, we would filter by relevance to the query
            return papers[:max_results]

        except Exception as e:
            logfire.error(f"OParl API search failed: {e}")
            return []

    def _analyze_documents(self, chromadb_results: dict, oparl_results: List[dict]) -> DocumentAnalysis:
        """Analyze the collected documents.

        Args:
            chromadb_results: Results from ChromaDB search
            oparl_results: Results from OParl API

        Returns:
            DocumentAnalysis with aggregated insights
        """
        # Calculate total documents
        chromadb_total = sum(len(results) for results in chromadb_results.values()) if isinstance(chromadb_results, dict) else 0
        total_documents = chromadb_total + len(oparl_results)

        # Count document types
        document_types = {
            DocumentType.PAPER: len(chromadb_results.get("papers", [])) + len(oparl_results),
            DocumentType.MEETING_PROTOCOL: 0,  # Not currently tracked
            DocumentType.AGENDA_ITEM: 0,  # Not currently tracked
        }

        # Collect key documents from all sources
        key_documents = []
        if isinstance(chromadb_results, dict):
            for collection_results in chromadb_results.values():
                key_documents.extend(collection_results[:2])  # Top 2 from each collection
        key_documents.extend(oparl_results[:3])  # Top 3 from OParl

        return DocumentAnalysis(
            total_documents=total_documents,
            document_types=document_types,
            key_documents=key_documents[:5],  # Limit to top 5
            trends=["Placeholder trend analysis"],
        )

    async def analyze_stakeholders_for_topic(self, topic: str, max_meetings: int = 20) -> StakeholderAnalysis:
        """Analyze stakeholders involved in a specific topic.

        Args:
            topic: The research topic
            max_meetings: Maximum number of meetings to analyze

        Returns:
            StakeholderAnalysis with identified stakeholders and relationships
        """
        return await self.stakeholder_tracker.create_stakeholder_map(topic, max_meetings)
