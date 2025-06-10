"""Script to get all necessary data for dashboard"""
import pandas as pd
import streamlit as st
from boto3 import session


@st.cache_resource
def get_boto3_session(access_key: str, secret_key: str):
    """Returns a live Boto3 session."""
    print("Connecting to AWS...")
    aws_session = Session(aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key,
                          region_name="eu-west-2")
    return aws_session
