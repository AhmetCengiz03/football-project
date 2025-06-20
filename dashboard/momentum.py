"""Script to calculate momentum and create plot."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def calculate_momentum_score(timeline_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate momentum scores for both teams based on multiple stats."""

    df = timeline_df[["match_minute", "attacks_home", "attacks_away",
                      "danger_attacks_home", "danger_attacks_away",
                      "shots_home", "shots_away"]].copy()

    df["attacks_home_change"] = df["attacks_home"].diff().fillna(0)
    df["attacks_away_change"] = df["attacks_away"].diff().fillna(0)
    df["danger_home_change"] = df["danger_attacks_home"].diff().fillna(0)
    df["danger_away_change"] = df["danger_attacks_away"].diff().fillna(0)
    df["shots_home_change"] = df["shots_home"].diff().fillna(0)
    df["shots_away_change"] = df["shots_away"].diff().fillna(0)

    window = 5

    df["home_activity"] = (df["attacks_home_change"].rolling(window).sum() +
                           df["danger_home_change"].rolling(window).sum()
                           * 3 + df["shots_home_change"]*2)
    df["away_activity"] = (df["attacks_away_change"].rolling(window).sum() +
                           df["danger_away_change"].rolling(window).sum() *
                           3 + df["shots_away_change"]*2)

    df["momentum"] = df["home_activity"] - df["away_activity"]

    return df


def create_momentum_chart(df: pd.DataFrame, selected_minute: int) -> go.Figure:
    """Make a momentum chart for the match."""
    fig = go.Figure()
    fig.add_scatter(
        x=df["match_minute"], y=df["momentum"],
        mode="lines", name="Momentum",
        line={"width": 3, "color": 'white'}
    )
    fig.add_scatter(
        x=df["match_minute"],
        y=df["momentum"].where(df["momentum"] >= 0, 0),
        fill="tozeroy", mode="none",
        fillcolor="rgba(0,255,0,0.3)", name=st.session_state["home_team"]
    )
    fig.add_scatter(
        x=df["match_minute"],
        y=df["momentum"].where(df["momentum"] <= 0, 0),
        fill="tozeroy", mode="none",
        fillcolor="rgba(255,0,0,0.3)", name=st.session_state["away_team"]
    )
    fig.add_vline(x=selected_minute, line_dash="dash", line_color="white")
    return fig


def process_momentum_chart_creation(timeline_df: pd.DataFrame, selected_minute: int) -> go.Figure:
    """Main processing function for momentum chart."""
    df = calculate_momentum_score(timeline_df)
    momentum_chart = create_momentum_chart(df, selected_minute)
    return momentum_chart
