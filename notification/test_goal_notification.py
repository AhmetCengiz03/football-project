"""Tests for create goal notification."""


from goal_notification import create_goal_message


def test_create_goal_message():
    goal = {"minute": 12, "player_name": "Salah", "team_id": 1}
    assert create_goal_message(goal) == "GOAL! 12' Salah scores for 1."
