"""
Tests for the aggregator module.
"""

import pytest
from datetime import datetime

from claude_code_cost_collector.aggregator import (
    aggregate_data,
    _aggregate_by_daily,
    _aggregate_by_monthly,
    _aggregate_by_project,
    _aggregate_by_session,
    _prepare_individual_entries,
    _create_aggregate_entry,
    _sort_aggregated_data,
    get_supported_granularities,
    validate_aggregation_input,
)
from claude_code_cost_collector.models import ProcessedLogEntry


class TestAggregateData:
    """Test cases for the main aggregate_data function."""

    def test_aggregate_data_daily(self):
        """Test daily aggregation through main function."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 11, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session2",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-3",
            ),
        ]

        result = aggregate_data(entries, "daily")

        assert "2025-05-09" in result
        assert result["2025-05-09"]["entry_count"] == 2
        assert result["2025-05-09"]["total_input_tokens"] == 300
        assert result["2025-05-09"]["total_output_tokens"] == 150
        assert result["2025-05-09"]["total_tokens"] == 450
        assert result["2025-05-09"]["total_cost_usd"] == 0.03

    def test_aggregate_data_invalid_granularity(self):
        """Test that invalid granularity raises ValueError."""
        entries = []

        with pytest.raises(ValueError, match="Invalid granularity"):
            aggregate_data(entries, "invalid")

    def test_aggregate_data_empty_entries(self):
        """Test aggregation with empty entry list."""
        result = aggregate_data([], "daily")
        assert result == {}

    def test_aggregate_data_invalid_entries_type(self):
        """Test that invalid entries type raises ValueError."""
        with pytest.raises(ValueError, match="entries must be a list"):
            aggregate_data("not a list", "daily")

    def test_aggregate_data_project(self):
        """Test project aggregation through main function."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 10, 11, 0, 0),
                date_str="2025-05-10",
                month_str="2025-05",
                project_name="project1",
                session_id="session2",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-4",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 11, 12, 0, 0),
                date_str="2025-05-11",
                month_str="2025-05",
                project_name="project2",
                session_id="session3",
                input_tokens=50,
                output_tokens=25,
                total_tokens=75,
                cost_usd=0.005,
                model="claude-3",
            ),
        ]

        result = aggregate_data(entries, "project")

        assert len(result) == 2
        assert "project1" in result
        assert "project2" in result

        # Check project1 (2 entries)
        project1_data = result["project1"]
        assert project1_data["entry_count"] == 2
        assert project1_data["total_input_tokens"] == 300
        assert project1_data["total_output_tokens"] == 150
        assert project1_data["total_tokens"] == 450
        assert project1_data["total_cost_usd"] == 0.03

        # Check project2 (1 entry)
        project2_data = result["project2"]
        assert project2_data["entry_count"] == 1
        assert project2_data["total_input_tokens"] == 50
        assert project2_data["total_output_tokens"] == 25
        assert project2_data["total_tokens"] == 75
        assert project2_data["total_cost_usd"] == 0.005


class TestAggregateByDaily:
    """Test cases for daily aggregation."""

    def test_single_day_multiple_entries(self):
        """Test aggregation of multiple entries on the same day."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 15, 30, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session2",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-3",
            ),
        ]

        result = _aggregate_by_daily(entries)

        assert len(result) == 1
        assert "2025-05-09" in result

        day_data = result["2025-05-09"]
        assert day_data["entry_count"] == 2
        assert day_data["total_input_tokens"] == 300
        assert day_data["total_output_tokens"] == 150
        assert day_data["total_tokens"] == 450
        assert day_data["total_cost_usd"] == 0.03
        assert day_data["models"] == ["claude-3"]
        assert day_data["projects"] == ["project1"]
        assert len(day_data["sessions"]) == 2

    def test_multiple_days(self):
        """Test aggregation across multiple days."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 10, 11, 0, 0),
                date_str="2025-05-10",
                month_str="2025-05",
                project_name="project2",
                session_id="session2",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-4",
            ),
        ]

        result = _aggregate_by_daily(entries)

        assert len(result) == 2
        assert "2025-05-09" in result
        assert "2025-05-10" in result

        # Check first day
        day1_data = result["2025-05-09"]
        assert day1_data["entry_count"] == 1
        assert day1_data["total_input_tokens"] == 100
        assert day1_data["models"] == ["claude-3"]
        assert day1_data["projects"] == ["project1"]

        # Check second day
        day2_data = result["2025-05-10"]
        assert day2_data["entry_count"] == 1
        assert day2_data["total_input_tokens"] == 200
        assert day2_data["models"] == ["claude-4"]
        assert day2_data["projects"] == ["project2"]

    def test_empty_entries(self):
        """Test daily aggregation with empty entry list."""
        result = _aggregate_by_daily([])
        assert result == {}


class TestAggregateByProject:
    """Test cases for project aggregation."""

    def test_single_project_multiple_entries(self):
        """Test aggregation of multiple entries for the same project."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 10, 11, 0, 0),
                date_str="2025-05-10",
                month_str="2025-05",
                project_name="project1",
                session_id="session2",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-4",
            ),
        ]

        result = _aggregate_by_project(entries)

        assert len(result) == 1
        assert "project1" in result

        project_data = result["project1"]
        assert project_data["entry_count"] == 2
        assert project_data["total_input_tokens"] == 300
        assert project_data["total_output_tokens"] == 150
        assert project_data["total_tokens"] == 450
        assert project_data["total_cost_usd"] == 0.03
        assert set(project_data["models"]) == {"claude-3", "claude-4"}
        assert project_data["projects"] == ["project1"]
        assert len(project_data["sessions"]) == 2

    def test_multiple_projects(self):
        """Test aggregation across multiple projects."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 11, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project2",
                session_id="session2",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-4",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 10, 12, 0, 0),
                date_str="2025-05-10",
                month_str="2025-05",
                project_name="project1",
                session_id="session3",
                input_tokens=50,
                output_tokens=25,
                total_tokens=75,
                cost_usd=0.005,
                model="claude-3",
            ),
        ]

        result = _aggregate_by_project(entries)

        assert len(result) == 2
        assert "project1" in result
        assert "project2" in result

        # Check project1 (2 entries)
        project1_data = result["project1"]
        assert project1_data["entry_count"] == 2
        assert project1_data["total_input_tokens"] == 150  # 100 + 50
        assert project1_data["total_output_tokens"] == 75  # 50 + 25
        assert project1_data["total_tokens"] == 225  # 150 + 75
        assert project1_data["total_cost_usd"] == 0.015  # 0.01 + 0.005
        assert project1_data["models"] == ["claude-3"]
        assert project1_data["projects"] == ["project1"]

        # Check project2 (1 entry)
        project2_data = result["project2"]
        assert project2_data["entry_count"] == 1
        assert project2_data["total_input_tokens"] == 200
        assert project2_data["total_output_tokens"] == 100
        assert project2_data["total_tokens"] == 300
        assert project2_data["total_cost_usd"] == 0.02
        assert project2_data["models"] == ["claude-4"]
        assert project2_data["projects"] == ["project2"]

    def test_empty_entries(self):
        """Test project aggregation with empty entry list."""
        result = _aggregate_by_project([])
        assert result == {}


class TestAggregateByMonthly:
    """Test cases for monthly aggregation."""

    def test_single_month_multiple_entries(self):
        """Test aggregation of multiple entries in the same month."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 15, 14, 30, 0),
                date_str="2025-05-15",
                month_str="2025-05",
                project_name="project2",
                session_id="session2",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-4",
            ),
        ]

        result = _aggregate_by_monthly(entries)

        assert len(result) == 1
        assert "2025-05" in result

        month_data = result["2025-05"]
        assert month_data["entry_count"] == 2
        assert month_data["total_input_tokens"] == 300
        assert month_data["total_output_tokens"] == 150
        assert month_data["total_tokens"] == 450
        assert month_data["total_cost_usd"] == 0.03
        assert set(month_data["models"]) == {"claude-3", "claude-4"}
        assert set(month_data["projects"]) == {"project1", "project2"}
        assert len(month_data["sessions"]) == 2

    def test_multiple_months(self):
        """Test aggregation across multiple months."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 6, 10, 11, 0, 0),
                date_str="2025-06-10",
                month_str="2025-06",
                project_name="project2",
                session_id="session2",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-4",
            ),
        ]

        result = _aggregate_by_monthly(entries)

        assert len(result) == 2
        assert "2025-05" in result
        assert "2025-06" in result

        # Check first month
        month1_data = result["2025-05"]
        assert month1_data["entry_count"] == 1
        assert month1_data["total_input_tokens"] == 100
        assert month1_data["models"] == ["claude-3"]
        assert month1_data["projects"] == ["project1"]

        # Check second month
        month2_data = result["2025-06"]
        assert month2_data["entry_count"] == 1
        assert month2_data["total_input_tokens"] == 200
        assert month2_data["models"] == ["claude-4"]
        assert month2_data["projects"] == ["project2"]

    def test_year_boundary_months(self):
        """Test aggregation across year boundaries."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2024, 12, 31, 23, 59, 0),
                date_str="2024-12-31",
                month_str="2024-12",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 1, 1, 0, 1, 0),
                date_str="2025-01-01",
                month_str="2025-01",
                project_name="project1",
                session_id="session2",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-3",
            ),
        ]

        result = _aggregate_by_monthly(entries)

        assert len(result) == 2
        assert "2024-12" in result
        assert "2025-01" in result

        # Verify separate aggregation despite same project
        dec_data = result["2024-12"]
        jan_data = result["2025-01"]
        assert dec_data["entry_count"] == 1
        assert jan_data["entry_count"] == 1
        assert dec_data["total_cost_usd"] == 0.01
        assert jan_data["total_cost_usd"] == 0.02

    def test_empty_entries(self):
        """Test monthly aggregation with empty entry list."""
        result = _aggregate_by_monthly([])
        assert result == {}

    def test_monthly_via_main_function(self):
        """Test monthly aggregation through main aggregate_data function."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 20, 15, 0, 0),
                date_str="2025-05-20",
                month_str="2025-05",
                project_name="project1",
                session_id="session2",
                input_tokens=150,
                output_tokens=75,
                total_tokens=225,
                cost_usd=0.015,
                model="claude-3",
            ),
        ]

        result = aggregate_data(entries, "monthly")

        assert "2025-05" in result
        assert result["2025-05"]["entry_count"] == 2
        assert result["2025-05"]["total_input_tokens"] == 250
        assert result["2025-05"]["total_output_tokens"] == 125
        assert result["2025-05"]["total_tokens"] == 375
        assert result["2025-05"]["total_cost_usd"] == 0.025


class TestAggregateBySession:
    """Test cases for session aggregation."""

    def test_single_session_multiple_entries(self):
        """Test aggregation of multiple entries in the same session."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 30, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-3",
            ),
        ]

        result = _aggregate_by_session(entries)

        assert len(result) == 1
        assert "session1" in result

        session_data = result["session1"]
        assert session_data["entry_count"] == 2
        assert session_data["total_input_tokens"] == 300
        assert session_data["total_output_tokens"] == 150
        assert session_data["total_tokens"] == 450
        assert session_data["total_cost_usd"] == 0.03
        assert session_data["models"] == ["claude-3"]
        assert session_data["projects"] == ["project1"]
        assert session_data["sessions"] == ["session1"]

    def test_multiple_sessions(self):
        """Test aggregation across multiple sessions."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 11, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project2",
                session_id="session2",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-4",
            ),
        ]

        result = _aggregate_by_session(entries)

        assert len(result) == 2
        assert "session1" in result
        assert "session2" in result

        # Check first session
        session1_data = result["session1"]
        assert session1_data["entry_count"] == 1
        assert session1_data["total_input_tokens"] == 100
        assert session1_data["models"] == ["claude-3"]
        assert session1_data["projects"] == ["project1"]

        # Check second session
        session2_data = result["session2"]
        assert session2_data["entry_count"] == 1
        assert session2_data["total_input_tokens"] == 200
        assert session2_data["models"] == ["claude-4"]
        assert session2_data["projects"] == ["project2"]

    def test_cross_project_session(self):
        """Test session that spans multiple projects."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 30, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project2",
                session_id="session1",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-3",
            ),
        ]

        result = _aggregate_by_session(entries)

        assert len(result) == 1
        assert "session1" in result

        session_data = result["session1"]
        assert session_data["entry_count"] == 2
        assert session_data["total_input_tokens"] == 300
        assert session_data["total_output_tokens"] == 150
        assert session_data["total_tokens"] == 450
        assert session_data["total_cost_usd"] == 0.03
        assert session_data["models"] == ["claude-3"]
        assert set(session_data["projects"]) == {"project1", "project2"}
        assert session_data["sessions"] == ["session1"]

    def test_empty_entries(self):
        """Test session aggregation with empty entry list."""
        result = _aggregate_by_session([])
        assert result == {}

    def test_session_aggregation_through_main_function(self):
        """Test session aggregation through main aggregate_data function."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 11, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session2",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-3",
            ),
        ]

        result = aggregate_data(entries, "session")

        assert len(result) == 2
        assert "session1" in result
        assert "session2" in result
        assert result["session1"]["entry_count"] == 1
        assert result["session2"]["entry_count"] == 1
        assert result["session1"]["total_cost_usd"] == 0.01
        assert result["session2"]["total_cost_usd"] == 0.02


class TestCreateAggregateEntry:
    """Test cases for the _create_aggregate_entry helper function."""

    def test_single_entry(self):
        """Test creating aggregate from single entry."""
        entry = ProcessedLogEntry(
            timestamp=datetime(2025, 5, 9, 10, 0, 0),
            date_str="2025-05-09",
            month_str="2025-05",
            project_name="project1",
            session_id="session1",
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            cost_usd=0.01,
            model="claude-3",
        )

        result = _create_aggregate_entry("test-key", [entry])

        assert result["key"] == "test-key"
        assert result["entry_count"] == 1
        assert result["total_input_tokens"] == 100
        assert result["total_output_tokens"] == 50
        assert result["total_tokens"] == 150
        assert result["total_cost_usd"] == 0.01
        assert result["models"] == ["claude-3"]
        assert result["projects"] == ["project1"]
        assert result["sessions"] == ["session1"]

    def test_empty_entries_raises_error(self):
        """Test that empty entry list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot create aggregate entry from empty list"):
            _create_aggregate_entry("test-key", [])

    def test_multiple_entries_aggregation(self):
        """Test aggregation of multiple entries."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 11, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project2",
                session_id="session2",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-4",
            ),
        ]

        result = _create_aggregate_entry("multi-test", entries)

        assert result["entry_count"] == 2
        assert result["total_input_tokens"] == 300
        assert result["total_output_tokens"] == 150
        assert result["total_tokens"] == 450
        assert result["total_cost_usd"] == 0.03
        assert set(result["models"]) == {"claude-3", "claude-4"}
        assert set(result["projects"]) == {"project1", "project2"}
        assert set(result["sessions"]) == {"session1", "session2"}


class TestUtilityFunctions:
    """Test cases for utility functions."""

    def test_get_supported_granularities(self):
        """Test that all expected granularities are supported."""
        granularities = get_supported_granularities()
        expected = ["daily", "monthly", "project", "session", "all"]
        assert granularities == expected

    def test_validate_aggregation_input_valid(self):
        """Test validation with valid input."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            )
        ]

        # Should not raise any exception
        validate_aggregation_input(entries, "daily")

    def test_validate_aggregation_input_invalid_entries_type(self):
        """Test validation with invalid entries type."""
        with pytest.raises(ValueError, match="entries must be a list"):
            validate_aggregation_input("not a list", "daily")

    def test_validate_aggregation_input_invalid_granularity(self):
        """Test validation with invalid granularity."""
        entries = []
        with pytest.raises(ValueError, match="Invalid granularity"):
            validate_aggregation_input(entries, "invalid")

    def test_validate_aggregation_input_invalid_entry_type(self):
        """Test validation with invalid entry objects."""
        entries = ["not a ProcessedLogEntry"]
        with pytest.raises(ValueError, match="All entries must be ProcessedLogEntry objects"):
            validate_aggregation_input(entries, "daily")


class TestPrepareIndividualEntries:
    """Test cases for individual entry preparation (all granularity)."""

    def test_prepare_individual_entries_single(self):
        """Test preparing single individual entry."""
        entry = ProcessedLogEntry(
            timestamp=datetime(2025, 5, 9, 10, 30, 45),
            date_str="2025-05-09",
            month_str="2025-05",
            project_name="project1",
            session_id="abcd1234-5678-90ef-abcd-1234567890ab",
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            cost_usd=0.01,
            model="claude-3",
        )

        result = _prepare_individual_entries([entry])

        assert len(result) == 1

        # Check the key format
        key = list(result.keys())[0]
        assert key.startswith("000000_20250509_103045_abcd1234")

        # Check the entry data
        entry_data = result[key]
        assert entry_data["entry_index"] == 0
        assert entry_data["total_cost_usd"] == 0.01
        assert entry_data["total_input_tokens"] == 100
        assert entry_data["total_output_tokens"] == 50
        assert entry_data["total_tokens"] == 150
        assert entry_data["entry_count"] == 1
        assert entry_data["project_name"] == "project1"
        assert entry_data["model"] == "claude-3"

    def test_prepare_individual_entries_multiple(self):
        """Test preparing multiple individual entries."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 30, 45),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="abcd1234-5678-90ef-abcd-1234567890ab",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 11, 15, 30),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project2",
                session_id="efgh5678-90ab-cdef-5678-90abcdef1234",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-4",
            ),
        ]

        result = _prepare_individual_entries(entries)

        assert len(result) == 2

        # Check that both entries are present with different keys
        keys = list(result.keys())
        assert keys[0].startswith("000000_20250509_103045_abcd1234")
        assert keys[1].startswith("000001_20250509_111530_efgh5678")

        # Check first entry
        entry1_data = result[keys[0]]
        assert entry1_data["entry_index"] == 0
        assert entry1_data["total_cost_usd"] == 0.01
        assert entry1_data["project_name"] == "project1"

        # Check second entry
        entry2_data = result[keys[1]]
        assert entry2_data["entry_index"] == 1
        assert entry2_data["total_cost_usd"] == 0.02
        assert entry2_data["project_name"] == "project2"

    def test_prepare_individual_entries_empty(self):
        """Test preparing empty individual entries list."""
        result = _prepare_individual_entries([])
        assert result == {}

    def test_aggregate_data_all_granularity(self):
        """Test aggregate_data function with 'all' granularity."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 30, 45),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="abcd1234-5678-90ef-abcd-1234567890ab",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 11, 15, 30),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project2",
                session_id="efgh5678-90ab-cdef-5678-90abcdef1234",
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
                cost_usd=0.02,
                model="claude-4",
            ),
        ]

        result = aggregate_data(entries, "all")

        assert len(result) == 2
        # Each entry should be individually represented, not aggregated
        for key, entry_data in result.items():
            assert entry_data["entry_count"] == 1
            assert "entry_index" in entry_data
            assert "total_cost_usd" in entry_data
            assert "total_input_tokens" in entry_data


class TestSortAggregatedData:
    """Test cases for the _sort_aggregated_data function."""

    def test_sort_by_input_tokens_ascending(self):
        """Test sorting by input tokens in ascending order."""
        data = {
            "item1": {"total_input_tokens": 200, "total_output_tokens": 50, "total_tokens": 250, "total_cost_usd": 0.02},
            "item2": {"total_input_tokens": 100, "total_output_tokens": 30, "total_tokens": 130, "total_cost_usd": 0.01},
            "item3": {"total_input_tokens": 300, "total_output_tokens": 70, "total_tokens": 370, "total_cost_usd": 0.03},
        }

        result = _sort_aggregated_data(data, "input", sort_desc=False)
        keys = list(result.keys())

        assert keys == ["item2", "item1", "item3"]  # 100, 200, 300

    def test_sort_by_input_tokens_descending(self):
        """Test sorting by input tokens in descending order."""
        data = {
            "item1": {"total_input_tokens": 200, "total_output_tokens": 50, "total_tokens": 250, "total_cost_usd": 0.02},
            "item2": {"total_input_tokens": 100, "total_output_tokens": 30, "total_tokens": 130, "total_cost_usd": 0.01},
            "item3": {"total_input_tokens": 300, "total_output_tokens": 70, "total_tokens": 370, "total_cost_usd": 0.03},
        }

        result = _sort_aggregated_data(data, "input", sort_desc=True)
        keys = list(result.keys())

        assert keys == ["item3", "item1", "item2"]  # 300, 200, 100

    def test_sort_by_output_tokens(self):
        """Test sorting by output tokens."""
        data = {
            "item1": {"total_input_tokens": 200, "total_output_tokens": 50, "total_tokens": 250, "total_cost_usd": 0.02},
            "item2": {"total_input_tokens": 100, "total_output_tokens": 30, "total_tokens": 130, "total_cost_usd": 0.01},
            "item3": {"total_input_tokens": 300, "total_output_tokens": 70, "total_tokens": 370, "total_cost_usd": 0.03},
        }

        result = _sort_aggregated_data(data, "output", sort_desc=False)
        keys = list(result.keys())

        assert keys == ["item2", "item1", "item3"]  # 30, 50, 70

    def test_sort_by_total_tokens(self):
        """Test sorting by total tokens."""
        data = {
            "item1": {"total_input_tokens": 200, "total_output_tokens": 50, "total_tokens": 250, "total_cost_usd": 0.02},
            "item2": {"total_input_tokens": 100, "total_output_tokens": 30, "total_tokens": 130, "total_cost_usd": 0.01},
            "item3": {"total_input_tokens": 300, "total_output_tokens": 70, "total_tokens": 370, "total_cost_usd": 0.03},
        }

        result = _sort_aggregated_data(data, "total", sort_desc=False)
        keys = list(result.keys())

        assert keys == ["item2", "item1", "item3"]  # 130, 250, 370

    def test_sort_by_cost_usd(self):
        """Test sorting by cost in USD."""
        data = {
            "item1": {"total_input_tokens": 200, "total_output_tokens": 50, "total_tokens": 250, "total_cost_usd": 0.02},
            "item2": {"total_input_tokens": 100, "total_output_tokens": 30, "total_tokens": 130, "total_cost_usd": 0.01},
            "item3": {"total_input_tokens": 300, "total_output_tokens": 70, "total_tokens": 370, "total_cost_usd": 0.03},
        }

        result = _sort_aggregated_data(data, "cost", sort_desc=False)
        keys = list(result.keys())

        assert keys == ["item2", "item1", "item3"]  # 0.01, 0.02, 0.03

    def test_sort_by_converted_cost(self):
        """Test sorting by converted cost when available."""
        data = {
            "item1": {
                "total_input_tokens": 200,
                "total_output_tokens": 50,
                "total_tokens": 250,
                "total_cost_usd": 0.02,
                "total_converted_cost": 2.0,
            },
            "item2": {
                "total_input_tokens": 100,
                "total_output_tokens": 30,
                "total_tokens": 130,
                "total_cost_usd": 0.01,
                "total_converted_cost": 1.0,
            },
            "item3": {
                "total_input_tokens": 300,
                "total_output_tokens": 70,
                "total_tokens": 370,
                "total_cost_usd": 0.03,
                "total_converted_cost": 3.0,
            },
        }

        result = _sort_aggregated_data(data, "cost", sort_desc=False)
        keys = list(result.keys())

        assert keys == ["item2", "item1", "item3"]  # 1.0, 2.0, 3.0

    def test_sort_empty_data(self):
        """Test sorting empty data returns empty dict."""
        result = _sort_aggregated_data({}, "input")
        assert result == {}

    def test_sort_invalid_field(self):
        """Test sorting with invalid field returns original data."""
        data = {
            "item1": {"total_input_tokens": 200, "total_output_tokens": 50, "total_tokens": 250, "total_cost_usd": 0.02},
            "item2": {"total_input_tokens": 100, "total_output_tokens": 30, "total_tokens": 130, "total_cost_usd": 0.01},
        }

        result = _sort_aggregated_data(data, "invalid_field")
        assert result == data

    def test_sort_missing_field_uses_zero(self):
        """Test sorting with missing field uses 0 as default value."""
        data = {
            "item1": {"total_input_tokens": 200, "total_output_tokens": 50},
            "item2": {"total_input_tokens": 100},  # missing total_output_tokens
            "item3": {"total_output_tokens": 30},  # missing total_input_tokens
        }

        result = _sort_aggregated_data(data, "output", sort_desc=False)
        keys = list(result.keys())

        # item2 has 0 output tokens, item3 has 30, item1 has 50
        assert keys == ["item2", "item3", "item1"]

    def test_aggregate_data_with_sort(self):
        """Test aggregate_data function with sort parameters."""
        entries = [
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 9, 10, 0, 0),
                date_str="2025-05-09",
                month_str="2025-05",
                project_name="project1",
                session_id="session1",
                input_tokens=300,
                output_tokens=50,
                total_tokens=350,
                cost_usd=0.03,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 10, 10, 0, 0),
                date_str="2025-05-10",
                month_str="2025-05",
                project_name="project1",
                session_id="session2",
                input_tokens=100,
                output_tokens=30,
                total_tokens=130,
                cost_usd=0.01,
                model="claude-3",
            ),
            ProcessedLogEntry(
                timestamp=datetime(2025, 5, 11, 10, 0, 0),
                date_str="2025-05-11",
                month_str="2025-05",
                project_name="project1",
                session_id="session3",
                input_tokens=200,
                output_tokens=40,
                total_tokens=240,
                cost_usd=0.02,
                model="claude-3",
            ),
        ]

        # Test sorting by input tokens descending
        result = aggregate_data(entries, "daily", sort_by="input", sort_desc=True)
        keys = list(result.keys())

        # Should be sorted by input tokens: 300, 200, 100
        assert keys == ["2025-05-09", "2025-05-11", "2025-05-10"]

        # Test sorting by cost ascending
        result = aggregate_data(entries, "daily", sort_by="cost", sort_desc=False)
        keys = list(result.keys())

        # Should be sorted by cost: 0.01, 0.02, 0.03
        assert keys == ["2025-05-10", "2025-05-11", "2025-05-09"]
