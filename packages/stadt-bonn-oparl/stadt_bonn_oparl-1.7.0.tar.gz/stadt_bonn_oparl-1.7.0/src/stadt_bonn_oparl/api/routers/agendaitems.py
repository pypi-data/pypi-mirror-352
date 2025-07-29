from typing import Optional

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

from stadt_bonn_oparl.api.dependencies import (
    chromadb_agendaitems_collection,
    http_client_factory,
)
from stadt_bonn_oparl.api.models import (
    AgendaItemResponse,
)
from stadt_bonn_oparl.config import UPSTREAM_API_URL


def chromadb_upsert_agenda_item(data: AgendaItemResponse, collection):
    """Upsert agenda item into ChromaDB."""
    collection.upsert(
        documents=[data.model_dump_json()],
        metadatas=[
            {
                "id": data.id,
                "name": data.name,
                "number": data.number,
                "order": data.order,
                "public": data.public,
                "meeting": data.meeting,
            }
        ],
        ids=[data.id],
    )


router = APIRouter()


@router.get(
    "/agendaitems/",
    tags=["oparl"],
    response_model=AgendaItemResponse,
    response_model_exclude_none=True,
)
async def agenda_items(
    background_tasks: BackgroundTasks,
    agenda_item_id: Optional[str] = Query(None, alias="id"),
    meeting_id: Optional[str] = Query(None, alias="meeting"),
    body_id: Optional[str] = Query(None, alias="body"),
    organization_id: Optional[str] = Query(None, alias="organization"),
    page: Optional[int] = Query(1, ge=1, le=1000),
    http_client: httpx.Client = Depends(http_client_factory),
    collection=Depends(chromadb_agendaitems_collection),
) -> AgendaItemResponse:
    """Abrufen der Tagesordnungspunkte (AgendaItems) von der Stadt Bonn OParl API.

    Ein Tagesordnungspunkt ist ein Gegenstand der Beratung in einer Sitzung.
    Jeder Tagesordnungspunkt gehört zu genau einer Sitzung und kann verschiedene
    Objekte und Personen zugeordnet haben.

    Parameter
    ---------
    * **agenda_item_id**: ID des spezifischen Tagesordnungspunktes (optional)
    * **meeting_id**: ID der Sitzung für Tagesordnungsabruf (optional)
    * **body_id**: ID der Körperschaft für Tagesordnungsabruf (optional)
    * **organization_id**: ID der Organisation für Tagesordnungsabruf (optional)

    Rückgabe
    --------
    * **AgendaItemResponse**: Spezifischer Tagesordnungspunkt mit allen Details

    Hinweise
    --------
    Verschiedene Objekte können einem Tagesordnungspunkt zugeordnet sein,
    vor allem Objekte vom Typ oparl:Consultation (Beratungsgegenstände).
    Außerdem können Personen zugeordnet sein, die eine bestimmte Rolle
    beim Tagesordnungspunkt wahrnehmen.

    Siehe: https://oparl.org/spezifikation/online-ansicht/#entity-agendaitem
    """
    try:
        # Construct the URL for the specific agenda item
        url = f"{UPSTREAM_API_URL.rstrip('/')}/agendaItems?id={agenda_item_id}"

        _response = http_client.get(url, timeout=10.0)
        _response.raise_for_status()

        response = AgendaItemResponse(**_response.json())

        # Upsert the agenda item into ChromaDB
        chromadb_upsert_agenda_item(response, collection)

        return response

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Agenda item with ID {agenda_item_id} not found",
            )
        else:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error fetching agenda item {agenda_item_id}: {e.response.text}",
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while fetching agenda item {agenda_item_id}: {str(e)}",
        )
