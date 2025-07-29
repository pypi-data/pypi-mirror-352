from stadt_bonn_oparl.api.helpers import _process_organization
from stadt_bonn_oparl.api.config import UPSTREAM_API_URL, SELF_API_URL


class TestProcessOrganization:
    """Test cases for the _process_organization helper function."""

    def test_process_organization_with_all_fields(self):
        """Test processing an organization with all fields present."""
        org = {
            "id": "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=1",
            "membership": [
                "https://www.bonn.sitzung-online.de/public/oparl/memberships?id=123",
                "https://www.bonn.sitzung-online.de/public/oparl/memberships?id=456"
            ],
            "location": {
                "id": "https://www.bonn.sitzung-online.de/public/oparl/locations?id=789"
            },
            "meeting": "https://www.bonn.sitzung-online.de/public/oparl/meetings?organization=1"
        }

        _process_organization(org)

        # Check membership processing
        assert org["membership"] is None
        assert org["membership_ref"] == [
            "http://localhost:8000/memberships?id=123",
            "http://localhost:8000/memberships?id=456"
        ]

        # Check location processing
        assert org["location"] is None
        assert org["location_ref"] == "http://localhost:8000/locations?id=789"

        # Check meeting processing
        assert org["meeting"] is None
        assert org["meeting_ref"] == "http://localhost:8000/meetings?organization=1"

    def test_process_organization_with_missing_fields(self):
        """Test processing an organization with missing optional fields."""
        org = {
            "id": "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=1"
        }

        _process_organization(org)

        # All ref fields should be None when original fields are missing
        assert org["membership_ref"] is None
        assert org["location_ref"] is None
        assert org["meeting_ref"] is None

        # Original fields should be set to None
        assert org["membership"] is None
        assert org["location"] is None
        assert org["meeting"] is None

    def test_process_organization_with_empty_membership(self):
        """Test processing an organization with empty membership list."""
        org = {
            "id": "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=1",
            "membership": []
        }

        _process_organization(org)

        assert org["membership"] is None
        assert org["membership_ref"] == []

    def test_process_organization_with_null_membership(self):
        """Test processing an organization with null membership field."""
        org = {
            "id": "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=1",
            "membership": None
        }

        # This should not raise an exception
        _process_organization(org)

        assert org["membership"] is None
        assert org["membership_ref"] is None

    def test_process_organization_with_null_location(self):
        """Test processing an organization with null location field."""
        org = {
            "id": "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=1",
            "location": None
        }

        # This should not raise an exception
        _process_organization(org)

        assert org["location"] is None
        assert org["location_ref"] is None

    def test_process_organization_with_null_meeting(self):
        """Test processing an organization with null meeting field."""
        org = {
            "id": "https://www.bonn.sitzung-online.de/public/oparl/organizations?typ=gr&id=1",
            "meeting": None
        }

        # This should not raise an exception
        _process_organization(org)

        assert org["meeting"] is None
        assert org["meeting_ref"] is None

    def test_process_organization_url_replacement(self):
        """Test that URLs are correctly replaced from upstream to self API."""
        org = {
            "membership": [
                "https://www.bonn.sitzung-online.de/public/oparl/memberships?id=123"
            ],
            "location": {
                "id": "https://www.bonn.sitzung-online.de/public/oparl/locations?id=456"
            },
            "meeting": "https://www.bonn.sitzung-online.de/public/oparl/meetings?organization=1"
        }

        _process_organization(org)

        # Verify URL replacements
        assert UPSTREAM_API_URL not in org["membership_ref"][0]
        assert SELF_API_URL in org["membership_ref"][0]
        assert UPSTREAM_API_URL not in org["location_ref"]
        assert SELF_API_URL in org["location_ref"]
        assert UPSTREAM_API_URL not in org["meeting_ref"]
        assert SELF_API_URL in org["meeting_ref"]

    def test_process_organization_modifies_in_place(self):
        """Test that the function modifies the organization dictionary in place."""
        org = {
            "id": "test",
            "membership": ["https://www.bonn.sitzung-online.de/public/oparl/memberships?id=123"]
        }
        original_org = org

        _process_organization(org)

        # Should be the same object, modified in place
        assert org is original_org
        assert "membership_ref" in org
        assert org["membership"] is None