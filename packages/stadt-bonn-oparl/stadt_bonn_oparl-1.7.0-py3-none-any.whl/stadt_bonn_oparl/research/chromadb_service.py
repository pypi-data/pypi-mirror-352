"""ChromaDB service for research operations."""

from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings

import logfire


class ChromaDBResearchService:
    """Service for accessing ChromaDB collections for research purposes."""

    def __init__(self, persist_directory: str = "chromadb/api"):
        """Initialize ChromaDB research service.

        Args:
            persist_directory: Directory for ChromaDB persistence
        """
        self.client = chromadb.PersistentClient(
            settings=Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False,
            )
        )

        # Get or create research-specific collections
        self.papers_collection = self.client.get_or_create_collection(name="papers")
        self.organizations_collection = self.client.get_or_create_collection(name="organizations")
        self.persons_collection = self.client.get_or_create_collection(name="persons")
        self.meetings_collection = self.client.get_or_create_collection(name="meetings")
        self.agendaitems_collection = self.client.get_or_create_collection(name="agendaitems")

    async def search_papers(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Search for papers using semantic search.

        Args:
            query: Search query
            n_results: Maximum number of results

        Returns:
            List of matching papers
        """
        try:
            results = self.papers_collection.query(query_texts=[query], n_results=n_results, include=["documents", "metadatas"])

            papers = []
            if results.get("ids") and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    paper_data = {
                        "id": doc_id,
                        "document": results.get("documents", [[]])[0][i] if results.get("documents") else None,
                        "metadata": results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {},
                    }
                    papers.append(paper_data)

            logfire.info(f"Found {len(papers)} papers for query: {query}")
            return papers

        except Exception as e:
            logfire.error(f"Error searching papers: {e}")
            return []

    async def search_organizations(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Search for organizations using semantic search.

        Args:
            query: Search query
            n_results: Maximum number of results

        Returns:
            List of matching organizations
        """
        try:
            results = self.organizations_collection.query(
                query_texts=[query], n_results=n_results, include=["documents", "metadatas"]
            )

            orgs = []
            if results.get("ids") and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    org_data = {
                        "id": doc_id,
                        "document": results.get("documents", [[]])[0][i] if results.get("documents") else None,
                        "metadata": results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {},
                    }
                    orgs.append(org_data)

            logfire.info(f"Found {len(orgs)} organizations for query: {query}")
            return orgs

        except Exception as e:
            logfire.error(f"Error searching organizations: {e}")
            return []

    async def search_persons(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Search for persons using semantic search.

        Args:
            query: Search query
            n_results: Maximum number of results

        Returns:
            List of matching persons
        """
        try:
            results = self.persons_collection.query(
                query_texts=[query], n_results=n_results, include=["documents", "metadatas"]
            )

            persons = []
            if results.get("ids") and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    person_data = {
                        "id": doc_id,
                        "document": results.get("documents", [[]])[0][i] if results.get("documents") else None,
                        "metadata": results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {},
                    }
                    persons.append(person_data)

            logfire.info(f"Found {len(persons)} persons for query: {query}")
            return persons

        except Exception as e:
            logfire.error(f"Error searching persons: {e}")
            return []

    async def search_all_collections(self, query: str, n_results: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Search across all collections for comprehensive results.

        Args:
            query: Search query
            n_results: Maximum number of results per collection

        Returns:
            Dictionary with results from all collections
        """
        results = {
            "papers": await self.search_papers(query, n_results),
            "organizations": await self.search_organizations(query, n_results),
            "persons": await self.search_persons(query, n_results),
        }

        total_results = sum(len(collection_results) for collection_results in results.values())
        logfire.info(f"Cross-collection search for '{query}' returned {total_results} total results")

        return results

    def get_collection_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all collections.

        Returns:
            Dictionary with collection statistics
        """
        info = {}
        collections = [
            ("papers", self.papers_collection),
            ("organizations", self.organizations_collection),
            ("persons", self.persons_collection),
            ("meetings", self.meetings_collection),
            ("agendaitems", self.agendaitems_collection),
        ]

        for name, collection in collections:
            try:
                count = collection.count()
                info[name] = {"count": count, "status": "OK"}
            except Exception as e:
                info[name] = {"count": 0, "status": f"ERROR: {e}"}

        return info
