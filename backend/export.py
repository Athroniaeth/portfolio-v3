"""Serialise the portfolio content to the JSON the frontend build consumes.

Same contract-at-rest idea as openapi.json: Python owns the definition, the artefact
is committed, and the frontend image builds without a Python interpreter. `just check`
regenerates both and fails on a diff, so an edit to content.py that was never exported
cannot reach production.

Run with `just content`.
"""

from pathlib import Path

import msgspec

from backend import CONTENT_EXPORT, PROJECT_ROOT
from backend.content import CONTENT


def export_content(destination: Path = CONTENT_EXPORT) -> None:
    """Write CONTENT to frontend/src/data/content.json.

    Indented and newline-terminated on purpose: the file is committed, so a diff has
    to be readable. The bytes never reach a browser — the prerenderer inlines the
    values it needs into the HTML — so there is nothing to gain by minifying it.

    Args:
        destination: Where to write. Overridden by the test that checks the exporter
            round-trips, which must not rewrite the committed file as a side effect of
            `just test`.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = msgspec.json.format(msgspec.json.encode(CONTENT), indent=2)
    destination.write_bytes(payload + b"\n")
    try:
        print(f"wrote {destination.relative_to(PROJECT_ROOT)}")
    except ValueError:
        print(f"wrote {destination}")


if __name__ == "__main__":
    export_content()
