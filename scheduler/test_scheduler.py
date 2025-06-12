# pylint: skip-file
"""Test script for scheduler."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone

from scheduler import (
    get_all_daily_fixtures, get_data_from_fixtures,
    format_team_codes, create_match_schedule,
    manage_schedule_groups
)


def test_format_team_codes():
    team_1 = {"team_1_code": "MAN", "team_1_name": "Man United"}
    team_2 = {"team_2_code": "LIV", "team_2_name": "Liverpool"}
    formatted = format_team_codes(team_1, team_2)
    assert formatted == "man-liv"
