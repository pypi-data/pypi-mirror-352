from typing import Optional

import httpx
import logfire
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from loguru import logger

from stadt_bonn_oparl.api.config import SELF_API_URL
from stadt_bonn_oparl.api.dependencies import (
    chromadb_organizations_collection,
    http_client_factory,
)
from stadt_bonn_oparl.api.helpers import (
    _get_organization_all,
    _get_organization_by_body_id,
    _get_organization_by_id,
)
from stadt_bonn_oparl.api.models import (
    OrganizationListResponse,
    OrganizationResponse,
)


# https://docs.pydantic.dev/latest/concepts/models/#rebuilding-model-schema
OrganizationResponse.model_rebuild()


def chromadb_upsert_organization(org: OrganizationResponse, collection):
    """Upsert organization into ChromaDB."""
    logger.debug(f"Upserting organization into ChromaDB: {org.id}")
    collection.upsert(
        documents=[org.model_dump_json()],
        metadatas=[
            {
                "id": org.id,
                "type": org.type,
                "name": org.name,
                "short_name": org.shortName,
            }
        ],
        ids=[org.id],
    )


router = APIRouter()


@router.get(
    "/organizations/",
    tags=["oparl"],
    response_model=OrganizationResponse | OrganizationListResponse,
)
async def organizations(
    background_tasks: BackgroundTasks,
    organization_id: Optional[str] = Query(None, alias="id"),
    body_id: Optional[str] = Query(None, alias="body"),
    page: int = Query(1, ge=1, le=1000),
    page_size: int = Query(5, ge=1, le=100),
    http_client: httpx.Client = Depends(http_client_factory),
    collection=Depends(chromadb_organizations_collection),
):
    """Abrufen der Organisationen (Organizations) von der Stadt Bonn OParl API.

    Organisationen dienen dazu, Gruppierungen von Personen abzubilden, die in der
    parlamentarischen Arbeit eine Rolle spielen. Dazu zählen insbesondere Fraktionen
    und Gremien. Unterstützt umfassende Filterung, Paginierung und automatisches
    ChromaDB-Caching für verbesserte Performance.

    Parameter
    ---------
    * **organization_id**: ID der spezifischen Organisation (optional)
      - Gibt eine einzelne Organisation zurück
      - Kann nicht zusammen mit body_id verwendet werden
    * **body_id**: ID der Körperschaft für Organisationsfilterung (optional)
      - Gibt alle Organisationen dieser Körperschaft zurück
      - Kann nicht zusammen mit organization_id verwendet werden
    * **page**: Seitennummer für Paginierung (1-1000, Standard: 1)
    * **page_size**: Anzahl Elemente pro Seite (1-100, Standard: 5)

    Rückgabe
    --------
    * **OrganizationResponse | OrganizationListResponse**: Einzelne Organisation oder paginierte Liste mit Metadaten und Navigationslinks

    Fehlerbehandlung
    ---------------
    * **400**: organization_id und body_id gleichzeitig angegeben
    * **500**: OParl API-Anfrage fehlgeschlagen

    Hinweise
    --------
    In der Praxis zählen zu den Organisationen insbesondere Fraktionen und Gremien.
    Alle Ergebnisse werden automatisch in ChromaDB für erweiterte Suchfähigkeiten
    zwischengespeichert.

    Siehe: https://oparl.org/spezifikation/online-ansicht/#entity-organization
    """
    _url = "https://www.bonn.sitzung-online.de/public/oparl/organizations"
    _response = None

    # if organization_id and body_id is provided, raise an error
    if organization_id is not None and body_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Please provide either id or body, not both.",
        )

    # if organization_id is None and body_id is None, return all organizations
    if organization_id is None and body_id is None:
        try:
            all_orgs_response = await _get_organization_all(http_client)
            # Apply pagination to the results
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_data = all_orgs_response.data[start_idx:end_idx]

            total_count = len(all_orgs_response.data)
            total_pages = (total_count + page_size - 1) // page_size

            # Build pagination links
            base_url = f"{SELF_API_URL}/organizations"
            links = {}
            if page > 1:
                links["prev"] = f"{base_url}?page={page-1}&page_size={page_size}"
            if page < total_pages:
                links["next"] = f"{base_url}?page={page+1}&page_size={page_size}"

            _response = OrganizationListResponse(
                data=paginated_data,
                pagination={
                    "page": page,
                    "page_size": page_size,
                    "total": total_count,
                    "total_pages": total_pages,
                },
                links=links,
            )
        except HTTPException as e:
            logfire.error(
                f"Error fetching organization information: {e.status_code}",
                extra={"url": _url, "body_id": body_id},
            )

    # if organization_id is provided, return the organization with that id
    if organization_id and not body_id:
        try:
            _response = await _get_organization_by_id(http_client, organization_id)

        except HTTPException as e:
            logfire.error(
                f"Error fetching organization information: {e.status_code}",
                extra={"url": _url, "organization_id": organization_id},
            )
            raise

    # if body_id is provided, return all organizations for that body
    if body_id and not organization_id:
        try:
            all_orgs_response = await _get_organization_by_body_id(http_client, body_id)
            # Apply pagination to the results
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_data = all_orgs_response.data[start_idx:end_idx]

            total_count = len(all_orgs_response.data)
            total_pages = (total_count + page_size - 1) // page_size

            # Build pagination links
            base_url = f"{SELF_API_URL}/organizations"
            links = {}
            if page > 1:
                links["prev"] = (
                    f"{base_url}?body={body_id}&page={page-1}&page_size={page_size}"
                )
            if page < total_pages:
                links["next"] = (
                    f"{base_url}?body={body_id}&page={page+1}&page_size={page_size}"
                )

            _response = OrganizationListResponse(
                data=paginated_data,
                pagination={
                    "page": page,
                    "page_size": page_size,
                    "total": total_count,
                    "total_pages": total_pages,
                },
                links=links,
            )

        except HTTPException as e:
            logfire.error(
                f"Error fetching organization information: {e.status_code}",
                extra={"url": _url, "body_id": body_id},
            )

    if _response is not None:
        # Upsert organization into ChromaDB
        if isinstance(_response, OrganizationListResponse):
            for org in _response.data:
                with logfire.span(
                    "Upserting organization into ChromaDB",
                ):
                    background_tasks.add_task(
                        chromadb_upsert_organization, org, collection
                    )

        elif isinstance(_response, OrganizationResponse):
            with logfire.span(
                "Upserting organization into ChromaDB",
            ):
                background_tasks.add_task(
                    chromadb_upsert_organization, _response, collection
                )

    return _response
