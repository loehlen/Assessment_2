"""
ui/working_screen.py - the working screen shown while the AI works (a progress card per step), and "Start over".
"""
import concurrent.futures as cf
import time

import streamlit as st

from ui import api_key

from ui.common import DEV_MODE, ss


# Long work (research, comparison) does not run in the middle of the page: Streamlit keeps the elements of the previous
# screen, faded, until a run ends, so old blocks would linger below the progress. A button only records the work and
# reloads; the next run clears the page body first and shows nothing but the progress, then opens the next step.
def start_work(kind, **args):
    ss.pending = {"kind": kind, **args}
    st.rerun()


class WorkCard:
    """The loading screen, the same everywhere: a heading, one progress bar and one plain sentence. The detailed lines
    are kept for development only, collapsed. Every card shows the seconds since it started, refreshed every second
    while the work runs (wait())."""

    def __init__(self, title, text, note=""):
        self.t0, self.text, self.fraction = time.time(), text, 0.0
        self.box = st.container(border=True)
        with self.box:
            st.markdown(f"#### {title}")
            self.bar = st.progress(0.0, text=self._label())
            if note:
                st.caption(note)
            self.dev = st.expander("Developer Details") if DEV_MODE else None

    def _label(self):
        return f"{self.text} · {time.time() - self.t0:.0f} s"

    def update(self, fraction, text):
        self.fraction, self.text = max(0.0, min(fraction, 1.0)), text
        self.bar.progress(self.fraction, text=self._label())

    def tick(self):
        self.bar.progress(self.fraction, text=self._label())

    def wait(self, futures):
        """Yields the futures as they finish, refreshing the seconds every second in between."""
        pending = set(futures)
        while pending:
            done, pending = cf.wait(pending, timeout=1, return_when=cf.FIRST_COMPLETED)
            self.tick()
            yield from done

    def log(self, line):
        if self.dev is not None:
            self.dev.write(line)


KEEP_ON_RESET = {"log", "auth_key", "openai_api_key", api_key.FIELD, "deploy_check", "started"}


def reset_all():
    """Discards everything of the current screen; keeps the key or password and, in development, the cost counter.
    The call log continues, but the audit log of the next screen starts here."""
    for k in list(ss.keys()):
        if k not in KEEP_ON_RESET:
            del ss[k]
    ss.run_first = ss.log.mark()
