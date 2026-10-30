"""
ui/api_key.py - the API Credentials sidebar module of the course (github.com/stoneman-mls/openai_credentials).

The user enters their own OpenAI API key in the sidebar ("API Key Input"); it is kept in
st.session_state.openai_api_key for this session only and never stored.

The course module's title, field, button and session variable are kept. Four changes for this app:
- The code runs in a function that the app calls on every rerun. Streamlit runs an imported module only once per server
  process, so widgets written at module level would disappear after the first click.
- The field is a password field, and the key is never written on the page: the course module prints
  "Current API Key: <the key>"; here only its last four characters are shown.
- "Update API Key" can check the key before it is used (the app passes a check that asks OpenAI, at no cost).
- The module can be drawn in another container than the sidebar: the app shows it on its first screen, in the middle
  of the page, and afterwards folded at the end of the sidebar, so that the key can be changed.
"""
import streamlit as st

FIELD = "openai_api_key_field"         # the widget's key, so that the field keeps its value on every rerun


def init():
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = None


def render_sidebar(box, title=True, primary=None, stretch=False):
    """The field and the button of the course module, in the sidebar or in another container."""
    if title:
        box.title("API Key Input")
    api_key = box.text_input("Enter your API key:", type="password", key=FIELD,
                             help="Your own OpenAI API key. It is used only for the calls of this session and not "
                                  "stored.")
    primary = title if primary is None else primary
    update_button = box.button("Update API Key", type="primary" if primary else "secondary",
                               width="stretch" if stretch else "content")
    return api_key, update_button


def api_key_input(check=None, box=None, title=True, primary=None, stretch=False, enter=False):
    """Draws the module and returns the key of this session (None until one is entered).
    check(key) returns None if the key can be used, otherwise the reason it cannot.
    enter=True: pressing Enter in the field does the same as "Update API Key" (each new value is checked once)."""
    init()
    box = box or st.sidebar
    api_key, update_button = render_sidebar(box, title, primary, stretch)
    typed = (api_key or "").strip()
    if enter and typed and typed != st.session_state.get("_api_key_tried"):
        update_button = True
    if update_button:
        key = typed
        st.session_state._api_key_tried = key
        problem = "Enter a key first." if not key else (check(key) if check else None)
        if problem:
            box.error(problem)
        else:
            st.session_state.openai_api_key = key
    if st.session_state.openai_api_key:
        box.caption(f"Current API Key: …{st.session_state.openai_api_key[-4:]} (this session only)")
    return st.session_state.openai_api_key