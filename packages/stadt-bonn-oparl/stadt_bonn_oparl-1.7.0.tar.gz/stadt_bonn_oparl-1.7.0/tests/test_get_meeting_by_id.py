from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from stadt_bonn_oparl.api.config import UPSTREAM_API_URL
from stadt_bonn_oparl.api.helpers import _get_meeting_by_id
from stadt_bonn_oparl.api.models import MeetingResponse


@pytest.fixture
def meeting_response():
    """Fixture to provide a mock response for a single meeting."""

    # read JSON from file
    with open("tests/fixtures/meeting_2005240.json", "r") as f:
        import json

        data = json.load(f)
        return data


@pytest.mark.asyncio
async def test_get_meeting_by_id_success(meeting_response):
    # Arrange
    mock_response_json = meeting_response

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_json

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    meeting_id = "2005240"

    # Act
    result = await _get_meeting_by_id(mock_client, meeting_id)

    # Assert
    assert isinstance(result, MeetingResponse)
    assert (
        result.id
        == "https://www.bonn.sitzung-online.de/public/oparl/meetings?id=2005240"
    )
    assert (
        result.name
        == "Sitzung des Beirates Kinder- und Jugendbeteiligung (Sammeldatum für alle Vorlagen der neuen Wahlperiode)"
    )
    assert result.meetingState == "terminiert"
    assert result.cancelled is False
    assert result.organization is None
    assert isinstance(result.organizations_ref, list)
    assert len(result.organizations_ref) == 1

    # Verify the correct URL was called
    expected_url = UPSTREAM_API_URL + "/meetings?id=2005240"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_meeting_by_id_success_with_int_id(meeting_response):
    # Arrange
    mock_response_json = meeting_response

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_json

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    meeting_id = 2005240  # integer ID

    # Act
    result = await _get_meeting_by_id(mock_client, meeting_id)

    # Assert
    assert isinstance(result, MeetingResponse)
    assert (
        result.id
        == "https://www.bonn.sitzung-online.de/public/oparl/meetings?id=2005240"
    )

    # Verify the correct URL was called with integer ID
    expected_url = UPSTREAM_API_URL + "/meetings?id=2005240"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_meeting_by_id_404():
    # Arrange
    meeting_id = "999999"

    mock_response = MagicMock()
    mock_response.status_code = 404

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await _get_meeting_by_id(mock_client, meeting_id)

    assert excinfo.value.status_code == 500
    assert (
        f"Failed to fetch meeting with ID {meeting_id} from OParl API"
        in excinfo.value.detail
    )

    # Verify the correct URL was called
    expected_url = UPSTREAM_API_URL + "/meetings?id=999999"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)


@pytest.mark.asyncio
async def test_get_meeting_by_id_500():
    # Arrange
    meeting_id = "2005240"

    mock_response = MagicMock()
    mock_response.status_code = 500

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await _get_meeting_by_id(mock_client, meeting_id)

    assert excinfo.value.status_code == 500
    assert (
        f"Failed to fetch meeting with ID {meeting_id} from OParl API"
        in excinfo.value.detail
    )

    # Verify the correct URL was called
    expected_url = UPSTREAM_API_URL + "/meetings?id=2005240"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)
