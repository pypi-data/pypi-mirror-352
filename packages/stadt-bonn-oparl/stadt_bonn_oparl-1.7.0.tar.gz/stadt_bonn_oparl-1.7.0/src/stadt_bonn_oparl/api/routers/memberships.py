from typing import Optional

import httpx
import logfire
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from loguru import logger

from stadt_bonn_oparl.api.dependencies import (
    chromadb_memberships_collection,
    http_client_factory,
)
from stadt_bonn_oparl.api.helpers import _get_membership, _get_memberships_by_body_id
from stadt_bonn_oparl.api.models import (
    MembershipListResponse,
    MembershipResponse,
)


def chromadb_upsert_membership(membership: MembershipResponse, collection):
    """Upsert membership into ChromaDB."""
    logger.debug(f"Upserting membership into ChromaDB: {membership.id}")
    collection.upsert(
        documents=[membership.model_dump_json()],
        metadatas=[
            {
                "id": membership.id,
                "type": membership.type,
            }
        ],
        ids=[membership.id],
    )


router = APIRouter()


@router.get(
    "/memberships",
    tags=["oparl"],
    response_model=MembershipResponse | MembershipListResponse,
    response_model_exclude_none=True,
)
async def memberships(
    background_tasks: BackgroundTasks,
    membership_id: Optional[str] = Query(None, alias="id"),
    person_id: Optional[str] = Query(None, alias="person"),
    body_id: Optional[str] = Query(None, alias="body"),
    page: Optional[int] = Query(1, ge=1, le=1000),
    page_size: int = Query(5, ge=1, le=100),
    http_client: httpx.Client = Depends(http_client_factory),
    collection=Depends(chromadb_memberships_collection),
):
    """Abrufen der Mitgliedschaften (Memberships) von der Stadt Bonn OParl API.

    Mitgliedschaften dienen dazu, die Zugehörigkeit von Personen zu Gruppierungen
    darzustellen. Diese können zeitlich begrenzt sein und bestimmte Rollen oder
    Positionen innerhalb der Gruppierung abbilden.

    Parameter
    ---------
    * **membership_id**: ID der spezifischen Mitgliedschaft (optional)
      - Gibt eine einzelne Mitgliedschaft zurück
      - Kann nicht zusammen mit person_id oder body_id verwendet werden
    * **person_id**: ID der Person für Mitgliedschaftsabruf (optional)
      - Gibt alle Mitgliedschaften dieser Person zurück
    * **body_id**: ID der Körperschaft für Mitgliedschaftsabruf (optional)
      - Gibt alle Mitgliedschaften innerhalb dieser Körperschaft zurück
    * **page**: Seitennummer für Paginierung (1-1000, Standard: 1)
    * **page_size**: Anzahl Elemente pro Seite (1-100, Standard: 5)

    Rückgabe
    --------
    * **MembershipResponse | MembershipListResponse**: Einzelne Mitgliedschaft oder Liste von Mitgliedschaften

    Fehlerbehandlung
    ---------------
    * **400**: membership_id zusammen mit person_id oder body_id angegeben
    * **500**: OParl API-Anfrage fehlgeschlagen

    Hinweise
    --------
    Mitgliedschaften können abbilden, dass eine Person eine bestimmte Rolle bzw.
    Position innerhalb der Gruppierung innehat (z.B. Fraktionsvorsitz).
    Alle Ergebnisse werden automatisch in ChromaDB zwischengespeichert.

    Siehe: https://oparl.org/spezifikation/online-ansicht/#entity-membership
    """
    _url = "https://www.bonn.sitzung-online.de/public/oparl/memberships"
    _response = None

    if membership_id and (person_id or body_id):
        raise HTTPException(
            status_code=400,
            detail="Failed to fetch membership information from OParl API: too many parameters provided.",
        )

    if membership_id is None and person_id is None and body_id is None:
        # TODO: implement helper
        response = http_client.get(_url)
        if response.status_code == 200:
            memberships = MembershipListResponse(**response.json())

            # Upsert all memberships into ChromaDB
            with logfire.span(
                "Upserting memberships into ChromaDB",
                extra={"count": len(memberships.data)},
            ):
                logger.debug(
                    f"Upserting {len(memberships.data)} memberships into ChromaDB"
                )
                for membership in memberships.data:
                    background_tasks.add_task(
                        chromadb_upsert_membership, membership, collection
                    )

            return MembershipListResponse(**response.json())
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch membership information from OParl API",
            )

    if membership_id and not person_id and not body_id:
        _response = await _get_membership(http_client, membership_id)

    if person_id and not body_id:
        # TODO: implement helper
        response = http_client.get(_url + f"?person={person_id}")
        if response.status_code == 200:
            return MembershipListResponse(**response.json())
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch membership information from OParl API",
            )

    if body_id:
        _response = await _get_memberships_by_body_id(http_client, body_id)

    if _response is not None:
        with logfire.span(
            "Upserting memberships into ChromaDB",
        ):
            if isinstance(_response, MembershipResponse):
                background_tasks.add_task(
                    chromadb_upsert_membership, _response, collection
                )
            elif isinstance(_response, MembershipListResponse):
                for membership in _response.data:
                    background_tasks.add_task(
                        chromadb_upsert_membership, membership, collection
                    )

        return _response
