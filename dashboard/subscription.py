"""Subscription page."""
import streamlit as st


def create_page() -> None:
    """Create the page for subscriptions."""
    st.title("Football Summary Subscription")
    with st.form("Subscription Form"):
        st.subheader("Your information")
        email = st.text_input(
            "Email Address", placeholder="your.email@example.com")

        reports = st.checkbox("Subscribe to Goal Notifications")

        submitted = st.form_submit_button("Subscribe Now")
    if email and submitted:
        st.success("Subscribed!")

    with st.form("Download Match Summary"):
        st.subheader("Download PDF summary of selected match")
        download = st.form_submit_button("Download")
    if download:
        st.success("File Downloaded!")


if __name__ == "__main__":
    create_page()
