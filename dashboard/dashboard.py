"""Dashboard Script"""
import streamlit as st
import emoji
import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objects as go

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


if __name__ == "__main__":

    st.set_page_config(layout="wide")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container():

            st.markdown("<h3 style='text-align: center'>Select Match</h3>",
                        unsafe_allow_html=True)

            # Temporary examples
            selected_match = st.selectbox(
                "", list(matches_data.keys()), label_visibility="collapsed")

    with col2:
        match_info = matches_data[selected_match]
        st.markdown("<h2 style='text-align: center'>Score</h2>",
                    unsafe_allow_html=True)
        col2a, col2b, col2c = st.columns(3)

        with col2a:
            st.markdown(f"<h3 style='text-align: left'>{match_info["home_team"]}</h3>",
                        unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: left'>{match_info["home_logo"]}</h3>",
                        unsafe_allow_html=True)

        with col2b:
            st.markdown(f"<h3 style='text-align: center'>{match_info["home_score"]} - {match_info["away_score"]}</h3>",
                        unsafe_allow_html=True)

        with col2c:
            st.markdown(f"<h3 style='text-align: right'>{match_info["away_team"]}</h3>",
                        unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: right'>{match_info["away_logo"]}</h3>",
                        unsafe_allow_html=True)

    with col3:
        st.markdown("<h3 style='text-align: center'>Play/Pause</h3>",
                    unsafe_allow_html=True)
        col2a, col2b, col2c = st.columns(3)
        with col2b:
            if st.button("PLAY/PAUSE GAME"):
                st.write("Game toggled!")

    st.slider("Minute", min_value=0, max_value=90, step=1)

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
