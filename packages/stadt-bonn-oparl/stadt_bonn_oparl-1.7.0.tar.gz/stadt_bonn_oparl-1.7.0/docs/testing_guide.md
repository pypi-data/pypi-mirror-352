# Testing Guide for Stadt Bonn OParl Project

This document outlines the testing patterns, conventions, and best practices used in the Stadt Bonn OParl project.

## Table of Contents

- [File Organization](#file-organization)
- [Naming Conventions](#naming-conventions)
- [Test Structure](#test-structure)
- [Fixture Patterns](#fixture-patterns)
- [Mocking Strategies](#mocking-strategies)
- [Assertion Patterns](#assertion-patterns)
- [Error Testing](#error-testing)
- [Async Testing](#async-testing)
- [Import Patterns](#import-patterns)
- [Best Practices](#best-practices)
- [Examples](#examples)

## File Organization

### Test File Structure
```
tests/
├── fixtures/                          # JSON fixtures from real API responses
│   ├── meeting_2005240.json
│   ├── meetings_by_organization_id.json
│   ├── membership.json
│   └── ...
├── test_api_server_*.py               # API endpoint tests
├── test_get_*.py                      # Helper function tests
├── test_models.py                     # Model behavior tests
└── test_*.py                          # Other functional tests
```

### Naming Conventions

#### Test Files
- **Pattern**: `test_<module_or_functionality>.py`
- **API tests**: `test_api_server_<endpoint>.py`
- **Helper functions**: `test_get_<resource>_by_<criteria>.py`
- **Models**: `test_models.py`
- **Utilities**: `test_<utility_name>.py`

#### Test Functions
- **Pattern**: `test_<function_or_scenario>_<condition>`
- **Success cases**: `test_get_person_success`
- **Failure cases**: `test_get_person_404`, `test_get_person_not_found`
- **Edge cases**: `test_get_meeting_by_id_success_with_int_id`
- **Model behavior**: `test_tagcount_addition`, `test_papertype_enum`

## Test Structure

### Basic Test Structure
```python
@pytest.mark.asyncio  # For async functions
async def test_function_name_condition():
    # Arrange
    mock_data = setup_test_data()
    mock_client = setup_mock_client()
    
    # Act
    result = await function_under_test(mock_client, parameters)
    
    # Assert
    assert isinstance(result, ExpectedType)
    assert result.property == expected_value
    mock_client.method.assert_called_once_with(expected_args)
```

### Class-Based Tests for Related Functionality
```python
class TestOParlAgendaItemDownloadAllFiles:
    """Test cases for the download_all_files method of OParlAgendaItem."""
    
    @pytest.fixture
    def sample_agenda_item(self):
        """Create a sample agenda item with files."""
        return OParlAgendaItem(...)
    
    def test_specific_behavior(self, sample_agenda_item):
        # Test implementation
        pass
```

## Fixture Patterns

### File-Based Fixtures
```python
@pytest.fixture
def meetings_list_response():
    """Fixture to provide a mock response for meetings list."""
    with open("tests/fixtures/meetings_by_organization_id.json", "r") as f:
        import json
        return json.load(f)
```

### Auto-Use Fixtures for Global Mocking
```python
@pytest.fixture(autouse=True)
def patch_http_client(monkeypatch):
    """Mock HTTP client globally for the test module."""
    def fake_get(url, timeout=None):
        return responses.get(url, MockResponse(404, {}))
    
    monkeypatch.setattr(httpx.Client, "get", fake_get)
```

### Temporary Directory Fixtures
```python
@pytest.fixture
def temp_data_path(self):
    """Create a temporary directory for test data."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)
```

### Data Transformation in Fixtures
```python
@pytest.fixture
def meeting_response():
    """Fixture that transforms raw API data to match model expectations."""
    with open("tests/fixtures/meeting_2005240.json", "r") as f:
        data = json.load(f)
        # Transform organization from list to None and add organizations_ref
        data["organizations_ref"] = data["organization"]
        data["organization"] = None
        # Handle field name mismatches
        if "cancelled" in data:
            data["canceled"] = data["cancelled"]
            del data["cancelled"]
        return data
```

## Mocking Strategies

### HTTP Client Mocking with Custom Mock Classes
```python
class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data
    
    def json(self):
        return self._json

def setup_mock_client(status_code=200, json_data=None):
    mock_response = MockResponse(status_code, json_data or {})
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    return mock_client
```

### MagicMock for Complex Objects
```python
from unittest.mock import MagicMock

mock_client = MagicMock()
mock_client.get.return_value = mock_response
# Later verify calls:
mock_client.get.assert_called_once_with(expected_url, timeout=10.0)
```

### Monkeypatch for Function Replacement
```python
def test_with_monkeypatch(monkeypatch):
    def fake_download_file(url, path, **kwargs):
        return True, None
    
    monkeypatch.setattr('stadt_bonn_oparl.utils.download_file', fake_download_file)
```

### Patch Decorator for Dependencies
```python
@patch('stadt_bonn_oparl.utils.download_file')
def test_download_all_files(mock_download, sample_agenda_item):
    mock_download.return_value = (True, None)
    # Test implementation
```

## Assertion Patterns

### Type Assertions
```python
assert isinstance(result, MembershipResponse)
assert isinstance(result.organizations_ref, list)
```

### Content Assertions
```python
assert result.role == "Stellv. beratendes Mitglied"
assert result.person is None
assert result.person_ref == expected_person_ref
```

### Collection Assertions
```python
assert len(result.data) > 0
assert len(result.organizations_ref) == 1
assert "tag1" in analysis.tags
```

### URL/Reference Assertions
```python
assert result.data[0].person_ref.startswith("http://localhost:8000/")
assert result.id == "https://www.bonn.sitzung-online.de/public/oparl/meetings?id=2005240"
```

### Null/None Assertions
```python
assert result.organization is None
assert result.person_ref is not None
```

## Error Testing

### Exception Context Managers
```python
with pytest.raises(HTTPException) as excinfo:
    await _get_membership(http_client, membership_id)

assert excinfo.value.status_code == 500
assert f"Failed to fetch membership {membership_id}" in excinfo.value.detail
```

### HTTP Status Code Testing
```python
# Test 404 Not Found
@pytest.mark.asyncio
async def test_get_meeting_by_id_404():
    mock_client = setup_mock_client(status_code=404)
    
    with pytest.raises(HTTPException) as excinfo:
        await _get_meeting_by_id(mock_client, "999999")
    
    assert excinfo.value.status_code == 500  # Function converts all non-200 to 500
    assert "Failed to fetch meeting with ID 999999" in excinfo.value.detail

# Test 500 Server Error
@pytest.mark.asyncio
async def test_get_meeting_by_id_500():
    mock_client = setup_mock_client(status_code=500)
    
    with pytest.raises(HTTPException) as excinfo:
        await _get_meeting_by_id(mock_client, "2005240")
    
    assert excinfo.value.status_code == 500
```

### Model Validation Error Testing
```python
with pytest.raises(ValueError):
    _ = tagcount1 + tagcount2  # Different tags should raise ValueError
```

## Async Testing

### Async Test Marking
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function_under_test()
    assert result is not None
```

### Async Function Testing Best Practices
- Always use `@pytest.mark.asyncio` decorator
- Use `await` for all async function calls
- Ensure proper async fixture handling
- Test async error handling with try/except or pytest.raises

## Import Patterns

### Standard Library Imports
```python
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
```

### Third-party Imports
```python
import httpx
import pytest
from fastapi import HTTPException
```

### Project-specific Imports
```python
from stadt_bonn_oparl.api.helpers import _get_membership
from stadt_bonn_oparl.api.models import MembershipResponse
from stadt_bonn_oparl.papers.models import TagCount, TagAggregation
from stadt_bonn_oparl.api.config import UPSTREAM_API_URL
```

## Best Practices

### 1. Comprehensive Test Coverage
- Test success scenarios with various input types
- Test all error conditions (404, 500, validation errors)
- Test edge cases (empty data, malformed input)

### 2. Realistic Test Data
- Use actual API responses as fixtures
- Store fixtures in `tests/fixtures/` directory
- Transform fixture data when needed to match model expectations

### 3. Test Isolation
- Each test should be independent
- Use fixtures for setup and teardown
- Don't rely on test execution order

### 4. Consistent Mocking Strategy
- Use consistent HTTP client mocking across API tests
- Mock external dependencies (file downloads, API calls)
- Verify mock calls with appropriate assertions

### 5. Clear Test Documentation
```python
def test_download_all_files_with_files(self, mock_download, sample_agenda_item, temp_data_path):
    \"\"\"Test downloading all files when agenda item has files.
    
    This test verifies that the download_all_files method correctly:
    - Downloads all files associated with an agenda item
    - Returns success status for each file
    - Creates appropriate directory structure
    \"\"\"
```

### 6. Error Message Testing
```python
# Always test both status code and error message content
assert excinfo.value.status_code == 500
assert f"Failed to fetch meeting with ID {meeting_id}" in excinfo.value.detail
```

### 7. URL Construction Verification
```python
# Verify that correct URLs are constructed and called
expected_url = UPSTREAM_API_URL + f"/meetings?id={meeting_id}"
mock_client.get.assert_called_once_with(expected_url, timeout=10.0)
```

## Examples

### Complete API Helper Function Test
```python
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException
from stadt_bonn_oparl.api.config import UPSTREAM_API_URL
from stadt_bonn_oparl.api.helpers import _get_meeting_by_id
from stadt_bonn_oparl.api.models import MeetingResponse

@pytest.fixture
def meeting_response():
    \"\"\"Fixture to provide a mock response for a single meeting.\"\"\"
    with open("tests/fixtures/meeting_2005240.json", "r") as f:
        import json
        data = json.load(f)
        # Transform data to match model expectations
        data["organizations_ref"] = data["organization"]
        data["organization"] = None
        if "cancelled" in data:
            data["canceled"] = data["cancelled"]
            del data["cancelled"]
        return data

@pytest.mark.asyncio
async def test_get_meeting_by_id_success(meeting_response):
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = meeting_response
    
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    
    meeting_id = "2005240"
    
    # Act
    result = await _get_meeting_by_id(mock_client, meeting_id)
    
    # Assert
    assert isinstance(result, MeetingResponse)
    assert result.id == "https://www.bonn.sitzung-online.de/public/oparl/meetings?id=2005240"
    assert result.organization is None
    assert isinstance(result.organizations_ref, list)
    
    # Verify URL construction
    expected_url = UPSTREAM_API_URL + "/meetings?id=2005240"
    mock_client.get.assert_called_once_with(expected_url, timeout=10.0)

@pytest.mark.asyncio
async def test_get_meeting_by_id_404():
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 404
    
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await _get_meeting_by_id(mock_client, "999999")
    
    assert excinfo.value.status_code == 500
    assert "Failed to fetch meeting with ID 999999" in excinfo.value.detail
```

### Model Testing Example
```python
from stadt_bonn_oparl.papers.models import TagCount

def test_tagcount_addition():
    \"\"\"Test that TagCount objects can be added correctly.\"\"\"
    t1 = TagCount(tag="environment", count=5)
    t2 = TagCount(tag="environment", count=3)
    
    result = t1 + t2
    
    assert result.tag == "environment"
    assert result.count == 8

def test_tagcount_addition_different_tags():
    \"\"\"Test that adding TagCount objects with different tags raises ValueError.\"\"\"
    t1 = TagCount(tag="environment", count=5)
    t2 = TagCount(tag="transport", count=3)
    
    with pytest.raises(ValueError):
        _ = t1 + t2
```

## Running Tests

### Run All Tests
```bash
uv run pytest
```

### Run Tests with Coverage
```bash
uv run pytest --cov
```

### Run Specific Test File
```bash
uv run pytest tests/test_get_meeting_by_id.py
```

### Run Specific Test Function
```bash
uv run pytest tests/test_get_meeting_by_id.py::test_get_meeting_by_id_success -v
```

### Run Tests with Verbose Output
```bash
uv run pytest -v
```

This testing guide should be followed when adding new tests to ensure consistency and maintainability across the project.