# pylint: skip-file
"""Test script for stop trigger for scheduler."""

import pytest
from unittest.mock import MagicMock

from stop_trigger import get_schedule_groups, delete_scheduler


def test_get_schedule_groups_success():
    mock_client = MagicMock()
    mock_paginator = MagicMock()
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


def test_delete_scheduler_success():
    mock_client = MagicMock()
    mock_logger = MagicMock()
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
