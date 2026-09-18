"""Subset the source font down to what the site actually renders.

The site this replaces shipped 1 008 KB of woff2 on every cold visit: InterVariable
(352 KB) and its italic (388 KB), plus six IBM Plex Mono files (292 KB) that only the
blog's code blocks ever used. None of them were subset, so every visitor also
downloaded Cyrillic, Greek and Vietnamese glyphs.

What survives is one ~23 KB file: Inter, upright, and only the characters the four
built documents actually contain. Four cuts got it there, in decreasing order of yield:

  - Dropping latin-ext (158 KB -> 67 KB). The copy is French and English prose, and
    every accent it uses lives in U+00C0-00FF.
  - Pinning the optical-size axis (67 KB -> 45 KB). `opsz` carried a second set of
    gvar deltas for roughly half the file. Pinned at its default, headings render as
    scaled-up 14pt Inter, which is what every static Inter deployment looks like.
  - Cutting to the glyphs on the page (45 KB -> ~23 KB). This was rejected at first,
    on the grounds that an edit to the copy could introduce tofu. That was wrong, and
    only wrong because of how it would have been done: the `unicode-range` is
    generated from the same character set as the subset, so a character the font does
    not carry is also a character the font does not *claim*, and the browser falls
    back to the system stack for it. The failure mode is one word set in a different
    sans, not a row of boxes. `just check` builds and then fails if the documents hold
    a character the font is missing, so it is visible before it ships.
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
DIST = PROJECT_ROOT / "frontend" / "dist"

# The @font-face, written here rather than in app.css, because its `unicode-range` has
# to be the exact set this script subset to. Two hand-kept copies of that list is how
# tofu gets shipped. Committed, so the frontend image needs no fonttools.
FACE = PROJECT_ROOT / "frontend" / "src" / "font.css"

# pyftsubset's entry point takes argv, so the instanced font has to reach it as a path
# rather than in memory. Deleted on the way out; it is an uncompressed TTF and has no
# business being committed or served.
SCRATCH = OUTPUT.with_name(".instanced.ttf")

# Always carried, whatever the copy says. Printable ASCII is what every URL, class
# name and number is made of, it is a hundred glyphs against a 23 KB file, and having
# it unconditionally means a typo in the copy can never cost a glyph. U+FFFD is the
# replacement character: if an encoding ever goes wrong, a visible box beats a silent
# fallback.
ALWAYS = set(range(0x20, 0x7F)) | {0xA0, 0xFFFD}

# Google Fonts' own `latin` cut, used only to bootstrap: on a checkout with no build
# yet there are no documents to read, so the script falls back to the wider set rather
# than producing a font with nothing in it.
FALLBACK = (
    set(range(0x100))
    | {0x131, 0x152, 0x153, 0x2BB, 0x2BC, 0x2C6, 0x2DA, 0x2DC, 0x304, 0x308, 0x329}
    | set(range(0x2000, 0x2070))
    | {0x2074, 0x20AC, 0x2122, 0x2191, 0x2193, 0x2212, 0x2215, 0xFEFF, 0xFFFD}
)

# Layout features worth their bytes. The default shaping set plus `kern` is what keeps
# the type looking like Inter; cv02/cv03/cv04/cv11 are the stylistic alternates the
# stylesheet asks for through font-feature-settings, so dropping them would leave that
# declaration pointing at glyphs the file no longer holds. They cost ~4 KB.
LAYOUT_FEATURES = "kern,liga,clig,calt,ccmp,mark,mkmk,rlig,cv02,cv03,cv04,cv11,tnum"

# Axes to pin, and the value to pin them at. `wght` is deliberately absent: leaving it
# variable is what lets one file serve the 400/500/600 the design uses.
PINNED_AXES = {"opsz": 14.0}


def characters_on_the_site() -> set[int]:
    """Every codepoint in the built documents, plus the floor set.

    Read from the whole file rather than from its text nodes. Class names, URLs and
    attribute values are all ASCII and therefore already in ALWAYS, so the
    over-approximation costs nothing — and it cannot miss a character that some
    attribute ends up painting, which a text-node parser could.
    """
    documents = sorted(DIST.rglob("*.html"))
    if not documents:
        print("no build to read; falling back to the Latin cut")
        return ALWAYS | FALLBACK
    found = set(ALWAYS)
    for document in documents:
        # Control characters are the newlines and tabs of the markup itself. They are
        # never painted, and declaring them in a `unicode-range` would be noise.
        found.update(
            ord(character)
            for character in document.read_text("utf-8")
            if ord(character) >= 0x20
        )
    print(f"{len(documents)} documents, {len(found)} distinct characters")
    return found


def unicode_ranges(codepoints: set[int]) -> str:
    """Render a codepoint set as a CSS `unicode-range` value, collapsing runs."""
    ranges: list[str] = []
    ordered = sorted(codepoints)
    start = previous = ordered[0]
    for codepoint in ordered[1:] + [-1]:
        if codepoint == previous + 1:
            previous = codepoint
            continue
        ranges.append(
            f"U+{start:04X}" if start == previous else f"U+{start:04X}-{previous:04X}"
        )
        start = previous = codepoint
    return ", ".join(ranges)


def write_face(codepoints: set[int]) -> None:
    """Write the @font-face whose `unicode-range` matches what was actually subset."""
    FACE.write_text(
        "/* Generated by scripts/optimize_fonts.py — do not edit, run `just fonts`.\n"
        " *\n"
        " * The `unicode-range` is the exact set of characters in inter-latin.woff2.\n"
        " * That equality is the whole safety argument for subsetting this far: a\n"
        " * character the file does not carry is one the browser is never told to look\n"
        " * for here, so it falls back to the system stack instead of rendering tofu.\n"
        " *\n"
        " * `swap` shows the fallback immediately rather than blocking on the font. */\n"
        "@font-face {\n"
        '  font-family: "Inter";\n'
        '  src: url("/fonts/inter-latin.woff2") format("woff2-variations");\n'
        "  font-weight: 100 900;\n"
        "  font-style: normal;\n"
        "  font-display: swap;\n"
        f"  unicode-range: {unicode_ranges(codepoints)};\n"
        "}\n",
        encoding="utf-8",
    )
    print(f"wrote {FACE.relative_to(PROJECT_ROOT)}")


def optimize_fonts() -> None:
    """Pin the optical-size axis, cut to the glyphs on the page, and write the woff2.

    Raises:
        SystemExit: If the source font is missing.
    """
    if not SOURCE.exists():
        raise SystemExit(f"missing source font: {SOURCE.relative_to(PROJECT_ROOT)}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    codepoints = characters_on_the_site()

    font = TTFont(SOURCE)
    instancer.instantiateVariableFont(font, PINNED_AXES, inplace=True)
    font.save(SCRATCH)

    pyftsubset(
        [
            str(SCRATCH),
            f"--output-file={OUTPUT}",
            f"--unicodes={','.join(f'U+{c:04X}' for c in sorted(codepoints))}",
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

    write_face(codepoints)

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
