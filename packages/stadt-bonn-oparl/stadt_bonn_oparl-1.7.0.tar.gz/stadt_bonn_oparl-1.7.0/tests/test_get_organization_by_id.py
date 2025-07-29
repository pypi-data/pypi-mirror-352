"""Tests for _get_organization_by_id helper function."""

import json
from unittest.mock import MagicMock

import httpx
import pytest
from fastapi import HTTPException

from stadt_bonn_oparl.api.helpers import _get_organization_by_id
from stadt_bonn_oparl.api.models import OrganizationResponse


@pytest.fixture
def organization_fixture():
    """Fixture to provide organization test data from file."""
    with open("tests/fixtures/organization_352.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.asyncio
async def test_get_organization_by_id_success_string_id(organization_fixture):
    """Test successful organization retrieval with string ID."""
    # Arrange
    organization_id = "352"
    mock_data = organization_fixture

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_organization_by_id(mock_client, organization_id)

    # Assert
    assert isinstance(result, OrganizationResponse)
    assert result.id == ("https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=352")
    assert result.name == "Beirat Kinder- und Jugendbeteiligung"
    assert result.shortName == "KuJB"
    assert result.organizationType == "Hilfsorgan"
    assert result.classification == "Beiräte und Kommissionen"
    assert str(result.startDate) == "2023-11-10"

    # Verify URL transformations
    assert result.location is None
    assert result.location_ref == "http://localhost:8000/locations?id=2000682"
    assert result.membership is None
    assert isinstance(result.membership_ref, list)
    assert len(result.membership_ref) == 60  # Should match the fixture
    assert all(url.startswith("http://localhost:8000/") for url in result.membership_ref)
    assert result.meeting_ref == "http://localhost:8000/meetings?organization=352"

    # Verify API call
    expected_url = "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=352"
    mock_client.get.assert_called_once_with(expected_url)


@pytest.mark.asyncio
async def test_get_organization_by_id_success_int_id(organization_fixture):
    """Test successful organization retrieval with integer ID."""
    # Arrange
    organization_id = 352
    mock_data = organization_fixture

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_organization_by_id(mock_client, organization_id)

    # Assert
    assert isinstance(result, OrganizationResponse)
    assert result.id == ("https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=352")

    # Verify API call with converted string ID
    expected_url = "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=352"
    mock_client.get.assert_called_once_with(expected_url)


@pytest.mark.asyncio
async def test_get_organization_by_id_deleted_organization():
    """Test handling of deleted organization."""
    # Arrange
    organization_id = "352"
    mock_data = {
        "id": "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=352",
        "type": "https://schema.oparl.org/1.1/Organization",
        "deleted": True,
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await _get_organization_by_id(mock_client, organization_id)

    assert exc_info.value.status_code == 404
    assert "Organization with ID 352 not found in OParl API" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_organization_by_id_http_error():
    """Test handling of HTTP error responses."""
    # Arrange
    organization_id = "352"

    mock_response = MagicMock()
    mock_response.status_code = 500

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await _get_organization_by_id(mock_client, organization_id)

    assert exc_info.value.status_code == 500
    assert "Failed to fetch organization 352 information from OParl API" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_organization_by_id_not_found():
    """Test handling of 404 response."""
    # Arrange
    organization_id = "999"

    mock_response = MagicMock()
    mock_response.status_code = 404

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await _get_organization_by_id(mock_client, organization_id)

    assert exc_info.value.status_code == 500
    assert "Failed to fetch organization 999 information from OParl API" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_organization_by_id_minimal_data():
    """Test with minimal organization data (no optional fields)."""
    # Arrange
    organization_id = "352"
    mock_data = {
        "id": "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=352",
        "type": "https://schema.oparl.org/1.1/Organization",
        "body": "https://www.bonn.sitzung-online.de/public/oparl/bodies?id=1",
        "name": "Test Organization",
        "shortName": "TEST",
        "organizationType": "Gremium",
        "classification": "Test Classification",
        "created": "2025-05-26T07:18:01+02:00",
        "modified": "2025-05-26T07:18:01+02:00",
        "deleted": False,
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_organization_by_id(mock_client, organization_id)

    # Assert
    assert isinstance(result, OrganizationResponse)
    assert result.id == ("https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=352")
    assert result.name == "Test Organization"
    assert result.shortName == "TEST"

    # Verify optional fields are handled correctly
    assert result.location is None
    assert result.location_ref is None
    assert result.membership is None
    assert result.membership_ref is None
    assert result.meeting_ref is None


@pytest.mark.asyncio
async def test_get_organization_by_id_url_transformations(organization_fixture):
    """Test that all URL transformations are applied correctly."""
    # Arrange
    organization_id = "352"
    mock_data = organization_fixture.copy()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_organization_by_id(mock_client, organization_id)

    # Assert URL transformations
    # Original URLs should be from upstream API (check the original fixture data)
    original_membership_url = "https://www.bonn.sitzung-online.de/public/oparl/memberships?id=2002462"
    assert original_membership_url in organization_fixture["membership"]

    # Transformed URLs should point to self API
    expected_membership_url = "http://localhost:8000/memberships?id=2002462"
    assert result.membership_ref is not None
    assert expected_membership_url in result.membership_ref

    # Location ref transformation
    assert result.location_ref == "http://localhost:8000/locations?id=2000682"

    # Meeting ref transformation
    assert result.meeting_ref == "http://localhost:8000/meetings?organization=352"

    # Nested objects should be set to None
    assert result.location is None
    assert result.membership is None
