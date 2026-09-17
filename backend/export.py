"""Serialise the portfolio content to the JSON the frontend build consumes.

Same contract-at-rest idea as openapi.json: Python owns the definition, the artefact
is committed, and the frontend image builds without a Python interpreter. `just check`
regenerates both and fails on a diff, so an edit to content.py that was never exported
cannot reach production.

Run with `just content`.
"""

import msgspec

from backend import CONTENT_EXPORT, PROJECT_ROOT
from backend.content import CONTENT


def export_content() -> None:
    """Write CONTENT to frontend/src/data/content.json.

    Indented and newline-terminated on purpose: the file is committed, so a diff has
    to be readable. The bytes never reach a browser — the prerenderer inlines the
    values it needs into the HTML — so there is nothing to gain by minifying it.
    """
    CONTENT_EXPORT.parent.mkdir(parents=True, exist_ok=True)
    payload = msgspec.json.format(msgspec.json.encode(CONTENT), indent=2)
    CONTENT_EXPORT.write_bytes(payload + b"\n")
    print(f"wrote {CONTENT_EXPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    export_content()
