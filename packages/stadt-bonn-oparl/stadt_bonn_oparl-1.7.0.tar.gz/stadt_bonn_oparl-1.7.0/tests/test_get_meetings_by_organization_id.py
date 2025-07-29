from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from stadt_bonn_oparl.api.config import UPSTREAM_API_URL
from stadt_bonn_oparl.api.helpers import _get_meetings_by_organization_id
from stadt_bonn_oparl.api.models import MeetingListResponse


@pytest.fixture
def meetings_list_response():
    """Fixture to provide a mock response for meetings list."""

    # read JSON from file
    with open("tests/fixtures/meetings_by_organization_id.json", "r") as f:
        import json

        return json.load(f)


@pytest.mark.asyncio
async def test_get_meetings_by_organization_id_success(meetings_list_response):
    # Arrange
    mock_response_json = meetings_list_response

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_json

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    organization_id = "352"
    mock_response_json = meetings_list_response

    # Act
    result = await _get_meetings_by_organization_id(mock_client, organization_id)

    # Assert
    assert isinstance(result, MeetingListResponse)
    assert len(result.data) > 0
    assert result.data[0] is not None
    assert (
        result.data[0].id
        == "https://www.bonn.sitzung-online.de/public/oparl/meetings?id=2005240"
    )
    assert result.data[0].organization is None
    assert isinstance(result.data[0].organizations_ref, list)


@pytest.mark.asyncio
async def test_get_meetings_by_organization_id_404():
    organization_id = "999"
    meetings_url = UPSTREAM_API_URL + "/meetings?organization=" + organization_id

    mock_response = MagicMock()
    mock_response.status_code = 404

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    with pytest.raises(HTTPException) as excinfo:
        await _get_meetings_by_organization_id(mock_client, organization_id)
    assert excinfo.value.status_code == 404
    assert "No meetings found for organization ID" in excinfo.value.detail


@pytest.mark.asyncio
async def test_get_meetings_by_organization_id_other_error():
    organization_id = "500"
    meetings_url = UPSTREAM_API_URL + "/meetings?organization=500"

    mock_response = MagicMock()
    mock_response.status_code = 500

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    with pytest.raises(HTTPException) as excinfo:
        await _get_meetings_by_organization_id(mock_client, organization_id)
    assert excinfo.value.status_code == 500
    assert (
        f"Failed to fetch meetings with organization ID {organization_id}"
        in excinfo.value.detail
    )
