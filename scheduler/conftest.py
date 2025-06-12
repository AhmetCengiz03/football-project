"""Define fixtures for test_schedule file."""

from pytest import fixture


@fixture
def sample_fixture_data():
    return [{
        "id": 101,
        "league_id": 200,
        "season_id": 300,
        "name": "Team A vs Team B",
        "starting_at": "2025-06-13 19:00:00",
        "participants": [
            {
                "id": 1,
                "name": "Team A",
                "short_code": "AFC",
                "image_path": "url-a",
                "meta": {"location": "home"}
            },
            {
                "id": 2,
                "name": "Team B",
                "short_code": "BFC",
                "image_path": "url-b",
                "meta": {"location": "away"}
            }
        ]
    }]


@fixture
def config():
    return {
        "AWS_ACCESS_KEY_ID": "fake-key",
        "AWS_SECRET_ACCESS_KEY": "fake-secret",
        "API_KEY": "fake-api-key",
        "TARGET_ARN": "arn:aws:lambda:region:account:function:my-function",
        "ROLE_ARN": "arn:aws:iam::account:role/my-role"
    }
