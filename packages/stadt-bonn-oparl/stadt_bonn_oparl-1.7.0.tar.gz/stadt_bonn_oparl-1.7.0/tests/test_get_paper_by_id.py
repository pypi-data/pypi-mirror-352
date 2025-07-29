from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from stadt_bonn_oparl.api.config import UPSTREAM_API_URL
from stadt_bonn_oparl.api.helpers import _get_paper_by_id
from stadt_bonn_oparl.api.models import PaperResponse


@pytest.fixture
def paper_response():
    """Fixture to provide a mock response for a single paper."""

    # read JSON from file
    with open("tests/fixtures/paper_2022382.json", "r") as f:
        import json

        data = json.load(f)
        return data


@pytest.mark.asyncio
async def test_get_paper_by_id_success(paper_response):
    # Arrange
    mock_response_json = paper_response

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_json

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    paper_id = "2022382"

    # Act
    result = await _get_paper_by_id(mock_client, paper_id)

    # Assert
    assert isinstance(result, PaperResponse)
    assert result.id == "https://www.bonn.sitzung-online.de/public/oparl/papers?id=2022382"
    assert result.name == "N-Vorlage zum CDU-Antrag: Priorisierungsliste Instandsetzung Baudenkmäler"
    assert result.reference == "252775-02"
    assert result.paperType == "Beschlussvorlage"
    assert result.deleted is False

    # Verify URL rewriting - body should be converted to body_ref
    assert result.body is None
    assert result.body_ref == "http://localhost:8000/bodies?id=1"

    # Verify mainFile is converted to mainFile_ref (extracted from the mainFile object's id)
    assert result.mainFile is None
    assert result.mainFile_ref == "http://localhost:8000/files?id=2954516&dtyp=130"

    # Verify originatorPerson is converted to originatorPerson_ref (list from list)
    assert result.originatorPerson is None
    assert result.originatorPerson_ref == ["http://localhost:8000/persons?id=11862"]

    # Verify underDirectionOf is converted to underDirectionOfPerson_ref (list from list)
    assert result.underDirectionOf is None
    assert result.underDirectionOfPerson_ref == [
        "http://localhost:8000/organizations?typ=at&id=224",
        "http://localhost:8000/organizations?typ=at&id=158",
        "http://localhost:8000/organizations?typ=at&id=60",
        "http://localhost:8000/organizations?typ=at&id=176",
        "http://localhost:8000/organizations?typ=at&id=80",
        "http://localhost:8000/organizations?typ=at&id=293",
        "http://localhost:8000/organizations?typ=at&id=352",
        "http://localhost:8000/organizations?typ=at&id=296",
        "http://localhost:8000/organizations?typ=at&id=297",
    ]

    # Verify consultation is converted to consultation_ref
    assert result.consultation is None
    assert result.consultation_ref is not None
    assert isinstance(result.consultation_ref, list)
    assert len(result.consultation_ref) == 2
    assert all("localhost:8000" in url for url in result.consultation_ref)

    # Verify the correct URL was called
    expected_url = UPSTREAM_API_URL + "/papers?id=2022382"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_paper_by_id_success_with_int_id(paper_response):
    # Arrange
    mock_response_json = paper_response

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_json

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    paper_id = 2022382  # integer ID

    # Act
    result = await _get_paper_by_id(mock_client, paper_id)

    # Assert
    assert isinstance(result, PaperResponse)
    assert result.id == "https://www.bonn.sitzung-online.de/public/oparl/papers?id=2022382"

    # Verify the correct URL was called with integer ID
    expected_url = UPSTREAM_API_URL + "/papers?id=2022382"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_paper_by_id_deleted_paper(paper_response):
    # Arrange
    paper_id = "2022382"

    # Modify the fixture to simulate a deleted paper
    deleted_paper_response = paper_response.copy()
    deleted_paper_response["deleted"] = True

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = deleted_paper_response

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await _get_paper_by_id(mock_client, paper_id)

    assert excinfo.value.status_code == 404
    assert f"Paper with ID {paper_id} not found in OParl API" in excinfo.value.detail

    # Verify the correct URL was called
    expected_url = UPSTREAM_API_URL + f"/papers?id={paper_id}"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_paper_by_id_404():
    # Arrange
    paper_id = "999999"

    mock_response = MagicMock()
    mock_response.status_code = 404

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await _get_paper_by_id(mock_client, paper_id)

    assert excinfo.value.status_code == 500
    assert f"Failed to fetch paper with ID {paper_id} from OParl API" in excinfo.value.detail

    # Verify the correct URL was called
    expected_url = UPSTREAM_API_URL + "/papers?id=999999"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_paper_by_id_500():
    # Arrange
    paper_id = "2022382"

    mock_response = MagicMock()
    mock_response.status_code = 500

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await _get_paper_by_id(mock_client, paper_id)

    assert excinfo.value.status_code == 500
    assert f"Failed to fetch paper with ID {paper_id} from OParl API" in excinfo.value.detail

    # Verify the correct URL was called
    expected_url = UPSTREAM_API_URL + "/papers?id=2022382"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_paper_by_id_url_rewriting_comprehensive(paper_response):
    """Test comprehensive URL rewriting for all reference fields."""
    # Arrange
    mock_response_json = paper_response.copy()

    # Add some additional fields to test URL rewriting
    mock_response_json["relatedPaper"] = [
        "https://www.bonn.sitzung-online.de/public/oparl/papers?id=1111111",
        "https://www.bonn.sitzung-online.de/public/oparl/papers?id=2222222",
    ]
    mock_response_json["superordinatedPaper"] = "https://www.bonn.sitzung-online.de/public/oparl/papers?id=3333333"
    mock_response_json["subordinatedPaper"] = ["https://www.bonn.sitzung-online.de/public/oparl/papers?id=4444444"]
    mock_response_json["auxilaryFile"] = [
        "https://www.bonn.sitzung-online.de/public/oparl/files?id=5555555",
        "https://www.bonn.sitzung-online.de/public/oparl/files?id=6666666",
    ]
    mock_response_json["location"] = "https://www.bonn.sitzung-online.de/public/oparl/locations?id=7777777"
    mock_response_json["originatorOrganization"] = "https://www.bonn.sitzung-online.de/public/oparl/organizations?id=8888888"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_json

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    paper_id = "2022382"

    # Act
    result = await _get_paper_by_id(mock_client, paper_id)

    # Assert URL rewriting for all reference fields
    assert result.relatedPapers_ref == ["http://localhost:8000/papers?id=1111111", "http://localhost:8000/papers?id=2222222"]
    assert result.superordinatedPaper_ref == "http://localhost:8000/papers?id=3333333"
    assert result.subordinatedPaper_ref == ["http://localhost:8000/papers?id=4444444"]
    assert result.auxilaryFiles_ref == ["http://localhost:8000/files?id=5555555", "http://localhost:8000/files?id=6666666"]
    assert result.location_ref == ["http://localhost:8000/locations?id=7777777"]
    assert result.originatorOrganization_ref == ["http://localhost:8000/organizations?id=8888888"]

    # Verify original fields are set to None
    assert result.relatedPaper is None
    assert result.superordinatedPaper is None
    assert result.subordinatedPaper is None
    assert result.auxilaryFile is None
    assert result.location is None
    assert result.originatorOrganization is None
