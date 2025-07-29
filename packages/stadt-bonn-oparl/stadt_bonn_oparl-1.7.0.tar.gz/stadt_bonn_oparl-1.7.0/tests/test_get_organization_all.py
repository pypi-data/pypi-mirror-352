"""Tests for _get_organization_all helper function."""

import json
from unittest.mock import MagicMock

import httpx
import pytest
from fastapi import HTTPException

from stadt_bonn_oparl.api.helpers import _get_organization_all
from stadt_bonn_oparl.api.models import OrganizationListResponse, OrganizationResponse


@pytest.fixture
def organizations_first_page_fixture():
    """Fixture to provide organizations first page test data from file."""
    with open(
        "tests/fixtures/organizations_all_first_page.json", "r", encoding="utf-8"
    ) as f:
        return json.load(f)


@pytest.mark.asyncio
async def test_get_organization_all_single_page(organizations_first_page_fixture):
    """Test successful retrieval of all organizations with single page."""
    # Arrange - modify fixture to have no next page
    mock_data = organizations_first_page_fixture.copy()
    mock_data["links"] = {
        "self": "https://www.bonn.sitzung-online.de/public/oparl/organizations?page=1"
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_organization_all(mock_client)

    # Assert
    assert isinstance(result, OrganizationListResponse)
    assert len(result.data) == 20  # First page has 20 organizations
    assert result.pagination["total"] == 20
    assert result.links == {}

    # Verify all organizations are properly processed
    for org in result.data:
        assert isinstance(org, OrganizationResponse)
        # Check that URL transformations were applied
        if org.membership_ref:
            assert all(
                url.startswith("http://localhost:8000/") for url in org.membership_ref
            )
        if org.location_ref:
            assert org.location_ref.startswith("http://localhost:8000/")
        if org.meeting_ref:
            assert org.meeting_ref.startswith("http://localhost:8000/")
        # Verify nested objects are set to None
        assert org.membership is None
        assert org.location is None
        assert org.meeting is None

    # Verify API call
    expected_url = "https://www.bonn.sitzung-online.de/public/oparl/organizations"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_organization_all_multiple_pages(organizations_first_page_fixture):
    """Test successful retrieval of all organizations with multiple pages."""
    # Arrange - first page with next link
    first_page_data = organizations_first_page_fixture.copy()

    # Second page data (simplified)
    second_page_data = {
        "data": [
            {
                "id": "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=999",
                "type": "https://schema.oparl.org/1.1/Organization",
                "body": "https://www.bonn.sitzung-online.de/public/oparl/bodies?id=1",
                "name": "Test Organization Page 2",
                "shortName": "TEST2",
                "organizationType": "Gremium",
                "classification": "Test",
                "created": "2025-06-01T04:40:13+02:00",
                "modified": "2025-06-01T04:40:13+02:00",
                "deleted": False,
            }
        ],
        "pagination": {
            "totalElements": 21,
            "elementsPerPage": 20,
            "currentPage": 2,
            "totalPages": 2,
        },
        "links": {
            "self": "https://www.bonn.sitzung-online.de/public/oparl/organizations?page=2"
        },
    }

    # Mock responses for both pages
    first_response = MagicMock()
    first_response.status_code = 200
    first_response.json.return_value = first_page_data

    second_response = MagicMock()
    second_response.status_code = 200
    second_response.json.return_value = second_page_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.side_effect = [first_response, second_response]

    # Act
    result = await _get_organization_all(mock_client)

    # Assert
    assert isinstance(result, OrganizationListResponse)
    assert len(result.data) == 21  # 20 from first page + 1 from second page
    assert result.pagination["total"] == 21
    assert result.links == {}

    # Verify both API calls were made
    assert mock_client.get.call_count == 2
    calls = mock_client.get.call_args_list
    assert (
        calls[0][0][0]
        == "https://www.bonn.sitzung-online.de/public/oparl/organizations"
    )
    assert (
        calls[1][0][0]
        == "https://www.bonn.sitzung-online.de/public/oparl/organizations?page=2"
    )


@pytest.mark.asyncio
async def test_get_organization_all_http_error_first_page():
    """Test handling of HTTP error on first page."""
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 500

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await _get_organization_all(mock_client)

    assert exc_info.value.status_code == 500
    assert "Failed to fetch organizations from OParl API" in exc_info.value.detail

    # Verify API call
    expected_url = "https://www.bonn.sitzung-online.de/public/oparl/organizations"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_organization_all_http_error_subsequent_page(
    organizations_first_page_fixture,
):
    """Test handling of HTTP error on subsequent page."""
    # Arrange - first page succeeds, second page fails
    first_page_data = organizations_first_page_fixture.copy()

    first_response = MagicMock()
    first_response.status_code = 200
    first_response.json.return_value = first_page_data

    second_response = MagicMock()
    second_response.status_code = 500

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.side_effect = [first_response, second_response]

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await _get_organization_all(mock_client)

    assert exc_info.value.status_code == 500
    assert "Failed to fetch organizations from OParl API" in exc_info.value.detail

    # Verify both API calls were attempted
    assert mock_client.get.call_count == 2


@pytest.mark.asyncio
async def test_get_organization_all_empty_response():
    """Test handling of empty organizations list."""
    # Arrange
    mock_data = {
        "data": [],
        "pagination": {
            "totalElements": 0,
            "elementsPerPage": 20,
            "currentPage": 1,
            "totalPages": 0,
        },
        "links": {
            "self": "https://www.bonn.sitzung-online.de/public/oparl/organizations?page=1"
        },
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_organization_all(mock_client)

    # Assert
    assert isinstance(result, OrganizationListResponse)
    assert len(result.data) == 0
    assert result.pagination["total"] == 0
    assert result.links == {}


@pytest.mark.asyncio
async def test_get_organization_all_minimal_organization_data():
    """Test with minimal organization data (no optional fields)."""
    # Arrange
    mock_data = {
        "data": [
            {
                "id": "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=1",
                "type": "https://schema.oparl.org/1.1/Organization",
                "body": "https://www.bonn.sitzung-online.de/public/oparl/bodies?id=1",
                "name": "Minimal Organization",
                "shortName": "MIN",
                "organizationType": "Gremium",
                "classification": "Test",
                "created": "2025-06-01T04:40:13+02:00",
                "modified": "2025-06-01T04:40:13+02:00",
                "deleted": False,
            }
        ],
        "pagination": {
            "totalElements": 1,
            "elementsPerPage": 20,
            "currentPage": 1,
            "totalPages": 1,
        },
        "links": {
            "self": "https://www.bonn.sitzung-online.de/public/oparl/organizations?page=1"
        },
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_organization_all(mock_client)

    # Assert
    assert isinstance(result, OrganizationListResponse)
    assert len(result.data) == 1

    org = result.data[0]
    assert isinstance(org, OrganizationResponse)
    assert org.name == "Minimal Organization"
    assert org.shortName == "MIN"

    # Verify optional fields are handled correctly
    assert org.location is None
    assert org.location_ref is None
    assert org.membership is None
    assert org.membership_ref is None
    assert org.meeting_ref is None


@pytest.mark.asyncio
async def test_get_organization_all_url_transformations(
    organizations_first_page_fixture,
):
    """Test that all URL transformations are applied correctly across all organizations."""
    # Arrange
    mock_data = organizations_first_page_fixture.copy()
    mock_data["links"] = {
        "self": "https://www.bonn.sitzung-online.de/public/oparl/organizations?page=1"
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_organization_all(mock_client)

    # Assert URL transformations for the first organization (Rat)
    rat_org = result.data[0]
    assert rat_org.name == "Rat"

    # Check membership URL transformations
    assert rat_org.membership_ref is not None
    assert len(rat_org.membership_ref) > 0
    # Original URL from fixture should be transformed
    expected_membership_url = "http://localhost:8000/memberships?id=13329"
    assert expected_membership_url in rat_org.membership_ref

    # Check location ref transformation
    assert rat_org.location_ref == "http://localhost:8000/locations?id=20001"

    # Check meeting ref transformation
    assert rat_org.meeting_ref == "http://localhost:8000/meetings?organization=1"

    # Verify nested objects are set to None
    assert rat_org.location is None
    assert rat_org.membership is None
    assert rat_org.meeting is None


@pytest.mark.asyncio
async def test_get_organization_all_timeout_parameter():
    """Test that timeout parameter is passed correctly to HTTP client."""
    # Arrange
    mock_data = {"data": [], "pagination": {"totalElements": 0}, "links": {}}

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    await _get_organization_all(mock_client)

    # Assert
    mock_client.get.assert_called_once_with(
        "https://www.bonn.sitzung-online.de/public/oparl/organizations", timeout=10.0
    )
