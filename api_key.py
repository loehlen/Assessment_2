"""
api_key.py - the API Credentials sidebar module of the course (github.com/stoneman-mls/openai_credentials).

The user enters their own OpenAI API key in the sidebar ("API Key Input"); it is kept in
st.session_state.openai_api_key for this session only and never stored.

The course module's title, field, button and session variable are kept. Three changes for this app:
- The code runs in a function that the app calls on every rerun. Streamlit runs an imported module only once per server
  process, so widgets written at module level would disappear after the first click.
- The field is a password field, and the key is never written on the page: the course module prints
  "Current API Key: <the key>"; here only its last four characters are shown.
- "Update API Key" can check the key before it is used (the app passes a check that asks OpenAI, at no cost).
"""
import streamlit as st

FIELD = "openai_api_key_field"         # the widget's key, so that the field keeps its value on every rerun


def init():
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = None


def render_sidebar(box, title=True):
    """The field and the button of the course module, in the sidebar or in a box inside it."""
    if title:
        box.title("API Key Input")
    api_key = box.text_input("Enter your API key:", type="password", key=FIELD,
                             help="Your own OpenAI API key. It is used only for the calls of this session and not "
                                  "stored.")
    update_button = box.button("Update API Key", type="primary" if title else "secondary")
    return api_key, update_button


def api_key_input(check=None, box=None, title=True):
    """Draws the module and returns the key of this session (None until one is entered).
    check(key) returns None if the key can be used, otherwise the reason it cannot."""
    init()
    box = box or st.sidebar
    api_key, update_button = render_sidebar(box, title)
    if update_button:
        key = (api_key or "").strip()
        problem = "Enter a key first." if not key else (check(key) if check else None)
        if problem:
            box.error(problem)
        else:
            st.session_state.openai_api_key = key
    if st.session_state.openai_api_key:
        box.caption(f"Current API Key: …{st.session_state.openai_api_key[-4:]} (this session only)")
    return st.session_state.openai_api_key