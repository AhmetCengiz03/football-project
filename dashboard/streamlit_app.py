"""Dashboard run script."""
import streamlit as st

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
page.run()

with st.sidebar.container(height=310):
    if page.title == "page2":
        st.text_input("test")
    else:
        st.page_link("home.py", label="Home", icon=":material/home:")
        st.write("Welcome to the home page!")
        st.write(
            "Select a page from above."
        )
