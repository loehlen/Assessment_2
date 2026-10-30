"""
ui/credentials.py - the first screen: the user's own OpenAI API key, entered in the course's API Credentials
module (ui/api_key.py), shown in the middle of the page; in development, an app password and the developer's key
instead.
"""
import openai
import streamlit as st

from logic import ai_client
from ui import api_key

from ui.common import PROFILE, ss, USE_CACHE, USES_PASSWORD


def key_problem(key):
    """Asks OpenAI whether it accepts the key (listing the models costs nothing). Only a rejected key is refused: if
    OpenAI cannot be reached just now, the key is accepted and a real problem shows at the first AI call."""
    try:
        ai_client.client_factory(key, 20).models.list()
    except openai.AuthenticationError:
        return "OpenAI did not accept this key. Check it and click “Update API Key” again."
    except Exception:  # noqa: BLE001 - network or service problem: not a reason to refuse the key
        return None
    return None


def gate_page(lead_html):
    """The first screen on its own, in the middle of the page: a narrow centred column, pushed down from the top."""
    st.markdown("<div class='gate-space'></div>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.3, 1])
    mid.markdown("<div class='gate-title'>EU Overlap Screen</div>"
                 f"<div class='gate-lead'>A preliminary overlap screen for EU merger control.</div>{lead_html}",
                 unsafe_allow_html=True)
    return mid


def credentials():
    """The OpenAI key for this session.
    Submitted version (DEV_MODE off): the user's own key, entered in the course's API Credentials module
    (ui/api_key.py), drawn on the first screen in the middle of the page. From step ① on, the module stays at the end
    of the sidebar, folded, so the key can be changed.
    Development (DEV_MODE), or PASSWORD_ONLY (the submitted version, but with the password): an app password on the
    first screen, then the developer's key from .env or Secrets.
    The key is kept for the session only (never stored)."""
    if not USES_PASSWORD:
        if ss.get("openai_api_key"):
            return ss.openai_api_key
        mid = gate_page("")
        with mid:
            entered = api_key.api_key_input(check=key_problem, box=st.container(), title=False, primary=True,
                                            stretch=True, enter=True)
            st.markdown("<div class='gate-note'>Your own OpenAI API key, used only for the calls of this session and "
                        "not stored. A screen of one of the examples costs about USD 0.50–1 in API fees. You can "
                        "change the key later in the sidebar, under “API Key Input”.</div>", unsafe_allow_html=True)
        if entered:                      # the start page follows; the module waits folded in the sidebar
            st.rerun()
        st.stop()
    if ss.get("auth_key"):
        return ss.auth_key
    expected, server_key = ai_client.setting("APP_PASSWORD"), ai_client.setting("OPENAI_API_KEY")
    if not expected:
        st.error("APP_PASSWORD is not set in .env or Secrets.")
        st.stop()
    if not server_key:
        st.error("OPENAI_API_KEY is not set in .env or Secrets.")
        st.stop()
    mid = gate_page("")
    with mid:
        value = st.text_input("App password", type="password", key="gate_input")
        st.button("Continue", type="primary", width="stretch")       # Enter in the field does the same
    if value:
        if value != expected:
            mid.error("This password is not correct.")
            st.stop()
        ss.auth_key = server_key
        st.rerun()
    st.stop()


def key_sidebar():
    """After the key is entered: the course module at the end of the sidebar, folded (submitted version only; with the
    password, the key comes from .env or Secrets)."""
    if not USES_PASSWORD:
        old = ss.get("openai_api_key")
        with st.sidebar.expander("API Key Input"):
            new = api_key.api_key_input(check=key_problem, box=st.container(), title=False)
        if new != old:
            st.rerun()


def make_ai(key):
    return ai_client.AI(profile=PROFILE, api_key=key, use_cache=USE_CACHE, log=ss.log)