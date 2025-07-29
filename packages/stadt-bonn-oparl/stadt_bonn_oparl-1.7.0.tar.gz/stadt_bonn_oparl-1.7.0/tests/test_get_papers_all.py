"""Tests for _get_papers_all helper function."""

import json
from unittest.mock import MagicMock

import httpx
import pytest
from fastapi import HTTPException

from stadt_bonn_oparl.api.helpers import _get_papers_all
from stadt_bonn_oparl.api.models import PaperListResponse, PaperResponse


@pytest.fixture
def papers_third_page_fixture():
    """Fixture to provide papers third page test data from file."""
    with open(
        "tests/fixtures/papers_all_third_page.json", "r", encoding="utf-8"
    ) as f:
        return json.load(f)


@pytest.mark.asyncio
async def test_get_papers_all_success(papers_third_page_fixture):
    """Test successful retrieval of all papers."""
    # Arrange
    mock_data = papers_third_page_fixture.copy()
    # Remove the next link to prevent infinite pagination loop in test
    if "links" in mock_data and "next" in mock_data["links"]:
        del mock_data["links"]["next"]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_papers_all(mock_client)

    # Assert
    assert isinstance(result, PaperListResponse)
    assert len(result.data) == 20  # Third page has 20 papers
    assert result.pagination["totalElements"] == 20360

    # Verify all papers are properly processed
    for paper in result.data:
        assert isinstance(paper, PaperResponse)
        # Check that URL transformations were applied
        if paper.body_ref:
            assert paper.body_ref.startswith("http://localhost:8000/")
        if paper.mainFile_ref:
            assert paper.mainFile_ref.startswith("http://localhost:8000/")
        if paper.originatorPerson_ref:
            assert all(url.startswith("http://localhost:8000/") for url in paper.originatorPerson_ref)
        if paper.underDirectionOfPerson_ref:
            assert all(url.startswith("http://localhost:8000/") for url in paper.underDirectionOfPerson_ref)
        if paper.consultation_ref:
            assert all(url.startswith("http://localhost:8000/") for url in paper.consultation_ref)
        
        # Verify nested objects are set to None
        assert paper.body is None
        assert paper.mainFile is None
        assert paper.originatorPerson is None
        assert paper.underDirectionOf is None
        assert paper.consultation is None

    # Verify API call with pagination parameters
    expected_url = "https://www.bonn.sitzung-online.de/public/oparl/papers?page=1&pageSize=10"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_papers_all_url_transformations(papers_third_page_fixture):
    """Test that all URL transformations are applied correctly across all papers."""
    # Arrange
    mock_data = papers_third_page_fixture.copy()
    # Remove the next link to prevent infinite pagination loop in test
    if "links" in mock_data and "next" in mock_data["links"]:
        del mock_data["links"]["next"]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_papers_all(mock_client)

    # Assert URL transformations for the first paper
    first_paper = result.data[0]
    assert first_paper.name == "Änderung der Geschäftsordnung des Beirats Kinder- und Jugendbeteiligung"

    # Check body URL transformation
    assert first_paper.body_ref == "http://localhost:8000/bodies?id=1"

    # Check mainFile URL transformation (from object id)
    assert first_paper.mainFile_ref == "http://localhost:8000/files?id=2976115&dtyp=130"

    # Check originatorPerson URL transformation (list from list)
    assert first_paper.originatorPerson_ref == ["http://localhost:8000/persons?id=2000210"]

    # Check underDirectionOf URL transformation (list from list)
    assert first_paper.underDirectionOfPerson_ref == ["http://localhost:8000/organizations?typ=at&id=322"]

    # Check consultation URL transformations
    assert first_paper.consultation_ref == [
        "http://localhost:8000/consultations?id=2032618&bi=0"
    ]

    # Verify nested objects are set to None
    assert first_paper.body is None
    assert first_paper.mainFile is None
    assert first_paper.originatorPerson is None
    assert first_paper.underDirectionOf is None
    assert first_paper.consultation is None


@pytest.mark.asyncio
async def test_get_papers_all_location_field_handling(papers_third_page_fixture):
    """Test handling of location field which appears in some papers."""
    # Arrange
    mock_data = papers_third_page_fixture.copy()
    # Remove the next link to prevent infinite pagination loop in test
    if "links" in mock_data and "next" in mock_data["links"]:
        del mock_data["links"]["next"]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_papers_all(mock_client)

    # Find paper with location field (ID: 2022899 has location field)
    paper_with_location = None
    for paper in result.data:
        if paper.id == "https://www.bonn.sitzung-online.de/public/oparl/papers?id=2022899":
            paper_with_location = paper
            break

    # Assert location URL transformations
    assert paper_with_location is not None
    # Original fixture has location as list, our processing converts to list of refs
    expected_location_refs = [
        "http://localhost:8000/locations?id=21184",
        "http://localhost:8000/locations?id=21984",
        "http://localhost:8000/locations?id=23224"
    ]
    assert paper_with_location.location_ref == expected_location_refs
    assert paper_with_location.location is None


@pytest.mark.asyncio
async def test_get_papers_all_multiple_underDirectionOf(papers_third_page_fixture):
    """Test handling of multiple underDirectionOf organizations."""
    # Arrange
    mock_data = papers_third_page_fixture.copy()
    # Remove the next link to prevent infinite pagination loop in test
    if "links" in mock_data and "next" in mock_data["links"]:
        del mock_data["links"]["next"]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_papers_all(mock_client)

    # Find paper with multiple underDirectionOf (ID: 2022912 has multiple)
    paper_with_multiple = None
    for paper in result.data:
        if paper.id == "https://www.bonn.sitzung-online.de/public/oparl/papers?id=2022912":
            paper_with_multiple = paper
            break

    # Assert all underDirectionOf organizations are included
    assert paper_with_multiple is not None
    expected_refs = [
        "http://localhost:8000/organizations?typ=at&id=296",
        "http://localhost:8000/organizations?typ=at&id=60", 
        "http://localhost:8000/organizations?typ=at&id=32"
    ]
    assert paper_with_multiple.underDirectionOfPerson_ref == expected_refs
    assert paper_with_multiple.underDirectionOf is None


@pytest.mark.asyncio
async def test_get_papers_all_http_error():
    """Test handling of HTTP error."""
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 500

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await _get_papers_all(mock_client)

    assert exc_info.value.status_code == 500
    assert "Failed to fetch papers from OParl API" in exc_info.value.detail

    # Verify API call with pagination parameters
    expected_url = "https://www.bonn.sitzung-online.de/public/oparl/papers?page=1&pageSize=10"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_papers_all_empty_response():
    """Test handling of empty papers list."""
    # Arrange
    mock_data = {
        "data": [],
        "pagination": {
            "totalElements": 0,
            "elementsPerPage": 10,
            "currentPage": 1,
            "totalPages": 0,
        },
        "links": {
            "self": "https://www.bonn.sitzung-online.de/public/oparl/papers?page=1"
        },
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_papers_all(mock_client)

    # Assert
    assert isinstance(result, PaperListResponse)
    assert len(result.data) == 0
    assert result.pagination["totalElements"] == 0


@pytest.mark.asyncio
async def test_get_papers_all_minimal_paper_data():
    """Test with minimal paper data (no optional fields)."""
    # Arrange
    mock_data = {
        "data": [
            {
                "id": "https://www.bonn.sitzung-online.de/public/oparl/papers?id=1",
                "type": "https://schema.oparl.org/1.1/Paper",
                "body": "https://www.bonn.sitzung-online.de/public/oparl/bodies?id=1",
                "name": "Minimal Paper",
                "reference": "MIN001",
                "date": "2025-06-01",
                "paperType": "Test",
                "created": "2025-06-01T12:00:00+02:00",
                "modified": "2025-06-01T12:00:00+02:00",
                "deleted": False,
            }
        ],
        "pagination": {
            "totalElements": 1,
            "elementsPerPage": 10,
            "currentPage": 1,
            "totalPages": 1,
        },
        "links": {
            "self": "https://www.bonn.sitzung-online.de/public/oparl/papers?page=1"
        },
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_papers_all(mock_client)

    # Assert
    assert isinstance(result, PaperListResponse)
    assert len(result.data) == 1

    paper = result.data[0]
    assert isinstance(paper, PaperResponse)
    assert paper.name == "Minimal Paper"
    assert paper.reference == "MIN001"

    # Verify body URL transformation was applied
    assert paper.body_ref == "http://localhost:8000/bodies?id=1"
    assert paper.body is None

    # Verify optional fields are handled correctly
    assert paper.mainFile is None
    assert paper.mainFile_ref is None
    assert paper.originatorPerson is None
    assert paper.originatorPerson_ref is None
    assert paper.consultation_ref is None


@pytest.mark.asyncio
async def test_get_papers_all_with_custom_pagination():
    """Test pagination behavior with custom page and page_size parameters."""
    # Arrange
    mock_data = {
        "data": [{
            "id": "https://example.com/papers?id=1", 
            "body": "https://example.com/bodies?id=1", 
            "name": "Paper 1", 
            "paperType": "Test",
            "type": "https://schema.oparl.org/1.1/Paper",
            "reference": "001",
            "date": "2025-01-01",
            "created": "2025-01-01T12:00:00+02:00",
            "modified": "2025-01-01T12:00:00+02:00",
            "deleted": False
        }],
        "pagination": {
            "totalElements": 100,
            "elementsPerPage": 25,
            "currentPage": 2,
            "totalPages": 4,
        },
        "links": {
            "first": "https://www.bonn.sitzung-online.de/public/oparl/papers?page=1&pageSize=25",
            "prev": "https://www.bonn.sitzung-online.de/public/oparl/papers?page=1&pageSize=25",
            "self": "https://www.bonn.sitzung-online.de/public/oparl/papers?page=2&pageSize=25",
            "next": "https://www.bonn.sitzung-online.de/public/oparl/papers?page=3&pageSize=25",
            "last": "https://www.bonn.sitzung-online.de/public/oparl/papers?page=4&pageSize=25"
        }
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_papers_all(mock_client, page=2, page_size=25)

    # Assert
    assert len(result.data) == 1
    assert result.pagination["totalElements"] == 100
    assert result.pagination["currentPage"] == 2
    assert result.pagination["elementsPerPage"] == 25
    
    # Verify links are converted to localhost URLs
    assert result.links["first"] == "http://localhost:8000/papers?page=1&pageSize=25"
    assert result.links["next"] == "http://localhost:8000/papers?page=3&pageSize=25"
    assert result.links["self"] == "http://localhost:8000/papers?page=2&pageSize=25"
    
    # Verify API call with custom pagination parameters
    expected_url = "https://www.bonn.sitzung-online.de/public/oparl/papers?page=2&pageSize=25"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)