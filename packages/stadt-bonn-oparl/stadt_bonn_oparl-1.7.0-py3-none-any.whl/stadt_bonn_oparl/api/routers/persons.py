from typing import Optional

import httpx
import logfire
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from loguru import logger

from stadt_bonn_oparl.api.dependencies import (
    chromadb_persons_collection,
    http_client_factory,
)
from stadt_bonn_oparl.api.helpers import _get_person
from stadt_bonn_oparl.api.models import PersonListResponse, PersonResponse


def chromadb_upsert_person(data: PersonResponse, collection):
    """Upsert person into ChromaDB."""
    logger.debug(f"Upserting person into ChromaDB: {data.id}")
    collection.upsert(
        documents=[data.model_dump_json()],
        metadatas=[
            {
                "id": data.id,
                "type": data.type,
                "affix": data.affix,
                "given_name": data.givenName,
                "family_name": data.familyName,
                "name": data.name,
                "gender": data.gender,
                "status": str(data.status),
            }
        ],
        ids=[data.id],
    )


router = APIRouter()


@router.get(
    "/persons",
    tags=["oparl"],
    response_model=PersonResponse | PersonListResponse,
    response_model_exclude_none=True,
)
async def persons(
    background_tasks: BackgroundTasks,
    person_id: Optional[str] = Query(None, alias="id"),
    body_id: Optional[str] = Query(None, alias="body"),
    page: Optional[int] = Query(None, ge=1, le=1000),
    page_size: int = Query(5, ge=1, le=100),
    http_client: httpx.Client = Depends(http_client_factory),
    collection=Depends(chromadb_persons_collection),
):
    """Abrufen der Personen (Persons) von der Stadt Bonn OParl API.

    Jede natürliche Person, die in der parlamentarischen Arbeit tätig und insbesondere
    Mitglied in einer Gruppierung ist, wird als Person abgebildet. Alle Personen
    werden automatisch in ChromaDB für verbesserte Suche zwischengespeichert.

    Parameter
    ---------
    * **person_id**: ID der spezifischen Person (optional)
      - Gibt eine einzelne Person zurück
    * **body_id**: ID der Körperschaft für Personenfilterung (optional)
      - Gibt Personen dieser Körperschaft zurück
    * **page**: Seitennummer für Paginierung (1-1000, optional)
      - Nur mit body_id Parameter verwendet

    Rückgabe
    --------
    * **PersonResponse | PersonListResponse**: Einzelne Person oder paginierte Liste von Personen

    Fehlerbehandlung
    ---------------
    * **400**: person_id und body_id gleichzeitig angegeben
    * **500**: OParl API-Anfrage fehlgeschlagen

    Hinweise
    --------
    Repräsentiert natürliche Personen, die in der parlamentarischen Arbeit aktiv sind,
    insbesondere Mitglieder von Organisationen (oparl:Organization) gemäß
    OParl-Spezifikation.

    Siehe: https://oparl.org/spezifikation/online-ansicht/#entity-person
    """
    _url = "https://www.bonn.sitzung-online.de/public/oparl/persons"

    # if person_id and body_id is provided, raise an error
    if person_id is not None and body_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Failed to fetch person information from OParl API: please provide either id or body, not both.",
        )

    if person_id is None and body_id is None:
        # TODO: implement helper to get organization by body_id
        response = http_client.get(_url)
        if response.status_code == 200:
            return PersonListResponse(**response.json())
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch person information from OParl API",
            )

    if person_id and not body_id:
        person = await _get_person(http_client, person_id)

        # Upsert organization into ChromaDB
        with logfire.span(
            "Upserting organization into ChromaDB",
        ):
            background_tasks.add_task(chromadb_upsert_person, person, collection)

        return person

    if body_id:
        # TODO: implement helper to get organization by body_id
        # if body_id is provided, we need to fetch all persons for that body
        # if page is provided, we need to fetch the persons for that body
        if page is not None:
            _request = _url + f"?body={body_id}&page={page}"
        else:
            _request = _url + f"?body={body_id}"
        response = http_client.get(_request)
        if response.status_code == 200:
            return PersonListResponse(**response.json())
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed hard to fetch person information from OParl API",
            )
