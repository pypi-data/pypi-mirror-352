from typing import Optional

import httpx
import logfire
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from loguru import logger

from stadt_bonn_oparl.api.dependencies import (
    chromadb_papers_collection,
    http_client_factory,
)
from stadt_bonn_oparl.api.helpers import _get_paper_by_id, _get_papers_all
from stadt_bonn_oparl.api.models import PaperListResponse, PaperResponse


def chromadb_upsert_paper(data: PaperResponse, collection):
    """Upsert paper into ChromaDB."""
    logger.debug(f"Upserting paper into ChromaDB: {data.id}")
    collection.upsert(
        documents=[data.model_dump_json()],
        metadatas=[
            {
                "id": data.id,
                "type": data.type,
                "name": data.name,
                "reference": data.reference,
                "date": data.date.isoformat() if data.date else None,
                "paperType": data.paperType,
                "body_ref": data.body_ref,
                "mainFile_ref": data.mainFile_ref,
            }
        ],
        ids=[data.id],
    )


router = APIRouter()


@router.get(
    "/papers/",
    tags=["oparl"],
    response_model=PaperListResponse | PaperResponse,
    response_model_exclude_none=True,
)
async def papers(
    background_tasks: BackgroundTasks,
    paper_id: Optional[str] = Query(None, alias="id"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    http_client: httpx.Client = Depends(http_client_factory),
    collection=Depends(chromadb_papers_collection),
):
    """Abrufen der Drucksachen (Papers) von der Stadt Bonn OParl API.

    Ein Dokument bildet Drucksachen in der parlamentarischen Arbeit ab. Drucksachen
    repräsentieren Dokumente wie Anträge, Anfragen und Vorlagen, die in der
    parlamentarischen Arbeit bearbeitet werden.

    Parameter
    ---------
    * **paper_id**: ID der spezifischen Drucksache (optional)
      - Bei Angabe: Einzelne Drucksache mit allen Details zurück
      - Ohne Angabe: Paginierte Liste aller Drucksachen zurück
    * **page**: Seitennummer für Paginierung (Standard: 1, Min: 1)
    * **page_size**: Anzahl Elemente pro Seite (Standard: 10, Min: 1, Max: 100)

    Rückgabe
    --------
    * **PaperResponse**: Einzelne Drucksache mit Referenzlinks zu lokalen API-URLs
    * **PaperListResponse**: Paginierte Liste von Drucksachen mit Navigation-Links

    Features
    --------
    * Automatische ChromaDB-Indizierung für abgerufene Drucksachen
    * URL-Umschreibung von Upstream zu lokalen API-Referenzen
    * Paginierung mit konfigurierbarer Seitengröße
    * Navigation-Links (first, prev, next, last) in der Antwort
    * Hintergrundverarbeitung für Performance
    * Umfassende Fehlerbehandlung
    * Logfire-Observability-Integration

    Hinweise
    --------
    Ein Objekt vom Typ oparl:Paper kann eine oder mehrere Dateien (oparl:File)
    enthalten. Weiterhin können Beratungsfolgen (oparl:Consultation) zugeordnet sein.

    Siehe: https://oparl.org/spezifikation/online-ansicht/#entity-paper
    """
    _response: PaperResponse | PaperListResponse | None = None

    # If paper_id is provided, fetch the specific paper
    if paper_id:
        try:
            _response = await _get_paper_by_id(
                http_client=http_client, paper_id=paper_id
            )

            # Upsert paper into ChromaDB
            with logfire.span(
                "Upserting paper into ChromaDB",
            ):
                background_tasks.add_task(chromadb_upsert_paper, _response, collection)

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error fetching paper {paper_id}: {e.response.text}",
            )

    # If no paper_id provided, return all papers (list endpoint)
    if paper_id is None:
        try:
            _response = await _get_papers_all(
                http_client=http_client, page=page, page_size=page_size
            )
        except HTTPException:
            raise

    if _response:
        if isinstance(_response, PaperListResponse):
            for d in _response.data:
                with logfire.span("Upserting papers into ChromaDB"):
                    background_tasks.add_task(chromadb_upsert_paper, d, collection)

        elif isinstance(_response, PaperResponse):
            with logfire.span("Upserting paper into ChromaDB"):
                background_tasks.add_task(chromadb_upsert_paper, _response, collection)

        return _response
