from fastapi import APIRouter, Depends
from pydantic import BaseModel

from stadt_bonn_oparl.api.dependencies import (
    chromadb_meetings_collection,
    chromadb_memberships_collection,
    chromadb_organizations_collection,
    chromadb_persons_collection,
)


class StatusResponse(BaseModel):
    status: str
    message: str
    document_count: int = 0


router = APIRouter()


@router.get("/status", tags=["service"], response_model=StatusResponse)
async def status(
    peeps=Depends(chromadb_persons_collection),
    orgs=Depends(chromadb_organizations_collection),
    members=Depends(chromadb_memberships_collection),
    meetings=Depends(chromadb_meetings_collection),
):
    """Abrufen des Service-Status.

    Gibt den aktuellen Status des KRAken-Services zurück, einschließlich
    der Anzahl der in ChromaDB gespeicherten Dokumente.

    Rückgabe
    --------
    * **StatusResponse**: Service-Status mit Dokumentenanzahl
      - status: "ok" oder "error"
      - message: Statusnachricht
      - document_count: Anzahl gespeicherter Dokumente
    """
    try:
        return StatusResponse(
            status="ok",
            message="Service is running",
            document_count=peeps.count()
            + orgs.count()
            + members.count()
            + meetings.count(),
        )
    except Exception as e:
        return StatusResponse(status="error", message=str(e))
