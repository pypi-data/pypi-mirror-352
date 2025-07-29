from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from stadt_bonn_oparl.api.dependencies import (
    http_client_factory,
)
from stadt_bonn_oparl.api.models import LocationResponse


router = APIRouter()


@router.get(
    "/locations",
    tags=["oparl"],
    response_model=LocationResponse,
    response_model_exclude_none=True,
)
async def locations(
    location_id: Optional[str] = Query(None, alias="id"),
    page: Optional[int] = Query(1, ge=1, le=1000),
    page_size: int = Query(5, ge=1, le=100),
    http_client: httpx.Client = Depends(http_client_factory),
) -> LocationResponse:
    """Abrufen der Orte (Locations) von der Stadt Bonn OParl API.

    Ortsangaben (Locations) dienen dazu, einen Ortsbezug formal abzubilden.
    Sie können sowohl aus Textinformationen (Straßennamen, Adressen) als auch
    aus Geodaten bestehen.

    Parameter
    ---------
    * **location_id**: ID des spezifischen Ortes (erforderlich)
      - Dieser Parameter ist obligatorisch
    * **page**: Seitennummer für Paginierung (1-1000, Standard: 1)
      - Aktuell nicht verwendet
    * **page_size**: Anzahl Elemente pro Seite (1-100, Standard: 5)
      - Aktuell nicht verwendet

    Rückgabe
    --------
    * **LocationResponse**: Orts-Objekt mit räumlichen Referenzinformationen

    Fehlerbehandlung
    ---------------
    * **400**: location_id nicht angegeben
    * **404**: Ort als gelöscht markiert oder nicht gefunden
    * **500**: OParl API-Anfrage fehlgeschlagen

    Hinweise
    --------
    Ortsangaben sind nicht auf einzelne Positionen beschränkt, sondern können
    eine Vielzahl von Positionen, Flächen, Strecken etc. abdecken.

    Siehe: https://oparl.org/spezifikation/online-ansicht/#entity-location
    """
    _url = "https://www.bonn.sitzung-online.de/public/oparl/locations"

    if location_id is None:
        raise HTTPException(status_code=400, detail="Location ID is required")

    _url += f"?id={location_id}"

    response = http_client.get(_url)
    if response.status_code == 200:
        _json = response.json()

        # check if the object has deleted = True aka not found
        if _json.get("deleted", False):
            raise HTTPException(
                status_code=404, detail=f"Location with ID {location_id} not found"
            )

        return LocationResponse(**_json)
    else:
        raise HTTPException(
            status_code=500, detail="Failed to fetch locations from OParl API"
        )
