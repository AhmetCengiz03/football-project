"""Dashboard run script."""
import streamlit as st

from selector import create_match_selector

pages = [
    st.Page(
        "home.py",
        title="home",
        icon=":material/home:"
    ),
    st.Page(
        "page2.py",
        title="page2",
        icon=":material/widgets:"
    )
]

page = st.navigation(pages)

create_match_selector()

page.run()
