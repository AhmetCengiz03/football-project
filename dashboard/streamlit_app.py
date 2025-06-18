"""Dashboard run script."""
from dotenv import load_dotenv
import streamlit as st

from selector import create_match_selector


def main() -> None:
    load_dotenv()
    st.set_page_config(layout="wide")
    create_match_selector()

    pages = [
        st.Page(
            "home.py",
            title="home",
            icon=":material/home:"
        ),
        st.Page(
            "fixtures.py",
            title="fixtures",
            icon=":material/widgets:"
        )
    ]

    page = st.navigation(pages)
    page.run()


if __name__ == "__main__":
    main()
