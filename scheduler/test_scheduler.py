# pylint: skip-file
"""Test script for scheduler."""

from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from scheduler import (
    get_data_from_fixtures,
    create_match_schedule,
    manage_schedule_groups,
    extract_team_data,
    process_daily_schedules,
    get_single_fixture
)


def test_extract_team_data_home(sample_fixture_data):
    team = sample_fixture_data[0]["participants"][0]

    result = extract_team_data(team, "home")

    expected = {
        "home_team_id": 1,
        "home_name": "Team A",
        "home_code": "AFC",
        "home_image": "url-a",
        "home_location": "home"
    }

    assert result == expected


def test_extract_team_data_away(sample_fixture_data):
    team = sample_fixture_data[0]["participants"][1]

    result = extract_team_data(team, "away")

    expected = {
        "away_team_id": 2,
        "away_name": "Team B",
        "away_code": "BFC",
        "away_image": "url-b",
        "away_location": "away"
    }

    assert result == expected


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


@patch("scheduler.HTTPSConnection")
@patch("scheduler.connect_to_scheduler_client")
@patch("scheduler.get_data_from_fixtures")
def test_process_daily_schedules_no_fixtures(mock_get_data, mock_connect, mock_https, config):
    mock_get_data.return_value = []
    mock_connect.return_value = MagicMock()
    mock_https.return_value = MagicMock()

    result = process_daily_schedules(config, "c17-football")

    assert result["statusCode"] == 200
    assert result["body"] == "No fixtures found today"
    assert result["matches"] == []


@patch("scheduler.HTTPSConnection")
@patch("scheduler.connect_to_scheduler_client")
@patch("scheduler.get_data_from_fixtures")
@patch("scheduler.manage_schedule_groups")
@patch("scheduler.create_match_schedule")
def test_process_daily_schedules_with_fixtures(mock_create_schedule, mock_manage_groups,
                                               mock_get_data, mock_connect, mock_https,
                                               sample_fixture_data, config):
    processed_fixtures = [get_single_fixture(sample_fixture_data[0])]
    mock_get_data.return_value = processed_fixtures
    mock_connect.return_value = MagicMock()
    mock_https.return_value = MagicMock()

    result = process_daily_schedules(config, "c17-football")

    assert result["statusCode"] == 200
    assert "Created 1 schedules" in result["body"]
    assert result["matches"] == processed_fixtures
