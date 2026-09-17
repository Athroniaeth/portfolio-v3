from typing import Literal

import msgspec
from litestar import Controller, get
from litestar.datastructures import CacheControlHeader

from backend.content import CONTENT, Content
from backend.security import require_api_key


class HealthCheck(msgspec.Struct):
    status: Literal["ok"] = "ok"


class ApiController(Controller):
    """Groups related routes. The /api prefix is applied by the root router in app.py,
    not here, so every controller stays prefix-agnostic. Add shared `guards`,
    `dependencies` here later."""

    # The site itself never calls this: `just content` exports the same structs to
    # JSON and the prerenderer bakes them into the HTML, so a visitor loads zero
    # bytes of data. The route exists to keep the content typed and documented in
    # openapi.json, and to leave it reachable for a third party or a future page
    # that does need it at runtime.
    @get(
        "/content",
        name="api:content",
        guards=[require_api_key],
        security=[{"APIKey": []}],
        # Content changes only on deploy, so let a proxy hold it for an hour rather
        # than re-ask an ASGI worker for bytes that cannot have moved.
        cache_control=CacheControlHeader(public=True, max_age=3600),
    )
    async def content(self) -> Content:
        return CONTENT

    @get("/health", name="api:health")
    async def health_check(self) -> HealthCheck:
        return HealthCheck()
