import pytest
from unittest.mock import MagicMock, patch

from extract_transform import (
    validate_required_keys, validate_team_data, get_team_by_location,
    extract_team_info, validate_timestamp, fetch_entity_name,
    check_entity_in_db, check_competition_exists, check_season_exists,
    check_team_exists
)


def test_validate_required_keys_missing_field():
    """Test validation failure with missing field."""

    with pytest.raises(ValueError, match="Missing field: league_id"):
        validate_required_keys({"match_id": "123"})


def test_validate_team_data_success(sample_event):
    """Test successful team data validation."""
    team1, team2 = validate_team_data(sample_event[0]["team_data"])

    assert team1["team_1_team_id"] == 1
    assert team2["team_2_team_id"] == 2


def test_validate_team_data_wrong_count():
    """Test team data validation with wrong number of teams."""
    with pytest.raises(ValueError, match="Team data must contain exactly two teams"):
        validate_team_data([{"team": "only_one"}])


def test_validate_timestamp_invalid():
    """Test timestamp validation with invalid format."""
    with pytest.raises(ValueError, match="Invalid 'start_time' format"):
        validate_timestamp("invalid-timestamp")


def test_get_team_by_location_home(sample_event):
    """Test getting home team by location."""
    team1, team2 = sample_event[0]["team_data"]
    home_team = get_team_by_location(team1, team2, "home")

    assert home_team["team_1_location"] == "home"


def test_get_team_by_location_away(sample_event):
    """Test getting away team by location."""
    team1, team2 = sample_event[0]["team_data"]
    away_team = get_team_by_location(team1, team2, "away")

    assert away_team["team_2_location"] == "away"


def test_get_team_by_location_not_found(sample_event):
    """Test error when location not found."""
    team1, team2 = sample_event[0]["team_data"]

    with pytest.raises(ValueError, match="No team found for location: neutral"):
        get_team_by_location(team1, team2, "neutral")


def test_extract_team_info_team1(sample_event):
    """Test extracting team1 info."""

    result = extract_team_info(sample_event[0]["team_data"][0])

    assert result == {
        "team_id": 1,
        "name": "Team A",
        "short_code": "AFC",
        "logo_url": "url-a"
    }


def test_extract_team_info_team2(sample_event):
    """Test extracting team2 info."""

    result = extract_team_info(sample_event[0]["team_data"][1])

    assert result == {
        "team_id": 2,
        "name": "Team B",
        "short_code": "BFC",
        "logo_url": "url-b"
    }


@patch('extract_transform.HTTPSConnection')
@patch('extract_transform.ENV', {"SPORTMONKS_API_TOKEN": "test-token"})
def test_fetch_entity_name_success(mock_https):
    """Test successful entity name fetching."""
    mock_conn = MagicMock()
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = b'{"data": {"name": "Premier League"}}'

    mock_https.return_value = mock_conn
    mock_conn.getresponse.return_value = mock_response

    result = fetch_entity_name("leagues", 200)

    assert result == "Premier League"
    mock_conn.request.assert_called_once_with(
        "GET",
        "/v3/football/leagues/200?api_token=test-token",
        headers={}
    )


@patch('extract_transform.HTTPSConnection')
@patch('extract_transform.ENV', {"SPORTMONKS_API_TOKEN": "test-token"})
def test_fetch_entity_name_api_error(mock_https):
    """Test entity name fetching with API error."""
    mock_conn = MagicMock()
    mock_response = MagicMock()
    mock_response.status = 404
    mock_response.reason = "Not Found"

    mock_https.return_value = mock_conn
    mock_conn.getresponse.return_value = mock_response

    with pytest.raises(ValueError, match="Failed to fetch leagues with ID 200: 404 Not Found"):
        fetch_entity_name("leagues", 200)


def test_check_entity_in_db_found(mock_conn):
    """Test checking entity in database when found."""
    cursor = mock_conn.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = ("Premier League",)

    result = check_entity_in_db(
        mock_conn, "competition", "competition_id", "competition_name", 200)

    assert result == "Premier League"
    cursor.execute.assert_called_once_with(
        "SELECT competition_name FROM competition WHERE competition_id = %s",
        (200,)
    )


def test_check_entity_in_db_not_found(mock_conn):
    """Test checking entity in database when not found."""
    cursor = mock_conn.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = None

    result = check_entity_in_db(
        mock_conn, "competition", "competition_id", "competition_name", 200)

    assert not result


@patch('extract_transform.fetch_entity_name')
def test_check_competition_not_exists_in_db(mock_fetch, mock_conn):
    """Test fallback to API when competition not in DB."""
    mock_fetch.return_value = "Premier League"

    cursor = mock_conn.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = None

    name, insert_flag = check_competition_exists(mock_conn, 200)

    assert name == "Premier League"
    assert insert_flag
    mock_fetch.assert_called_once_with("leagues", 200)


def test_check_season_exists_in_db(mock_conn):
    cursor = mock_conn.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = ("2024/25",)

    name, insert_flag = check_season_exists(mock_conn, 300)
    assert name == "2024/25"
    assert not insert_flag


@patch('extract_transform.fetch_entity_name')
def test_check_team_exists_team1_not_in_db(mock_fetch, mock_conn):
    team_data = {
        "team_1_team_id": 101,
        "team_1_name": "Team A"
    }
    cursor = mock_conn.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = None
    mock_fetch.return_value = "Team A Updated"

    insert_needed = check_team_exists(mock_conn, team_data)

    assert insert_needed
    assert team_data["team_1_name"] == "Team A Updated"
    mock_fetch.assert_called_once_with("teams", 101)


def test_check_team_exists_team2_in_db(mock_conn):
    team_data = {
        "team_2_team_id": 102,
        "team_2_name": "Team B"
    }
    cursor = mock_conn.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = ("Team B",)

    insert_needed = check_team_exists(mock_conn, team_data)

    assert not insert_needed
