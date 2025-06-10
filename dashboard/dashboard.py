"""Dashboard Script"""
import streamlit as st


matches_data = {
    "Arsenal vs Chelsea": {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "home_score": 2,
        "away_score": 1
    },
    "Arsenal vs Liverpool": {
        "home_team": "Arsenal",
        "away_team": "Liverpool",
        "home_score": 3,
        "away_score": 2
    }
}


if __name__ == "__main__":

    st.set_page_config(layout="wide")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container():

            st.markdown("<h3 style='text-align: center'>SELECT MATCH</h1>",
                        unsafe_allow_html=True)

            # Temporary examples
            selected_match = st.selectbox(
                "", list(matches_data.keys()), label_visibility="collapsed")

    with col2:
        match_info = matches_data[selected_match]
        st.markdown("<h2 style='text-align: center'>Score</h1>",
                    unsafe_allow_html=True)
        col2a, col2b, col2c = st.columns(3)

        with col2a:
            st.markdown(f"<h5 style='text-align: left'>{match_info["home_team"]}</h1>",
                        unsafe_allow_html=True)

        with col2b:
            st.markdown(f"<h5 style='text-align: center'>{match_info["home_score"]} - {match_info["away_score"]}</h1>",
                        unsafe_allow_html=True)

        with col2c:
            st.markdown(f"<h5 style='text-align: right'>{match_info["away_team"]}</h1>",
                        unsafe_allow_html=True)

    with col3:
        st.markdown("<h3 style='text-align: center'>PLAY/PAUSE</h1>",
                    unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center'>Football Statistics</h1>",
                unsafe_allow_html=True)

    st.slider("Minute", min_value=0, max_value=90, step=1)

    # Game momentum/pressure chart

    col1, col2, col3 = st.columns(3)

    # Minute by minute stats comparison
    with col1:
        pass

    # Radar chart
    with col2:
        pass

    # Match events/commentary
    with col3:
        pass
