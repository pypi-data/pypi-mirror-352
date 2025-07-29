from typing import Optional

import httpx
import logfire
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from loguru import logger

from stadt_bonn_oparl.api.dependencies import (
    chromadb_files_collection,
    http_client_factory,
)
from stadt_bonn_oparl.api.helpers import _get_file_by_id
from stadt_bonn_oparl.api.models import FileListResponse, FileResponse


def chromadb_upsert_file(file: FileResponse, collection):
    """Upsert file into ChromaDB."""
    logger.debug(f"Upserting file into ChromaDB: {file.id}")
    collection.upsert(
        documents=[file.model_dump_json()],
        metadatas=[
            {
                "id": file.id,
                "type": file.type,
                "name": file.name,
                "fileName": file.fileName,
                "date": file.date.isoformat() if file.date else None,
                "mimeType": file.mimeType,
                "agendaItem_ref": file.agendaItem_ref,
                "meeting_ref": file.meeting_ref,
                "paper_ref": file.paper_ref,
            }
        ],
        ids=[file.id],
    )


router = APIRouter()


@router.get(
    "/files/",
    tags=["oparl"],
    response_model=FileListResponse | FileResponse,
    response_model_exclude_none=True,
)
async def files(
    background_tasks: BackgroundTasks,
    file_id: Optional[str] = Query(None, alias="id"),
    http_client: httpx.Client = Depends(http_client_factory),
    collection=Depends(chromadb_files_collection),
) -> FileListResponse | FileResponse:
    """Abrufen der Dateien (Files) von der Stadt Bonn OParl API.

    Dateien sind Dokumente, die zur Verwaltungsarbeit gehören. Sie können
    Drucksachen, Sitzungsprotokollen, Anlagen oder anderen Dokumenten
    zugeordnet sein.

    Parameter
    ---------
    * **file_id**: ID der spezifischen Datei (optional)
      - Bei Angabe: Einzelne Datei mit allen Details zurück
      - Ohne Angabe: Paginierte Liste aller Dateien zurück

    Rückgabe
    --------
    * **FileResponse**: Einzelne Datei mit Referenzlinks zu lokalen API-URLs
    * **FileListResponse**: Paginierte Liste von Dateien

    Features
    --------
    * Automatische ChromaDB-Indizierung für abgerufene Dateien
    * URL-Umschreibung von Upstream zu lokalen API-Referenzen
    * Hintergrundverarbeitung für Performance
    * Umfassende Fehlerbehandlung
    * Logfire-Observability-Integration

    Hinweise
    --------
    Ein Objekt vom Typ oparl:File kann verschiedene Dokumenttypen repräsentieren,
    einschließlich PDFs, Word-Dokumente, Bilder und andere Dateiformate.

    Siehe: https://oparl.org/spezifikation/online-ansicht/#entity-file
    """
    _url = "https://www.bonn.sitzung-online.de/public/oparl/files"

    # If file_id is provided, fetch the specific file
    if file_id:
        try:
            _response = await _get_file_by_id(http_client=http_client, file_id=file_id)

            # Upsert file into ChromaDB
            with logfire.span(
                "Upserting file into ChromaDB",
            ):
                background_tasks.add_task(chromadb_upsert_file, _response, collection)

            return _response
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error fetching file {file_id}: {e.response.text}",
            )

    # If no file_id provided, return all files (list endpoint)
    response = http_client.get(_url)
    if response.status_code == 200:
        return FileListResponse(**response.json())
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch files information from OParl API",
        )
