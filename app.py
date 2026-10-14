import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.title("Cocoa Overlap Screen")

# Simple password check for testing
password = st.sidebar.text_input("Password", type="password")
if password != os.getenv("APP_PASSWORD"):
    st.info("Enter the password in the sidebar.")
    st.stop()

client = OpenAI()  # reads OPENAI_API_KEY from .env automatically

if st.button("Test connection"):
    response = client.responses.create(
        model="gpt-6-luna",
        input="Reply with the single word: ready",
    )
    st.write(response.output_text)