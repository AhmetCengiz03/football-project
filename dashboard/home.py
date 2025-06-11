"""Dashboard Script."""
import streamlit as st
import emoji
import plotly.graph_objects as go

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


if __name__ == "__main__":

    st.set_page_config(layout="wide")

    col1, col2, col3 = st.columns([1.5, 4, 1.5])

    with col1:
        with st.container():

            # Temporary examples
            selected_match = st.selectbox(
                "", list(matches_data.keys()), label_visibility="collapsed")

    with col2:
        match_info = matches_data[selected_match]

        col2a, col2b, col2c = st.columns(3)

        with col2a:
            st.markdown(f"<h1 style='text-align: left'>{match_info["home_team"]
                                                        } {match_info["home_logo"]}</h1>",
                        unsafe_allow_html=True)

        with col2b:
            st.markdown(f"<h1 style='text-align: center'>{match_info["home_score"]
                                                          } - {match_info["away_score"]}</h1>",
                        unsafe_allow_html=True)

        with col2c:
            st.markdown(f"<h1 style='text-align: right'>{match_info["away_logo"]
                                                         } {match_info["away_team"]} </h1>",
                        unsafe_allow_html=True)

    with col3:
        col2a, col2b, col2c = st.columns(3)
        with col2b:
            if st.button("PLAY/PAUSE GAME"):
                st.write("Game toggled!")

    with st.container():
        st.slider("Minute", min_value=0, max_value=90, step=1)

        num = st.columns(91)

        num[44].write(emoji.emojize(":football:"))
        num[90].write(emoji.emojize(":blue_circle:"))

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
