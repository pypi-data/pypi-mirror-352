from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from stadt_bonn_oparl.api.config import UPSTREAM_API_URL
from stadt_bonn_oparl.api.helpers import _get_file_by_id
from stadt_bonn_oparl.api.models import FileResponse


@pytest.fixture
def file_response():
    """Fixture to provide a mock response for a single file."""

    # read JSON from file
    with open("tests/fixtures/file_2956457.json", "r") as f:
        import json

        data = json.load(f)
        return data


@pytest.mark.asyncio
async def test_get_file_by_id_success(file_response):
    # Arrange
    mock_response_json = file_response

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_json

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    file_id = "2956457"

    # Act
    result = await _get_file_by_id(mock_client, file_id)

    # Assert
    assert isinstance(result, FileResponse)
    assert (
        result.id
        == "https://www.bonn.sitzung-online.de/public/oparl/files?id=2956457&dtyp=138"
    )
    assert result.name == "Öffentliches Sitzungspaket"
    assert result.fileName == "2025-05-02 _GREMIUM_KURZ_ TOP 1 SAO.pdf"
    assert result.mimeType == "pdf"
    assert result.size == 38662
    assert result.deleted is False

    # Verify URL rewriting - agendaItem should be converted to agendaItem_ref
    assert result.agendaItem is None
    assert result.agendaItem_ref == ["http://localhost:8000/agendaItems?id=2076312"]

    # Verify meeting is converted to meeting_ref
    assert result.meeting is None
    assert result.meeting_ref == "http://localhost:8000/meetings?id=2004610"

    # Verify paper is converted to paper_ref
    assert result.paper is None
    assert result.paper_ref == "http://localhost:8000/papers?id=2022383"

    # Verify the correct URL was called
    expected_url = UPSTREAM_API_URL + "/files?id=2956457"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_file_by_id_success_with_int_id(file_response):
    # Arrange
    mock_response_json = file_response

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_json

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    file_id = 2956457  # integer ID

    # Act
    result = await _get_file_by_id(mock_client, file_id)

    # Assert
    assert isinstance(result, FileResponse)
    assert (
        result.id
        == "https://www.bonn.sitzung-online.de/public/oparl/files?id=2956457&dtyp=138"
    )

    # Verify the correct URL was called with integer ID
    expected_url = UPSTREAM_API_URL + "/files?id=2956457"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_file_by_id_deleted_file(file_response):
    # Arrange
    file_id = "2956457"
    
    # Modify the fixture to simulate a deleted file
    deleted_file_response = file_response.copy()
    deleted_file_response["deleted"] = True

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = deleted_file_response

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await _get_file_by_id(mock_client, file_id)

    assert excinfo.value.status_code == 404
    assert f"File with ID {file_id} not found in OParl API" in excinfo.value.detail

    # Verify the correct URL was called
    expected_url = UPSTREAM_API_URL + f"/files?id={file_id}"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_file_by_id_404():
    # Arrange
    file_id = "999999"

    mock_response = MagicMock()
    mock_response.status_code = 404

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await _get_file_by_id(mock_client, file_id)

    assert excinfo.value.status_code == 500
    assert (
        f"Failed to fetch file with ID {file_id} from OParl API"
        in excinfo.value.detail
    )

    # Verify the correct URL was called
    expected_url = UPSTREAM_API_URL + "/files?id=999999"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_file_by_id_500():
    # Arrange
    file_id = "2956457"

    mock_response = MagicMock()
    mock_response.status_code = 500

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await _get_file_by_id(mock_client, file_id)

    assert excinfo.value.status_code == 500
    assert (
        f"Failed to fetch file with ID {file_id} from OParl API"
        in excinfo.value.detail
    )

    # Verify the correct URL was called
    expected_url = UPSTREAM_API_URL + "/files?id=2956457"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_file_by_id_url_rewriting_comprehensive(file_response):
    """Test comprehensive URL rewriting for all reference fields."""
    # Arrange
    mock_response_json = file_response.copy()
    
    # Test with multiple agendaItems
    mock_response_json["agendaItem"] = [
        "https://www.bonn.sitzung-online.de/public/oparl/agendaItems?id=1111111",
        "https://www.bonn.sitzung-online.de/public/oparl/agendaItems?id=2222222"
    ]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_json

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    file_id = "2956457"

    # Act
    result = await _get_file_by_id(mock_client, file_id)

    # Assert URL rewriting for all reference fields
    assert result.agendaItem_ref == [
        "http://localhost:8000/agendaItems?id=1111111",
        "http://localhost:8000/agendaItems?id=2222222"
    ]
    assert result.meeting_ref == "http://localhost:8000/meetings?id=2004610"
    assert result.paper_ref == "http://localhost:8000/papers?id=2022383"

    # Verify original fields are set to None
    assert result.agendaItem is None
    assert result.meeting is None
    assert result.paper is None


@pytest.mark.asyncio
async def test_get_file_by_id_no_optional_fields():
    """Test handling of file with no optional reference fields."""
    # Arrange
    minimal_file_response = {
        "id": "https://www.bonn.sitzung-online.de/public/oparl/files?id=2956457&dtyp=138",
        "type": "https://schema.oparl.org/1.1/File",
        "name": "Test File",
        "fileName": "test.pdf",
        "mimeType": "pdf",
        "size": 1000,
        "accessUrl": "https://www.bonn.sitzung-online.de/public/doc?test=1",
        "created": "2025-06-01T01:42:21+02:00",
        "modified": "2025-06-01T01:42:21+02:00",
        "deleted": False
        # No agendaItem, meeting, or paper fields
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = minimal_file_response

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    file_id = "2956457"

    # Act
    result = await _get_file_by_id(mock_client, file_id)

    # Assert
    assert isinstance(result, FileResponse)
    assert result.agendaItem_ref is None
    assert result.meeting_ref is None
    assert result.paper_ref is None
    assert result.agendaItem is None
    assert result.meeting is None
    assert result.paper is None