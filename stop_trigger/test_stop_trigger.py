# pylint: skip-file
"""Test script for stop trigger for scheduler."""

import pytest
from stop_trigger import format_team_names
from unittest.mock import Mock, patch, MagicMock

from stop_trigger import get_schedule_groups, delete_scheduler


def test_format_team_codes_valid_codes():
    team_1 = "team1"
    team_2 = "team2"
    formatted = format_team_names(team_1, team_2)
    assert formatted == "team1-team2"


def test_format_team_names_long_names_truncated():
    team_1 = "A" * 30
    team_2 = "B" * 30
    result = format_team_names(team_1, team_2)
    assert len(result) == 50
    assert result.endswith("b" * 19)


def test_get_schedule_groups_success():
    mock_client = Mock()
    mock_paginator = Mock()
    mock_client.get_paginator.return_value = mock_paginator

    mock_paginator.paginate.return_value = [
        {
            "ScheduleGroups": [
                {"Name": "c17-football-2025-06-12-fixtures"},
                {"Name": "c17-football-2025-06-13-fixtures"},
                {"Name": "random-group"},
                {"Name": "c17-football-2025-06-14-fixtures"}
            ]
        }
    ]
    result = get_schedule_groups(mock_client, "c17-football")

    expected = [
        "c17-football-2025-06-12-fixtures",
        "c17-football-2025-06-13-fixtures",
        "c17-football-2025-06-14-fixtures"
    ]
    assert result == expected


def test_delete_scheduler_success_first_group():
    mock_client = Mock()
    mock_logger = Mock()
    result = delete_scheduler(
        mock_client,
        "test-schedule",
        ["group1", "group2"],
        mock_logger
    )

    assert mock_client.delete_schedule.call_count == 2
    mock_client.delete_schedule.assert_any_call(
        Name="test-schedule",
        GroupName="group1"
    )
    mock_client.delete_schedule.assert_any_call(
        Name="test-schedule",
        GroupName="group2"
    )
    assert result is True
