# pylint: skip-file
"""Tests for the extract.py script."""

from pytest import raises
from unittest.mock import MagicMock

from extract import prepare_data, build_scrape_url, scrape_live_match


def test_prepare_data_removes_keys():

    data = {
        "rate_limit": {"calls_left": 2999},
        "subscription": {"plan": "worldwide"},
        "timezone": "UTC",
        "data": {}
    }
    prepared_data = prepare_data(data)

    assert "subscription" not in prepared_data
    assert "timezone" not in prepared_data


def test_prepare_data_adds_timestamp():

    data = {
        "rate_limit": {"calls_left": 2999},
        "subscription": {"plan": "worldwide"},
        "timezone": "UTC",
        "data": {}
    }
    prepared_data = prepare_data(data)

    assert "request_timestamp" in prepared_data["data"]


def test_prepare_data_raises_keyerror():

    data = {
        "subscription": {"plan": "worldwide"},
        "timezone": "UTC"
    }
    with raises(KeyError):
        prepare_data(data)


def test_build_url_builds_correctly_with_name():
    url = build_scrape_url("Scotland", "MYTOKEN")

    assert "participantSearch:Scotland" in url
    assert "api_token=MYTOKEN" in url


def test_build_url_builds_correctly_with_id():
    url = build_scrape_url(19194929, "MYTOKEN")

    assert "fixtures/19194929?" in url
    assert "api_token=MYTOKEN" in url


def test_build_url_type_error_with_bad_type():

    with raises(TypeError):
        build_scrape_url(["Scotland"], "MYTOKEN")


def test_scrape_live_match_scrapes_once_and_is_successful():

    mock_conn = MagicMock()
    mock_response = MagicMock()
    mock_data = MagicMock()

    mock_conn.getresponse.return_value = mock_response
    mock_response.read.return_value = mock_data

    mock_data.decode.return_value = '{"match_id": "101010", "fixture_name": "Scotland vs Hungary"}'
    mock_response.status = 200

    response = scrape_live_match("fixtures", mock_conn)
    assert response == {"match_id": "101010",
                        "fixture_name": "Scotland vs Hungary"}
