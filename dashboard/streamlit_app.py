"""Dashboard run script."""
from dotenv import load_dotenv
import streamlit as st

from selector import create_match_selector


def main() -> None:
    """Main function for generating all pages."""
    load_dotenv()
    st.set_page_config(layout="wide")
    create_match_selector()

    pages = [
        st.Page(
            "home.py",
            title="Home",
            icon=":material/home:",
        ),
        st.Page(
            "fixtures.py",
            title="Fixtures",
            icon=":material/widgets:"
        ),
        st.Page(
            "subscription.py",
            title="Subscription",
            icon=":material/widgets:"
        )
    ]

    page = st.navigation(pages)
    page.run()


if __name__ == "__main__":
    main()
