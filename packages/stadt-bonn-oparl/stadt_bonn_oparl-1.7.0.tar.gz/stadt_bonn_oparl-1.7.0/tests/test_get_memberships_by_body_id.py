from unittest.mock import MagicMock

import httpx
import pytest

from stadt_bonn_oparl.api.helpers import (
    _get_memberships_by_body_id,
)
from stadt_bonn_oparl.api.models import MembershipListResponse


# read json from fixture
@pytest.fixture
def memberships_list_response_fixture():
    """Fixture to provide a mock response for memberships list."""

    # read JSON from file
    with open("tests/fixtures/memberships_body_id_1.json", "r") as f:
        import json

        return json.load(f)


@pytest.mark.asyncio
async def test_get_memberships_by_body_id_success(memberships_list_response_fixture):
    # Arrange
    mock_response_json = memberships_list_response_fixture

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_json

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.return_value = mock_response

    # Act
    result = await _get_memberships_by_body_id(mock_client, "1")

    # Assert
    assert isinstance(result, MembershipListResponse)
    assert len(result.data) > 0
    assert result.data[0] is not None
    assert (
        result.data[0].id
        == "https://www.bonn.sitzung-online.de/public/oparl/memberships?id=2000470"
    )
    assert isinstance(result.data[0].person_ref, str)
    assert result.data[0].person_ref.startswith("http://localhost:8000/")
    assert result.data[0].person is None
    assert isinstance(result.data[0].organization_ref, str)
    assert result.data[0].organization_ref.startswith("http://localhost:8000/")
    assert result.data[0].organization is None
