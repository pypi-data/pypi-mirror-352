import pytest
from pathlib import Path
from unittest.mock import patch
import tempfile
import shutil

from stadt_bonn_oparl.papers.models import (
    TagCount,
    TagAggregation,
    TagAggregationPeriod,
    PaperType,
    PaperAnalysis,
    Paper,
    UnifiedPaper,
)
from stadt_bonn_oparl.models import OParlAgendaItem, OParlFile


def test_tagcount_addition():
    t1 = TagCount(tag="foo", count=2)
    t2 = TagCount(tag="foo", count=3)
    result = t1 + t2
    assert isinstance(result, TagCount)
    assert result.tag == "foo"
    assert result.count == 5


def test_tagcount_addition_different_tags_raises():
    t1 = TagCount(tag="foo", count=2)
    t2 = TagCount(tag="bar", count=3)
    with pytest.raises(ValueError):
        _ = t1 + t2


def test_tagcount_equality_and_hash():
    t1 = TagCount(tag="foo", count=2)
    t2 = TagCount(tag="foo", count=2)
    t3 = TagCount(tag="foo", count=3)
    assert t1 == t2
    assert t1 != t3
    assert hash(t1) == hash(t2)
    assert hash(t1) != hash(t3)


def test_tagcount_repr_and_str():
    t = TagCount(tag="foo", count=7)
    assert repr(t) == "TagCount(tag='foo', count=7)"
    assert str(t) == "foo: 7"


def test_tagaggregation_model():
    tag_counts = [TagCount(tag="foo", count=1), TagCount(tag="bar", count=2)]
    agg = TagAggregation(
        period=TagAggregationPeriod.DAILY, data={"2024-01-01": tag_counts}
    )
    assert agg.period == TagAggregationPeriod.DAILY
    assert agg.data["2024-01-01"] == tag_counts


def test_papertype_enum():
    assert PaperType.antrag.value == "Antrag"
    assert PaperType["antrag"] == PaperType.antrag


def test_paperanalysis_model():
    analysis = PaperAnalysis(
        id="1",
        title="Test Paper",
        type=PaperType.antrag,
        creation_date="2024-01-01",
        responsible_department="Dept",
        decision_body=None,
        decision_date=None,
        subject_area="Area",
        geographic_scope="Scope",
        priority_level="High",
        main_proposal="Proposal",
        key_stakeholders=["Stakeholder1"],
        summary="Summary",
        tags=["tag1", "tag2"],
        next_steps=None,
        additional_notes=None,
    )
    assert analysis.id == "1"
    assert analysis.type == PaperType.antrag
    assert "tag1" in analysis.tags


def test_paper_model():
    paper = Paper(id="paper-1", metadata={"foo": "bar"}, content="Some markdown")
    assert paper.id == "paper-1"
    assert paper.metadata["foo"] == "bar"
    assert paper.content == "Some markdown"


def test_unifiedpaper_model():
    up = UnifiedPaper(
        paper_id="p1",
        metadata={"foo": "bar"},
        analysis={"summary": "test"},
        markdown_text="text",
        external_oparl_data={"key": None},
        enrichment_status="done",
    )
    assert up.paper_id == "p1"
    assert up.metadata["foo"] == "bar"
    assert up.analysis["summary"] == "test"
    assert up.markdown_text == "text"
    assert up.external_oparl_data["key"] is None
    assert up.enrichment_status == "done"


def test_tagaggregationperiod_enum():
    assert TagAggregationPeriod.DAILY.value == "daily"
    assert TagAggregationPeriod["WEEKLY"] == TagAggregationPeriod.WEEKLY


def test_tagcount_add_tagcount_same_tag():
    t1 = TagCount(tag="foo", count=2)
    t2 = TagCount(tag="foo", count=5)
    result = t1 + t2
    assert isinstance(result, TagCount)
    assert result.tag == "foo"
    assert result.count == 7


def test_tagcount_add_tagcount_different_tag_raises():
    t1 = TagCount(tag="foo", count=2)
    t2 = TagCount(tag="bar", count=3)
    with pytest.raises(ValueError):
        _ = t1 + t2


def test_tagcount_add_int():
    t = TagCount(tag="foo", count=4)
    result = t + 3
    assert isinstance(result, TagCount)
    assert result.tag == "foo"
    assert result.count == 7


def test_tagcount_add_invalid_type_returns_notimplemented():
    t = TagCount(tag="foo", count=1)

    class Dummy:
        pass

    dummy = Dummy()
    result = t.__add__(dummy)
    assert result is NotImplemented


def test_add_tag_count_new_date():
    agg = TagAggregation(period=TagAggregationPeriod.DAILY, data={})
    tag_count = TagCount(tag="foo", count=2)
    agg.add_tag_count("2024-01-01", tag_count)
    assert "2024-01-01" in agg.data
    assert agg.data["2024-01-01"][0] == tag_count


def test_add_tag_count_existing_date_new_tag():
    agg = TagAggregation(
        period=TagAggregationPeriod.DAILY,
        data={"2024-01-01": [TagCount(tag="foo", count=2)]},
    )
    new_tag_count = TagCount(tag="bar", count=3)
    agg.add_tag_count("2024-01-01", new_tag_count)
    tags = {tc.tag for tc in agg.data["2024-01-01"]}
    assert "foo" in tags and "bar" in tags
    assert any(tc.tag == "bar" and tc.count == 3 for tc in agg.data["2024-01-01"])


def test_add_tag_count_existing_date_existing_tag():
    agg = TagAggregation(
        period=TagAggregationPeriod.DAILY,
        data={"2024-01-01": [TagCount(tag="foo", count=2)]},
    )
    agg.add_tag_count("2024-01-01", TagCount(tag="foo", count=5))
    assert len(agg.data["2024-01-01"]) == 1
    assert agg.data["2024-01-01"][0].tag == "foo"
    assert agg.data["2024-01-01"][0].count == 7


def test_add_tag_count_multiple_dates_and_tags():
    agg = TagAggregation(period=TagAggregationPeriod.DAILY, data={})
    agg.add_tag_count("2024-01-01", TagCount(tag="foo", count=1))
    agg.add_tag_count("2024-01-02", TagCount(tag="bar", count=2))
    agg.add_tag_count("2024-01-01", TagCount(tag="bar", count=3))
    assert set(agg.data.keys()) == {"2024-01-01", "2024-01-02"}
    tags_0101 = {tc.tag for tc in agg.data["2024-01-01"]}
    tags_0102 = {tc.tag for tc in agg.data["2024-01-02"]}
    assert tags_0101 == {"foo", "bar"}
    assert tags_0102 == {"bar"}


class TestOParlAgendaItemDownloadAllFiles:
    """Test cases for the download_all_files method of OParlAgendaItem."""

    @pytest.fixture
    def temp_data_path(self):
        """Create a temporary directory for test data."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_agenda_item(self):
        """Create a sample agenda item with files."""
        return OParlAgendaItem(
            id="https://example.com/agenda/123",
            order=1,
            number="1.1",
            name="Test Agenda Item",
            resolutionFile={
                "id": "https://example.com/file/1",
                "name": "Resolution Document",
                "fileName": "resolution.pdf",
                "accessUrl": "https://example.com/download/resolution.pdf",
                "mimeType": "application/pdf",
            },
            auxiliaryFile=[
                {
                    "id": "https://example.com/file/2",
                    "name": "Supporting Document 1",
                    "fileName": "support1.pdf",
                    "accessUrl": "https://example.com/download/support1.pdf",
                    "mimeType": "application/pdf",
                },
                {
                    "id": "https://example.com/file/3",
                    "name": "Supporting Document 2",
                    "fileName": "support2.pdf",
                    "accessUrl": "https://example.com/download/support2.pdf",
                    "mimeType": "application/pdf",
                },
            ],
        )

    @pytest.fixture
    def agenda_item_no_files(self):
        """Create an agenda item with no files."""
        return OParlAgendaItem(
            id="https://example.com/agenda/456",
            order=2,
            number="2.1",
            name="Empty Agenda Item",
        )

    @patch("stadt_bonn_oparl.utils.download_file")
    def test_download_all_files_with_files(
        self, mock_download, sample_agenda_item, temp_data_path
    ):
        """Test downloading all files when agenda item has files."""
        # Mock successful downloads
        mock_download.return_value = (True, "pdf")

        results = sample_agenda_item.download_all_files(temp_data_path)

        # Should return 3 files (1 resolution + 2 auxiliary)
        assert len(results) == 3

        # All downloads should be successful
        for file_obj, success in results:
            assert isinstance(file_obj, OParlFile)
            assert success is True

        # Check that download_file was called 3 times
        assert mock_download.call_count == 3

        # Verify the agenda item directory was created
        expected_dir = temp_data_path / "agenda_item_123_Test_Agenda_Item"
        assert expected_dir.exists()
        assert expected_dir.is_dir()

    @patch("stadt_bonn_oparl.utils.download_file")
    def test_download_all_files_no_files(
        self, mock_download, agenda_item_no_files, temp_data_path
    ):
        """Test downloading when agenda item has no files."""
        results = agenda_item_no_files.download_all_files(temp_data_path)

        # Should return empty list
        assert len(results) == 0

        # download_file should not be called
        mock_download.assert_not_called()

        # Directory should still be created
        expected_dir = temp_data_path / "agenda_item_456_Empty_Agenda_Item"
        assert expected_dir.exists()

    @patch("stadt_bonn_oparl.utils.download_file")
    def test_download_all_files_mixed_success(
        self, mock_download, sample_agenda_item, temp_data_path
    ):
        """Test downloading when some files succeed and others fail."""
        # Mock mixed success/failure
        mock_download.side_effect = [(True, "pdf"), (False, "error"), (True, "pdf")]

        results = sample_agenda_item.download_all_files(temp_data_path)

        # Should return 3 results
        assert len(results) == 3

        # Check success/failure pattern
        assert results[0][1] is True  # First file succeeds
        assert results[1][1] is False  # Second file fails
        assert results[2][1] is True  # Third file succeeds

    @patch("stadt_bonn_oparl.utils.download_file")
    def test_download_all_files_default_path(
        self, mock_download, sample_agenda_item, temp_data_path
    ):
        """Test downloading with default data path when none provided."""
        mock_download.return_value = (True, "pdf")

        # Patch the DEFAULT_DATA_PATH to use a temp directory
        with patch("stadt_bonn_oparl.config.DEFAULT_DATA_PATH", temp_data_path):
            results = sample_agenda_item.download_all_files()

        # Should use default path and still work
        assert len(results) == 3

        # Check that download_file was called with correct paths under default directory
        for call_args in mock_download.call_args_list:
            download_path = call_args[0][1]  # Second argument is the path
            assert str(download_path).startswith(
                str(temp_data_path / "agenda_item_123_Test_Agenda_Item")
            )

    @patch("stadt_bonn_oparl.utils.download_file")
    def test_download_all_files_sanitized_directory_name(
        self, mock_download, temp_data_path
    ):
        """Test that directory names are properly sanitized."""
        agenda_item = OParlAgendaItem(
            id="https://example.com/agenda/special/chars!@#$%",
            order=1,
            number="1.1",
            name="Special/Characters: In Name!",
            resolutionFile={
                "id": "https://example.com/file/1",
                "name": "Test File",
                "accessUrl": "https://example.com/download/test.pdf",
            },
        )

        mock_download.return_value = (True, "pdf")

        agenda_item.download_all_files(temp_data_path)

        # Check that directory name is sanitized
        created_dirs = [d for d in temp_data_path.iterdir() if d.is_dir()]
        assert len(created_dirs) == 1

        dir_name = created_dirs[0].name
        # Should not contain special characters
        assert "/" not in dir_name
        assert ":" not in dir_name
        assert "!" not in dir_name
        assert "@" not in dir_name

    @patch("stadt_bonn_oparl.utils.download_file")
    def test_download_all_files_missing_filename(self, mock_download, temp_data_path):
        """Test downloading files that don't have explicit filenames."""
        agenda_item = OParlAgendaItem(
            id="https://example.com/agenda/123",
            order=1,
            number="1.1",
            name="Test Item",
            resolutionFile={
                "id": "https://example.com/file/1",
                "name": "Document Without Filename",
                "accessUrl": "https://example.com/download/doc1.pdf",
                # No filename field
            },
        )

        mock_download.return_value = (True, "pdf")

        results = agenda_item.download_all_files(temp_data_path)

        assert len(results) == 1

        # Should use the name field as filename when filename is missing
        call_args = mock_download.call_args_list[0]
        download_path = call_args[0][1]
        assert "Document_Without_Filename" in str(download_path)

    def test_get_all_files_method(self, sample_agenda_item):
        """Test the get_all_files helper method."""
        files = sample_agenda_item.get_all_files()

        # Should return 3 files (1 resolution + 2 auxiliary)
        assert len(files) == 3

        # All should be OParlFile instances
        for file_obj in files:
            assert isinstance(file_obj, OParlFile)

        # Check specific files
        file_names = [f.name for f in files]
        assert "Resolution Document" in file_names
        assert "Supporting Document 1" in file_names
        assert "Supporting Document 2" in file_names
