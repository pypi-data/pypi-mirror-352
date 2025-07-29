"""
Cross-platform clipboard helper used by SavePlugin.
Falls back silently if the platform has no clipboard.
"""

import subprocess
import os
import sys

try:
    import pyperclip  # type: ignore

    def _COPY(txt: str) -> None:
        pyperclip.copy(txt)

except Exception:  # pyperclip not installed or unsupported
    if sys.platform == "win32":

        def _COPY(txt: str) -> None:
            p = subprocess.Popen(["clip"], stdin=subprocess.PIPE, close_fds=True)
            p.communicate(txt.encode("utf-8"))

    elif sys.platform == "darwin":

        def _COPY(txt: str) -> None:
            subprocess.run(["pbcopy"], input=txt.encode())

    else:  # X11 / Wayland

        def _COPY(txt: str) -> None:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=txt.encode(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


def copy(text: str) -> None:
    """
    Copy *text* to the system clipboard unless the user opted out by
    setting SAVECODE_NOCOPY=1.
    """
    if os.getenv("SAVECODE_NOCOPY") == "1":
        return
    try:
        _COPY(text)
    except Exception:
        pass  # never break the main flow
