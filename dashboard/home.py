"""Home page."""
import streamlit as st
import emoji
import plotly.graph_objects as go

from data import get_all_stats_for_selected_match, get_match_info_for_selected_match
from data_processing import calculate_score_from_events, create_timeline_df, create_slider


# Temporary data
matches_data = {
    "Arsenal vs Chelsea": {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "home_score": 2,
        "away_score": 1,
        "home_logo": emoji.emojize(":red_circle:"),
        "away_logo": emoji.emojize(":blue_circle:")
    },
    "Arsenal vs Liverpool": {
        "home_team": "Arsenal",
        "away_team": "Liverpool",
        "home_score": 3,
        "away_score": 2,
        "home_logo": emoji.emojize(":red_circle:"),
        "away_logo": emoji.emojize(":red_circle:")
    }
}


def create_top_bar(timeline_df, selected_minute):
    match_info = get_match_info_for_selected_match(
        st.session_state["selected_match_id"])

    col1, col2, col3 = st.columns([1.5, 4, 1.5])

    minute_data = timeline_df[timeline_df["match_minute"] == selected_minute]

    home_score = int(minute_data["home_score"].iloc[0])

    away_score = int(minute_data["away_score"].iloc[0])

    home_logo = match_info["home_logo_url"].iloc[0]

    away_logo = match_info["away_logo_url"].iloc[0]

    with col2:
        col2a, col2b, col2c = st.columns(3)
        with col2a:
            st.image(home_logo)

            st.markdown(f"<h1 style='text-align: left'>{st.session_state["home_team"]
                                                        }</h1>",
                        unsafe_allow_html=True)

        with col2b:
            st.markdown(f"<h1 style='text-align: center'>{home_score
                                                          } - {away_score}</h1>",
                        unsafe_allow_html=True)

        with col2c:
            st.image(away_logo)

            st.markdown(f"<h1 style='text-align: right'> {st.session_state["away_team"]} </h1>",
                        unsafe_allow_html=True)

    with col3:
        col2a, col2b, col2c = st.columns(3)
        with col2b:
            if st.button("PLAY/PAUSE GAME"):
                st.write("Game toggled!")


def main():

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
        st.markdown("<h3 style='text-align: center'>Radar Chart</h3>",
                    unsafe_allow_html=True)
        fig = go.Figure(data=go.Scatterpolar(
            r=[1, 5, 2, 2, 3],
            theta=['processing cost', 'mechanical properties', 'chemical stability', 'thermal stability',
                   'device integration'],
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

        st.plotly_chart(fig)

    # Match events/commentary
    with col3:
        st.markdown("<h3 style='text-align: center'>Match Events/Commentary</h1>",
                    unsafe_allow_html=True)


main()
