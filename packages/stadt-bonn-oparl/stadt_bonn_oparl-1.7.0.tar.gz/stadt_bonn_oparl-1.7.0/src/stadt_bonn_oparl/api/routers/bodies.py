from typing import Optional

import httpx
from fastapi import APIRouter, Depends, Query

from stadt_bonn_oparl.api.dependencies import (
    http_client_factory,
)


router = APIRouter()


@router.get("/bodies/", tags=["oparl"], response_model_exclude_none=True)
async def bodies(
    body_id: Optional[str] = Query(None, alias="id"),
    http_client: httpx.Client = Depends(http_client_factory),
):
    """Abrufen der Körperschaften (Bodies) von der Stadt Bonn OParl API.

    Eine Körperschaft (Body) bildet eine Gebietskörperschaft ab, welche als übergeordnete
    organisatorische Einheit fungiert. Alle anderen Entitäten sind einer Körperschaft zugeordnet.

    Parameter
    ---------
    * **body_id**: ID der spezifischen Körperschaft (optional)
      - Aktuell wird nur "1" (Stadt Bonn) unterstützt
      - Ohne Angabe werden alle verfügbaren Körperschaften zurückgegeben

    Rückgabe
    --------
    * **dict**: Körperschafts-Objekt oder Liste von Körperschaften

    Hinweise
    --------
    Die Körperschaft repräsentiert die primäre organisatorische Struktur in OParl,
    typischerweise entsprechend Gemeinderäten oder ähnlichen Regierungsgremien.

    Siehe: https://oparl.org/spezifikation/online-ansicht/#entity-body
    """
    _url = "https://www.bonn.sitzung-online.de/public/oparl/bodies"

    if body_id is None:
        response = http_client.get(_url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch bodies from OParl API"}

    if body_id != "1":
        return {"error": "Invalid body ID. Only '1' is supported."}

    response = http_client.get(
        _url + f"?id={body_id}",
    )
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch bodies from OParl API"}
