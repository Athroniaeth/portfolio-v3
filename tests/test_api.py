import json
import pathlib
import re

import msgspec
import pytest
from litestar import Litestar, get
from litestar.exceptions import ImproperlyConfiguredException
from litestar.openapi.spec import Components
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_429_TOO_MANY_REQUESTS,
)
from litestar.testing import AsyncTestClient, RequestFactory

from backend import CONTENT_EXPORT, FRONTEND_ROOT
from backend.app import build_openapi_config, build_rate_limit_config
from backend.content import CONTENT, Content, Sections, Text
from backend.exceptions import NotFoundError, ProblemDetail, app_error_handler
from backend.export import export_content
from backend.security import (
    API_KEY_ENV_VAR,
    API_KEY_HEADER,
    ensure_api_key_configured,
    identify_client,
)


async def test_health_check(client: AsyncTestClient):
    response = await client.get("/api/health")
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"status": "ok"}


async def test_root_is_not_served_by_the_api(client: AsyncTestClient):
    """The frontend is served by nginx, not Litestar.

    Guards the decoupling: re-enabling the Vite plugin at runtime would mount an
    HTML catch-all on `/` and silently couple the two again.
    """
    response = await client.get("/")
    assert response.status_code == HTTP_404_NOT_FOUND


async def test_content_accepts_the_configured_key(
    client: AsyncTestClient, api_key: str
):
    response = await client.get("/api/content", headers={API_KEY_HEADER: api_key})
    assert response.status_code == HTTP_200_OK
    payload = response.json()
    assert payload["profile"]["name"] == CONTENT.profile.name
    assert len(payload["projects"]) == len(CONTENT.projects)


async def test_content_rejects_a_missing_key(client: AsyncTestClient, api_key: str):
    response = await client.get("/api/content")
    assert response.status_code == HTTP_401_UNAUTHORIZED


async def test_content_rejects_a_wrong_key(client: AsyncTestClient, api_key: str):
    response = await client.get("/api/content", headers={API_KEY_HEADER: "wrong-key"})
    assert response.status_code == HTTP_401_UNAUTHORIZED


async def test_content_denies_everything_when_no_key_is_configured(
    client: AsyncTestClient, monkeypatch: pytest.MonkeyPatch
):
    """Fail closed: a missing API_KEY must lock the route, not open it."""
    monkeypatch.delenv(API_KEY_ENV_VAR, raising=False)
    response = await client.get("/api/content", headers={API_KEY_HEADER: "any-key"})
    assert response.status_code == HTTP_401_UNAUTHORIZED


async def test_health_stays_public(client: AsyncTestClient, api_key: str):
    """The compose healthcheck reaches /api/health directly, without nginx or a key."""
    response = await client.get("/api/health")
    assert response.status_code == HTTP_200_OK


def test_app_error_handler_maps_to_problem_detail():
    response = app_error_handler(RequestFactory().get("/"), NotFoundError())
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.media_type == "application/problem+json"
    assert response.content == ProblemDetail(
        status=HTTP_404_NOT_FOUND, detail="Resource not found", type="NotFoundError"
    )


def test_startup_check_rejects_a_missing_key(monkeypatch: pytest.MonkeyPatch):
    """Fail fast: a deployment without a key must break loudly, not answer 401s."""
    monkeypatch.delenv(API_KEY_ENV_VAR, raising=False)
    with pytest.raises(ImproperlyConfiguredException, match=API_KEY_ENV_VAR):
        ensure_api_key_configured()


def test_startup_check_rejects_an_empty_key(monkeypatch: pytest.MonkeyPatch):
    """An empty value is the Coolify case: nginx then drops the header entirely."""
    monkeypatch.setenv(API_KEY_ENV_VAR, "")
    with pytest.raises(ImproperlyConfiguredException, match=API_KEY_ENV_VAR):
        ensure_api_key_configured()


def test_startup_check_passes_with_a_key(api_key: str):
    ensure_api_key_configured()


async def test_docs_are_served_when_enabled(client: AsyncTestClient):
    """The default: handy in development, and what `generate-types` relies on."""
    response = await client.get("/schema/openapi.json")
    assert response.status_code == HTTP_200_OK


async def test_docs_are_absent_when_disabled():
    """No openapi_config means no /schema router at all.

    Guards production: the API has its own public domain on Coolify, so hiding the
    docs in nginx alone would leave them reachable.
    """
    app_without_docs = Litestar(
        route_handlers=[],
        openapi_config=build_openapi_config(docs_enabled=False),
    )
    async with AsyncTestClient(app=app_without_docs) as client:
        for path in ("/schema", "/schema/openapi.json", "/schema/swagger"):
            assert (await client.get(path)).status_code == HTTP_404_NOT_FOUND


def test_build_openapi_config_returns_none_when_disabled():
    assert build_openapi_config(docs_enabled=False) is None


def test_build_openapi_config_declares_the_api_key_scheme():
    config = build_openapi_config(docs_enabled=True)
    assert config is not None
    # `components` may also be a list in Litestar's API, hence the narrowing.
    components = config.components
    assert isinstance(components, Components)
    assert "APIKey" in (components.security_schemes or {})


def test_client_identifier_uses_the_proxy_header():
    """Behind nginx every connection comes from the proxy, so request.client is the
    same address for everyone — one shared quota instead of one per visitor.

    X-Real-IP is trustworthy here because nginx sets it with proxy_set_header, which
    overwrites whatever a caller sent.
    """
    request = RequestFactory().get("/", headers={"X-Real-IP": "203.0.113.42"})
    assert identify_client(request) == "203.0.113.42"


def test_client_identifier_falls_back_to_the_connection():
    """Direct hits, with no proxy in front."""
    request = RequestFactory().get("/")
    assert request.client is not None
    assert identify_client(request) == request.client.host


def test_rate_limit_spares_the_healthcheck():
    """The compose healthcheck must never be throttled."""
    config = build_rate_limit_config()
    assert config.exclude is not None
    assert "/api/health" in config.exclude


async def test_rate_limit_answers_429_beyond_the_quota():
    @get("/ping")
    async def ping() -> str:
        return "pong"

    config = build_rate_limit_config(rate_limit=("minute", 2))
    limited_app = Litestar(route_handlers=[ping], middleware=[config.middleware])
    async with AsyncTestClient(app=limited_app) as limited_client:
        assert (await limited_client.get("/ping")).status_code == HTTP_200_OK
        assert (await limited_client.get("/ping")).status_code == HTTP_200_OK
        response = await limited_client.get("/ping")
        assert response.status_code == HTTP_429_TOO_MANY_REQUESTS


async def test_rate_limit_is_wired_into_the_app(client: AsyncTestClient, api_key: str):
    """The quota headers prove the middleware is active without consuming it."""
    response = await client.get("/api/content", headers={API_KEY_HEADER: api_key})
    assert response.status_code == HTTP_200_OK
    assert "RateLimit-Limit" in response.headers


def test_exported_content_matches_the_source(tmp_path: pathlib.Path):
    """The JSON the frontend builds from must be the JSON content.py produces.

    `just check-content` enforces this on the committed file; this covers the exporter
    itself, so a change to the structs that breaks serialisation fails here rather than
    in a Docker build with no Python in it.
    """
    export_content()
    assert CONTENT_EXPORT.exists()
    exported = msgspec.json.decode(CONTENT_EXPORT.read_bytes(), type=Content)
    assert exported == CONTENT


def test_every_project_image_has_its_encoded_variants():
    """A project pointing at a stem with no files behind it renders a broken card.

    content.py names an image by stem and the <picture> markup derives the file names
    from the manifest, so nothing in either language catches a typo or a source that
    was never run through `just images`.
    """
    manifest = json.loads((FRONTEND_ROOT / "src" / "data" / "images.json").read_text())
    widths = manifest["cards"]["widths"]
    formats = manifest["cards"]["formats"]

    missing = [
        f"{project.image}-{width}.{fmt}"
        for project in CONTENT.projects
        for width in widths
        for fmt in formats
        if not (
            FRONTEND_ROOT
            / "public"
            / "images"
            / "projects"
            / f"{project.image}-{width}.{fmt}"
        ).exists()
    ]
    assert not missing, f"run `just images` — missing: {missing}"


def test_every_localised_string_is_filled_in_both_languages():
    """A missing translation renders as an empty element, not as an error.

    `Text` carries fr and en side by side precisely so that adding a field forces both
    to be written; this is what catches the one that was added and half-filled.

    """
    blanks: list[str] = []

    def walk(value: object, path: str) -> None:
        if isinstance(value, Text):
            for language in ("fr", "en"):
                if not getattr(value, language).strip():
                    blanks.append(f"{path}.{language}")
            return
        if isinstance(value, msgspec.Struct):
            for field in value.__struct_fields__:
                walk(getattr(value, field), f"{path}.{field}")
            return
        if isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")

    walk(CONTENT, "content")
    assert not blanks, f"untranslated: {sorted(set(blanks))}"


def test_every_period_ends_after_it_starts():
    """An inverted period renders a negative duration, which no one reads as a bug —
    it just looks like a typo in a CV."""
    for entry in CONTENT.timeline:
        for achievement in entry.achievements:
            period = achievement.period
            if period is not None and period.end is not None:
                assert period.start < period.end, achievement.title.en


def test_timeline_years_are_the_start_years_in_descending_order():
    """The anchor convention, enforced.

    The previous site filed one job under the year it began and a diploma under the
    year it ended, which made the chronology unreadable. A test is the only thing that
    keeps a convention like this from eroding on the next edit.
    """
    years = [entry.year for entry in CONTENT.timeline]
    assert years == sorted(years, reverse=True), years

    for entry in CONTENT.timeline:
        for achievement in entry.achievements:
            if achievement.period is not None:
                assert achievement.period.start.year == entry.year, achievement.title.en


def test_every_section_is_named_and_introduced():
    """The site is one page, and each section is an anchor the header links to.

    site.ts derives both the nav label and the `id` from these fields, so a section
    with an empty heading would render a nav entry with no text pointing at an anchor
    with no name, and nothing else would catch it.
    """
    for name in Sections.__struct_fields__:
        section = getattr(CONTENT.sections, name)
        assert section.heading.fr and section.heading.en, name
        assert section.subheading.fr and section.subheading.en, name


def test_skill_groups_are_not_empty():
    """An empty group renders as a card with a title and nothing under it."""
    for group in CONTENT.skills:
        assert group.items, group.name.fr


# Em dash and en dash as separators, and a colon used to introduce a clause. A hyphen
# inside a compound word ("auto-hébergé") is untouched, and so is a colon with no
# space after it, which is how the PII placeholder `<<EMAIL:1>>` survives.
FORBIDDEN_PUNCTUATION = (
    ("—", "em dash"),
    ("–", "en dash"),
    (" : ", "spaced colon"),
)


def test_prose_avoids_dashes_and_colons_as_separators():
    """A house style rule, enforced rather than remembered.

    Every one of these was in the copy at some point, and each rewrite is an
    opportunity to reintroduce one. URLs are exempt because `article` is a `Text` too
    and every https:// in it would otherwise trip the colon check.
    """
    offences: list[str] = []

    def walk(value: object, path: str) -> None:
        if isinstance(value, Text):
            for language in ("fr", "en"):
                text = getattr(value, language)
                if text.startswith("http"):
                    continue
                for token, name in FORBIDDEN_PUNCTUATION:
                    if token in text:
                        offences.append(f"{path}.{language}: {name}")
                if re.search(r"\w: ", text):
                    offences.append(f"{path}.{language}: colon before a space")
            return
        if isinstance(value, msgspec.Struct):
            for field in value.__struct_fields__:
                walk(getattr(value, field), f"{path}.{field}")
            return
        if isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")

    walk(CONTENT, "content")
    assert not offences, "\n".join(offences)


def test_every_achievement_declares_what_kind_it_is():
    """The icon and label are chosen from `kind`, so an unclassified entry would be
    drawn as something it is not. msgspec's Literal already refuses a wrong value; this
    checks the set actually in use against the one the frontend can render."""
    renderable = {"experience", "education", "certification", "distinction"}
    kinds = {
        achievement.kind
        for entry in CONTENT.timeline
        for achievement in entry.achievements
    }
    assert kinds <= renderable, kinds - renderable
    # Every kind the frontend can draw is used, so a stale icon cannot go unnoticed.
    assert kinds == renderable, renderable - kinds
