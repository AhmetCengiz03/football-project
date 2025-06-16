"""Home page."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from data import get_match_info_for_selected_match
from timeline import create_timeline_df, create_slider


def create_top_bar(timeline_df: pd.DataFrame, selected_minute: int) -> None:
    """Create the top bar of the page."""
    match_info = get_match_info_for_selected_match(
        st.session_state["selected_match_id"])

    _, col2, col3 = st.columns([1.5, 4, 1.5])

    minute_data = timeline_df[timeline_df["match_minute"] == selected_minute]
    home_score = int(minute_data["home_score"].iloc[0])
    away_score = int(minute_data["away_score"].iloc[0])
    home_logo = match_info["home_logo_url"].iloc[0]
    away_logo = match_info["away_logo_url"].iloc[0]

    with col2:
        col2a, col2b, col2c = st.columns(3)
        with col2a:
            st.image(home_logo, width=100)
            st.markdown(f"<h1 style='text-align: center'>{st.session_state["home_team"]
                                                          }</h1>",
                        unsafe_allow_html=True)

        with col2b:
            st.markdown(f"<h1 style='text-align: center'>{home_score
                                                          } - {away_score}</h1>",
                        unsafe_allow_html=True)

        with col2c:
            st.image(away_logo, width=100)
            st.markdown(f"<h1 style='text-align: center'> {st.session_state["away_team"]} </h1>",
                        unsafe_allow_html=True)

    with col3:
        col2a, col2b, col2c = st.columns(3)
        with col2b:
            if st.button("PLAY/PAUSE GAME"):
                st.write("Game toggled!")


def create_match_progression_radar(timeline_df: pd.DataFrame, selected_minute: int) -> go.Figure:
    """Create radar plot for match statistics."""
    data_up_to_minute = timeline_df[timeline_df["match_minute"]
                                    == selected_minute]

    # I may calculate averages here? For now it is just the stats for this minute for proof of concept
    latest_data = data_up_to_minute.iloc[-1]

    categories = [
        "possession_home",
        "shots_home",
        "corners_home",
        "tackles_home"
    ]

    values = [
        latest_data.get("possession_home", 0),
        latest_data.get("shots_home", 0),
        latest_data.get("corners_home", 0),
        latest_data.get("tackles_home", 0)
    ]
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True
            ),
        ),
        showlegend=False
    )

    return fig


def create_home_page() -> None:
    """Main function to create the home page."""
    timeline_df = create_timeline_df()

    selected_minute = create_slider(timeline_df)

    create_top_bar(timeline_df, selected_minute)

    col1, col2, col3 = st.columns([1.5, 4, 1.5])

    # Game momentum/pressure chart

    col1, col2, col3 = st.columns(3)

    # Minute by minute stats comparison
    with col1:
        st.markdown("<h3 style='text-align: center'>Minute by minute statistics</h3>",
                    unsafe_allow_html=True)

    # Radar chart
    with col2:
        fig = create_match_progression_radar(timeline_df, selected_minute)

        st.plotly_chart(fig)

    # Match events/commentary
    with col3:
        st.markdown("<h3 style='text-align: center'>Match Events/Commentary</h1>",
                    unsafe_allow_html=True)


create_home_page()
