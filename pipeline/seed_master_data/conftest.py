# pylint: skip-file
from unittest.mock import MagicMock

from pytest import fixture


@fixture
def mock_conn():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn


@fixture
def sample_event():
    """Sample event."""
    return [{
        "match_id": 101,
        "league_id": 200,
        "season_id": 300,
        "start_time": "2025-06-13 19:00:00",
        "team_data": [
            {
                "team_1_team_id": 1,
                "team_1_name": "Team A",
                "team_1_code": "AFC",
                "team_1_image": "url-a",
                "team_1_location": "home"
            },
            {
                "team_2_team_id": 2,
                "team_2_name": "Team B",
                "team_2_code": "BFC",
                "team_2_image": "url-b",
                "team_2_location": "away"
            }
        ]
    }]
