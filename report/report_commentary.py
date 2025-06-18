import json

from pydantic import BaseModel
from openai import OpenAI
import pandas as pd

from report_data import get_match_data


class MatchEvent(BaseModel):
    minute: int
    half: int
    event_type: str
    team_name: str
    player_name: str = None
    related_player_name: str = None
    commentary: str


class MatchPeriodSummary(BaseModel):
    period: str
    key_stats: str
    commentary: str


class MatchReport(BaseModel):
    match_title: str
    final_score: str
    match_date: str
    competition: str
    season: str
    match_summary: str
    period_summaries: list[MatchPeriodSummary]
    key_events: list[MatchEvent]
    final_thoughts: str


def get_openai_client(config: dict):
    """Get the Open AI client."""
    return OpenAI(
        api_key=config["OPENAI_API_KEY"]
    )


def create_match_analysis_prompt(match_info: dict, stats_data: pd.DataFrame, events_data: pd.DataFrame) -> str:
    """Create detailed prompt for AI analysis."""

    final_stats = stats_data.iloc[-1] if not stats_data.empty else {}
    total_shots_home = final_stats.get('shots_home', 0)
    total_shots_away = final_stats.get('shots_away', 0)
    final_possession_home = final_stats.get('possession_home', 50)

    significant_events = events_data[events_data['event_type'].isin(
        ['goal', 'redcard', 'yellowcard', 'substitution'])].to_dict('records')

    prompt = f"""
    You must analyse this football match and create a comprehensive report using only the data below.:

    MATCH DETAILS:
    - Home Team: {match_info['home_team']}
    - Away Team: {match_info['away_team']}
    - Date: {match_info['match_date']}
    - Competition: {match_info['competition_name']}
    - Season: {match_info['season_name']}

    HOME STATISTICS:
    - Total Shots: {match_info['home_team']} {total_shots_home} 
    - Final Possession: {match_info['home_team']} {final_possession_home}%

    AWAY STATISTICS:
    - Total Shots: {match_info['away_team']} {total_shots_away} 
    - Final Possession: {match_info['away_team']} {100-final_possession_home}%

    MINUTE-BY-MINUTE STATS:
    {stats_data.to_string() if not stats_data.empty else "No detailed stats available"}

    KEY MATCH EVENTS:
    {significant_events}

    1. An engaging match title
    2. Final score - count the number of "goal" events for each team.
    3. Overall match summary
    4. Period-by-period analysis (First Half, Second Half, etc.)
    5. Commentary on key events with specific player and team references
    6. Final thoughts on the match

    You must be:
    - Engaging and professional, similar tone to British football commentary
    - References specific players and teams
    - Mentions tactical aspects when relevant
    - Highlights turning points in the match
    - Uses football terminology appropriately

    DO NOT MAKE UP ANYTHING.
    DO NOT HALLUCINATE.

    """
    return prompt


def generate_match_report(config: dict, match_id: int) -> MatchReport:
    """Generate AI-powered match report."""
    client = get_openai_client(config)

    match_data = get_match_data(config, match_id)
    match_info = match_data['match_info']

    stats_data = pd.DataFrame(match_data['match_stats'])
    events_data = pd.DataFrame(match_data['match_events'])

    prompt = create_match_analysis_prompt(
        match_info, stats_data, events_data)
    chat_completion = client.beta.chat.completions.parse(
        messages=[
            {"role": "system", "content": "You are an expert football commentator and analyst. Generate engaging match reports with insightful commentary using only the stats provided."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        model="gpt-4.1-nano",
        response_format=MatchReport,
    )

    try:
        return MatchReport.model_validate(json.loads(chat_completion.choices[0].message.content))
    except (TypeError, json.JSONDecodeError):
        return MatchReport.model_validate(json.loads(chat_completion.choices[0].message.refusal))
