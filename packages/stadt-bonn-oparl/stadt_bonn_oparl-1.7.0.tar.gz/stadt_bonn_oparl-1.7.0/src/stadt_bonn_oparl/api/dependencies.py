import chromadb
import hishel
from chromadb.config import Settings

import stadt_bonn_oparl

controller = hishel.Controller(force_cache=True)
storage = hishel.FileStorage(
    ttl=7 * 60 * 60 * 24,  # Cache for 7 days
)
http_client = hishel.CacheClient(
    storage=storage,
    controller=controller,
    timeout=10.0,
    headers={
        "User-Agent": f"stadt_bonn_oparl.api/{stadt_bonn_oparl.__version__}+{hishel.__version__}"
    },
)

chromadb_client = chromadb.PersistentClient(
    path="./chroma-api",
    settings=Settings(
        anonymized_telemetry=False,  # disable posthog telemetry
    ),
)

agendaitems_collection = chromadb_client.get_or_create_collection(name="agendaitems")
files_collection = chromadb_client.get_or_create_collection(name="files")
meetings_collection = chromadb_client.get_or_create_collection(name="meetings")
memberships_collection = chromadb_client.get_or_create_collection(name="memberships")
organizations_collection = chromadb_client.get_or_create_collection(
    name="organizations"
)
papers_collection = chromadb_client.get_or_create_collection(name="papers")
persons_collection = chromadb_client.get_or_create_collection(name="persons")


# let's set up the hishel cache client, so that we can use it as a dependency in our endpoints
async def http_client_factory():
    """Factory function to create an HTTP client with caching."""
    return http_client


# This function can be used as a dependency in FastAPI endpoints
async def chromadb_persons_collection():
    """Factory function to create a ChromaDB client."""
    return persons_collection


# This function can be used as a dependency in FastAPI endpoints
async def chromadb_organizations_collection():
    """Factory function to create a ChromaDB client."""
    return organizations_collection


# This function can be used as a dependency in FastAPI endpoints
async def chromadb_memberships_collection():
    """Factory function to create a ChromaDB client."""
    return memberships_collection


# This function can be used as a dependency in FastAPI endpoints
async def chromadb_agendaitems_collection():
    """Factory function to create a ChromaDB client."""
    return agendaitems_collection


# This function can be used as a dependency in FastAPI endpoints
async def chromadb_papers_collection():
    """Factory function to create a ChromaDB client."""
    return papers_collection


# This function can be used as a dependency in FastAPI endpoints
async def chromadb_files_collection():
    """Factory function to create a ChromaDB client."""
    return files_collection


# This function can be used as a dependency in FastAPI endpoints
async def chromadb_meetings_collection():
    """Factory function to create a ChromaDB client."""
    return meetings_collection
