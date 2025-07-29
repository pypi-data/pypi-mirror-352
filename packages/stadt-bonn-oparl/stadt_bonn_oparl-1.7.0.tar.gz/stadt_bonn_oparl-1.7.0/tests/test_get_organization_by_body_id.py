from typing import List
from unittest.mock import MagicMock

import httpx
import pytest
from fastapi import HTTPException

from stadt_bonn_oparl.api.helpers import _get_organization_by_body_id
from stadt_bonn_oparl.api.models import OrganizationListResponse


# read json from fixture
@pytest.fixture
def organization_list_response_fixture():
    """Fixture to provide a mock response for organization list."""

    # read JSON from file
    with open("tests/fixtures/organization_body_id_1.json", "r") as f:
        import json

        return json.load(f)


@pytest.mark.asyncio
async def test_get_organization_by_body_id_success(organization_list_response_fixture):
    # Arrange
    mock_response_json = organization_list_response_fixture
    # Remove the "next" link to avoid infinite pagination loop in the test
    if "links" in mock_response_json and "next" in mock_response_json["links"]:
        del mock_response_json["links"]["next"]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_json

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_organization_by_body_id(mock_client, "1")

    # Assert
    assert isinstance(result, OrganizationListResponse)
    assert len(result.data) > 0
    assert result.data[0] is not None
    assert (
        result.data[0].id
        == "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=1"
    )
    assert isinstance(result.data[0].membership_ref, List)
    assert len(result.data[0].membership_ref) > 0
    assert result.data[0].membership_ref[0] is not None
    assert result.data[0].membership_ref[0].startswith("http://localhost:8000/")
    assert result.data[0].membership is None
    assert isinstance(result.data[0].location_ref, str)
    assert result.data[0].location_ref.startswith("http://localhost:8000/")
    assert result.data[0].location is None
    assert isinstance(result.data[0].meeting_ref, str)
    assert result.data[0].meeting_ref.startswith("http://localhost:8000/")
    assert result.data[0].meeting is None


@pytest.mark.asyncio
async def test_get_organization_by_body_id_failure():
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {}

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await _get_organization_by_body_id(mock_client, "body:404")

    assert exc_info.value.status_code == 500
    assert "Failed to fetch organization with body ID" in exc_info.value.detail
