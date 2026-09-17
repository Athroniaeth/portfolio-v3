"""Subset the source font down to what the site actually renders.

The site this replaces shipped 1 008 KB of woff2 on every cold visit: InterVariable
(352 KB) and its italic (388 KB), plus six IBM Plex Mono files (292 KB) that only the
blog's code blocks ever used. None of them were subset, so every visitor also
downloaded Cyrillic, Greek and Vietnamese glyphs.

What survives is one 45 KB file: Inter, upright, Latin only. Three cuts got it there,
in decreasing order of yield:

  - Dropping latin-ext (158 KB -> 67 KB). The copy is English prose plus French proper
    nouns, and every accent it uses lives in U+00C0-00FF. The @font-face declares a
    matching `unicode-range`, so a character outside the cut falls back to a system
    font instead of rendering as tofu — the failure mode stays legible if the copy
    ever grows a Polish or Turkish name.
  - Pinning the optical-size axis (67 KB -> 45 KB). `opsz` carried a second set of
    gvar deltas for roughly half the file. Pinned at its default, headings render as
    scaled-up 14pt Inter, which is what every static Inter deployment looks like.
  - Dropping the italic and the mono family entirely, upstream of this script: nothing
    on the site is italic, and the blog that used the mono face is not ported.

The weight axis is kept rather than instanced to 400/500/600 — one variable file beats
three static ones once the axis costs a few hundred bytes.

Run with `just fonts`. The output is committed, so neither CI nor Dockerfile.web needs
fonttools.
"""

from pathlib import Path

from fontTools.subset import main as pyftsubset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

PROJECT_ROOT = Path(__file__).parents[1]
SOURCE = PROJECT_ROOT / "assets" / "fonts" / "InterVariable.woff2"
OUTPUT = PROJECT_ROOT / "frontend" / "public" / "fonts" / "inter-latin.woff2"

# pyftsubset's entry point takes argv, so the instanced font has to reach it as a path
# rather than in memory. Deleted on the way out; it is an uncompressed TTF and has no
# business being committed or served.
SCRATCH = OUTPUT.with_name(".instanced.ttf")

# Google Fonts' own `latin` cut. Kept verbatim rather than narrowed to the exact
# glyphs in content.py: an edit to the copy must not be able to introduce tofu, and
# the remaining glyphs cost little next to the axis data.
UNICODES = (
    "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,"
    "U+0304,U+0308,U+0329,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,"
    "U+2193,U+2212,U+2215,U+FEFF,U+FFFD"
)

# Layout features worth their bytes. The default shaping set plus `kern` is what keeps
# the type looking like Inter; cv02/cv03/cv04/cv11 are the stylistic alternates the
# stylesheet asks for through font-feature-settings, so dropping them would leave that
# declaration pointing at glyphs the file no longer holds. They cost ~4 KB.
LAYOUT_FEATURES = "kern,liga,clig,calt,ccmp,mark,mkmk,rlig,cv02,cv03,cv04,cv11,tnum"

# Axes to pin, and the value to pin them at. `wght` is deliberately absent: leaving it
# variable is what lets one file serve the 400/500/600 the design uses.
PINNED_AXES = {"opsz": 14.0}


def optimize_fonts() -> None:
    """Pin the optical-size axis, cut to Latin, and write the woff2.

    Raises:
        SystemExit: If the source font is missing.
    """
    if not SOURCE.exists():
        raise SystemExit(f"missing source font: {SOURCE.relative_to(PROJECT_ROOT)}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    font = TTFont(SOURCE)
    instancer.instantiateVariableFont(font, PINNED_AXES, inplace=True)
    font.save(SCRATCH)

    pyftsubset(
        [
            str(SCRATCH),
            f"--output-file={OUTPUT}",
            f"--unicodes={UNICODES}",
            f"--layout-features={LAYOUT_FEATURES}",
            "--flavor=woff2",
            "--drop-tables+=DSIG",
            # Names bloat the file and nothing reads them at runtime; IDs 0, 13 and 14
            # are the copyright, licence and licence URL, which the SIL OFL requires
            # to travel with the font.
            "--name-IDs=0,13,14",
            "--name-legacy",
            "--notdef-outline",
        ]
    )

    before = SOURCE.stat().st_size
    after = OUTPUT.stat().st_size
    print(
        f"{SOURCE.name}: {before / 1024:.0f} KB -> {OUTPUT.name}: "
        f"{after / 1024:.0f} KB  (-{100 * (1 - after / before):.0f}%)"
    )


def check_tooling() -> None:
    """Fail early with a readable message when brotli is missing.

    fontTools can read a woff2 without it but cannot write one, and the error it
    raises deep in the compressor names neither the package nor the fix.

    Raises:
        SystemExit: If the brotli extra is not installed.
    """
    try:
        import brotli  # noqa: F401
    except ImportError:
        raise SystemExit(
            "woff2 output needs brotli: `uv sync` installs it via the "
            "fonttools[woff] dev dependency."
        ) from None


if __name__ == "__main__":
    check_tooling()
    try:
        optimize_fonts()
    finally:
        SCRATCH.unlink(missing_ok=True)
