import httpx
import pytest
from fastapi import HTTPException

from stadt_bonn_oparl.api.helpers import _get_person

http_client = httpx.Client(base_url="https://www.bonn.sitzung-online.de/public/oparl")


@pytest.fixture(autouse=True)
def patch_http_client(monkeypatch):
    class DummyResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self._json = json_data

        def json(self):
            return self._json

    responses = {}

    def set_response(url, status_code, json_data):
        responses[url] = DummyResponse(status_code, json_data)

    def fake_get(url):
        return responses[url]

    monkeypatch.setattr(http_client, "get", fake_get)
    return set_response


@pytest.mark.asyncio
async def test_get_person_success(patch_http_client):
    person_id = "12851"
    person_ref = "https://www.bonn.sitzung-online.de/public/oparl/persons?id=12851"

    url = f"https://www.bonn.sitzung-online.de/public/oparl/persons?id={person_id}"
    person_data = {
        "id": "https://www.bonn.sitzung-online.de/public/oparl/persons?id=12851",
        "type": "https://schema.oparl.org/1.1/Person",
        "name": "Jutta Acar",
        "familyName": "Acar",
        "givenName": "Jutta",
        "formOfAdress": "Frau",
        "affix": "Bezirksverordnete",
        "gender": "female",
        "phone": ["0160 - 7136945"],
        "email": ["jutta.acar@googlemail.com"],
        "location": "https://www.bonn.sitzung-online.de/public/oparl/locations?id=24175",
        "status": ["Politik"],
        "membership": [
            {
                "id": "https://www.bonn.sitzung-online.de/public/oparl/memberships?id=18257",
                "type": "https://schema.oparl.org/1.1/Membership",
                "person": "https://www.bonn.sitzung-online.de/public/oparl/persons?id=12851",
                "organization": "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=3",
                "role": "Bezirksverordnete/r",
                "votingRight": True,
                "startDate": "2020-11-03",
                "created": "2025-05-29T10:24:09+02:00",
                "modified": "2025-05-29T10:24:09+02:00",
                "deleted": False,
            },
            {
                "id": "https://www.bonn.sitzung-online.de/public/oparl/memberships?id=19721",
                "type": "https://schema.oparl.org/1.1/Membership",
                "person": "https://www.bonn.sitzung-online.de/public/oparl/persons?id=12851",
                "organization": "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=259",
                "role": "Sachkundige/r Bürger/in",
                "votingRight": True,
                "startDate": "2021-01-22",
                "created": "2025-05-29T10:24:09+02:00",
                "modified": "2025-05-29T10:24:09+02:00",
                "deleted": False,
            },
        ],
        "web": "https://www.bonn.sitzung-online.de/public/kp020?KPLFDNR=12851",
        "created": "2025-05-26T07:18:01+02:00",
        "modified": "2025-05-26T07:18:01+02:00",
        "deleted": False,
    }

    patch_http_client(url, 200, person_data)
    result = await _get_person(http_client, person_id)
    assert result.id == person_ref
    assert result.location == None
    assert result.location_ref == "http://localhost:8000/locations?id=24175"
    assert result.membership_ref == [
        "http://localhost:8000/memberships?id=18257",
        "http://localhost:8000/memberships?id=19721",
    ]


@pytest.mark.asyncio
async def test_get_person_not_found(patch_http_client):
    person_id = "999"
    url = f"https://www.bonn.sitzung-online.de/public/oparl/persons?id={person_id}"
    patch_http_client(url, 404, {})
    with pytest.raises(HTTPException) as excinfo:
        await _get_person(http_client, person_id)
    assert excinfo.value.status_code == 500
    assert f"Failed to fetch person {person_id} information" in str(
        excinfo.value.detail
    )
