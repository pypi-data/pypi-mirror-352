"""API client for interacting with the local OParl API server."""

import httpx
from loguru import logger
from typing import Optional


class OParlAPIClient:
    """Client for interacting with the local OParl API server."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the API client.

        Args:
            base_url: Base URL of the local API server
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(follow_redirects=True)

    def get_papers(self, page: int = 1, limit: int = 20) -> Optional[dict]:
        """Fetch papers through local API server.

        Args:
            page: Page number to fetch
            limit: Maximum number of papers per page

        Returns:
            Parsed JSON response or None if request fails
        """
        try:
            response = self.client.get(
                f"{self.base_url}/papers",
                params={"page": page, "limit": limit},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            logger.info(
                f"Successfully fetched {len(data.get('data', []))} papers from API server"
            )
            return data
        except httpx.RequestError as e:
            logger.error(f"Failed to fetch papers from API server: {e}")
            return None
        except ValueError as e:
            logger.error(f"Failed to parse JSON response from API server: {e}")
            return None

    def get_paper_by_id(self, paper_id: str) -> Optional[dict]:
        """Fetch a specific paper by ID.

        Args:
            paper_id: The paper ID to fetch

        Returns:
            Parsed JSON response or None if request fails
        """
        try:
            response = self.client.get(f"{self.base_url}/papers/{paper_id}", timeout=30)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Failed to fetch paper {paper_id} from API server: {e}")
            return None
        except ValueError as e:
            logger.error(f"Failed to parse JSON response for paper {paper_id}: {e}")
            return None

    def health_check(self) -> bool:
        """Check if the API server is running and accessible.

        Returns:
            True if server is accessible, False otherwise
        """
        try:
            response = self.client.get(f"{self.base_url}/status", timeout=5)
            return response.status_code == 200
        except httpx.RequestError:
            return False

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
