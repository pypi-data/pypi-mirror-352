import httpx
import pytest
from fastapi import HTTPException

from stadt_bonn_oparl.api.helpers import _get_membership
from stadt_bonn_oparl.api.models import MembershipResponse

http_client = httpx.Client(base_url="https://www.bonn.sitzung-online.de/public/oparl")


@pytest.fixture(autouse=True)
def patch_http_client(monkeypatch):
    class MockResponse:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self._json = json_data

        def json(self):
            return self._json

    responses = {}

    def set_response(url, status_code, json_data):
        responses[url] = MockResponse(status_code, json_data)

    def fake_get(url):
        return responses[url]

    monkeypatch.setattr(http_client, "get", fake_get)
    return set_response


@pytest.mark.asyncio
async def test_get_memberships_success(patch_http_client):
    membership_id = "2002449"
    membership_ref = (
        "https://www.bonn.sitzung-online.de/public/oparl/memberships?id=2002449"
    )
    person_ref = "http://localhost:8000/persons?id=12851"
    organization_ref = "http://localhost:8000/organizations?typ=gr&id=352"

    json_data = {
        "id": "https://www.bonn.sitzung-online.de/public/oparl/memberships?id=2002449",
        "type": "https://schema.oparl.org/1.1/Membership",
        "person": "https://www.bonn.sitzung-online.de/public/oparl/persons?id=12851",
        "organization": "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=352",
        "role": "Stellv. beratendes Mitglied",
        "votingRight": False,
        "startDate": "2023-11-10",
        "created": "2025-05-29T12:15:12+02:00",
        "modified": "2025-05-29T12:15:12+02:00",
        "deleted": False,
    }

    patch_http_client(membership_ref, 200, json_data)
    result = await _get_membership(http_client, membership_id)

    assert isinstance(result, MembershipResponse)
    assert result.person is None
    assert result.organization is None
    assert result.person_ref == person_ref
    assert result.organization_ref == organization_ref
    assert result.role == "Stellv. beratendes Mitglied"


@pytest.mark.asyncio
async def test_get_memberships_failure(patch_http_client):
    membership_id = "0"
    membership_ref = f"https://www.bonn.sitzung-online.de/public/oparl/memberships?id={membership_id}"

    patch_http_client(membership_ref, 404, {})

    with pytest.raises(HTTPException) as excinfo:
        await _get_membership(http_client, membership_id)
    assert excinfo.value.status_code == 500
    assert f"Failed to fetch membership {membership_id} information" in str(
        excinfo.value.detail
    )

    with pytest.raises(HTTPException) as exc_info:
        await _get_membership(http_client, membership_id)

    assert exc_info.value.status_code == 500
    assert (
        f"Failed to fetch membership {membership_id} information"
        in exc_info.value.detail
    )
