# pylint: skip-file
"""Test script for scheduler."""

from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from scheduler import (
    get_data_from_fixtures,
    create_match_schedule,
    manage_schedule_groups
)


@patch("scheduler.get_all_daily_fixtures")
def test_get_data_from_fixtures(mock_get_all, sample_fixture_data, config):
    conn = MagicMock()
    mock_get_all.return_value = sample_fixture_data

    data = get_data_from_fixtures(conn, config)

    assert data[0]["fixture_name"] == "Team A vs Team B"
    assert "team_data" in data[0]


def test_create_match_schedule_success(sample_fixture_data, config):
    scheduler_client = MagicMock()

    fixture = sample_fixture_data[0]
    match = {
        "match_id": fixture["id"],
        "start_time": fixture["starting_at"],
        "fixture_name": fixture["name"],
        "team_data": [
            {
                "team_1_code": fixture["participants"][0]["short_code"],
                "team_1_name": fixture["participants"][0]["name"]
            },
            {
                "team_2_code": fixture["participants"][1]["short_code"],
                "team_2_name": fixture["participants"][1]["name"]
            }
        ]
    }
    group_name = "c17-football-2025-06-13-fixtures"

    create_match_schedule(scheduler_client, match,
                          group_name, config, 'c17-football')
    assert scheduler_client.create_schedule.called
    schedule = scheduler_client.create_schedule.call_args[1]
    assert schedule["Name"].startswith(
        "c17-football-101")
    assert schedule["GroupName"] == group_name
    assert schedule["ScheduleExpression"] == 'cron(* * * * ? *)'


def test_manage_schedule_groups_deletes_old():
    scheduler_client = MagicMock()

    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    valid_group = f"c17-football-{today}-fixtures"

    scheduler_client.get_paginator.return_value.paginate.return_value = [{
        "ScheduleGroups": [
            {"Name": valid_group},
            {"Name": "c17-football-2024-01-01-fixtures"},
        ]
    }]

    manage_schedule_groups(
        scheduler_client, f"c17-football-{tomorrow}-fixtures", 'c17-football')
    assert scheduler_client.delete_schedule_group.called
    assert scheduler_client.delete_schedule_group.call_args[
        1]["Name"] == "c17-football-2024-01-01-fixtures"
