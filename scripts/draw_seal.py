#!/usr/bin/env python3
"""Overlay the 密封线 (seal strip) onto an HTML-fallback exam PDF.

Why this exists: Chromium has no way to scope an absolutely-positioned CSS
block to page 1.  ``top: 20%`` is relative to the whole document, and
``@page :first`` cannot hide a document element on later pages.  Printing the
seal from HTML therefore either puts the personal-info block on the wrong page
or requires manual per-page edits.  Draw it onto the finished PDF instead.

Layout matches ``references/latex-templates.md`` §1:
  * dashed line at x=22mm, full page height
  * binding circles along that line, radius 2mm
  * "密封线内不得答题" at x=16.5mm, 50% page height
  * 学校/班级/姓名/学号 at x=7.5mm, 65/50/35/20% page height,
    rotated 90°, each followed by a 26mm vertical fill line

X values are the *centre* of the rotated glyph box, exactly like TikZ
``\node at (x, y)``; the baseline is shifted by half the font's
(ascender + descender) so the ink lands where LaTeX puts it.

The font is embedded (and subset) on every run: MuPDF's built-in CJK font is
not embedded by default, and a non-embedded CJK font can print as boxes on a
print-shop RIP.

Pre-flight guards (exit 3 unless ``--force``): pages with ``/Rotate``, and body
text that starts inside the 22mm seal band (that means the left margin is not
the 32mm the seal-on layout requires, so the overlay would stamp over questions).

By default the whole seal is drawn on page 1 only (P2+ stays clean).  Pass
``--repeat`` to keep the dashed line, circles, and prompt on every page while
still limiting the personal info to page 1 (the LaTeX template's behavior).

Usage:
    python scripts/draw_seal.py output/试卷.pdf -o output/试卷_密封.pdf \
        --paper 420x297 --lang zh

Requires PyMuPDF (``pip install pymupdf``).  Exit codes: 0 ok, 2 bad input,
3 pre-flight check failed (re-run with ``--force`` to override).
"""

import argparse
import os
import re
import sys
import tempfile

try:
    import fitz  # PyMuPDF
except ImportError:  # PyMuPDF >= 1.24 also exposes the pymupdf module name
    try:
        import pymupdf as fitz  # type: ignore
    except ImportError:
        print(
            "draw_seal.py requires PyMuPDF.\n"
            "Install it with: pip install pymupdf",
            file=sys.stderr,
        )
        sys.exit(2)

MM = 72.0 / 25.4  # PDF points per millimetre

# Seal geometry (mm / page-height fractions), mirroring latex-templates.md §1.
SEAL_X_MM = 22.0
PROMPT_X_MM = 16.5
PROMPT_FRACTION = 0.50
INFO_X_MM = 7.5
INFO_FRACTIONS = (0.65, 0.50, 0.35, 0.20)
FILL_LINE_MM = 26.0
FILL_GAP_MM = 1.0
CIRCLE_RADIUS_MM = 2.0
# LaTeX: \foreach \y in {0.07,0.12,...,0.93} -> 0.07, 0.12, ..., 0.92
CIRCLE_FRACTIONS = tuple(0.07 + 0.05 * i for i in range(18))
FONT_SIZE = 9.0

SEAL_TEXT = {
    "zh": "密封线内不得答题",
    "en": "Do not write inside the seal line",
}
INFO_LABELS = {
    "zh": ("学校", "班级", "姓名", "学号"),
    "en": ("School", "Class", "Name", "ID"),
}
# lang -> (PyMuPDF built-in font name, PDF resource name)
FONT_SPEC = {"zh": ("china-s", "SEALZH"), "en": ("helv", "SEALEN")}

_FONT_CACHE = {}


def _seal_font(lang):
    """Return ``(fitz.Font, resource name, font bytes)`` for *lang*.

    The bytes are embedded per page via ``page.insert_font`` and subset once
    before saving.  Without this the CJK seal text is written as a reference to
    a non-embedded font: fine on a desktop viewer with a CJK fallback, but a
    print RIP may draw nothing or boxes.
    """
    if lang not in _FONT_CACHE:
        base_name, resource = FONT_SPEC[lang]
        font = fitz.Font(base_name)
        _FONT_CACHE[lang] = (font, resource, font.buffer)
    return _FONT_CACHE[lang]


def _text_length_mm(text, font, fontsize=FONT_SIZE):
    """Advance width of *text* in millimetres (points -> mm)."""
    return font.text_length(text, fontsize=fontsize) * 25.4 / 72.0


def _baseline_x_mm(x_center_mm, font, fontsize=FONT_SIZE):
    """Baseline x that puts the rotated glyph box centre on *x_center_mm*.

    PyMuPDF's ``insert_text`` anchors at the baseline (ink sits left of it when
    rotated 90°), while TikZ ``\\node at (x, y)`` centres the box.  Compensate by
    half the font's ascender + descender; measured drift without it is 1.27mm.
    """
    offset_pt = (font.ascender + font.descender) / 2.0 * fontsize
    return x_center_mm + offset_pt * 25.4 / 72.0


def _draw_rotated_centered(page, text, x_center_mm, y_center_mm, font, resource):
    """Draw text rotated 90° CCW, centred on (x_center_mm, y_center_mm).

    PyMuPDF's ``rotate=90`` extends text upward from the insertion point, so the
    insertion point is moved down by half the advance width.
    """
    length = _text_length_mm(text, font)
    page.insert_text(
        (
            _baseline_x_mm(x_center_mm, font) * MM,
            (y_center_mm + length / 2.0) * MM,
        ),
        text,
        fontname=resource,
        fontsize=FONT_SIZE,
        rotate=90,
        color=(0, 0, 0),
    )


def _draw_info_field(page, label, fraction, font, resource):
    """Label + 26mm vertical fill line, the whole group centred on *fraction*.

    The label sits at the bottom of the group and the fill line continues
    upward, matching a rotated ``学校________`` line in LaTeX.  The fill line is
    a real stroke at the text baseline, not a run of underscore glyphs.
    """
    label_len = _text_length_mm(label, font)
    total = label_len + FILL_GAP_MM + FILL_LINE_MM
    y_center = (1.0 - fraction) * page.rect.height / MM
    y_bottom = y_center + total / 2.0
    x_baseline = _baseline_x_mm(INFO_X_MM, font)

    page.insert_text(
        (x_baseline * MM, y_bottom * MM),
        label,
        fontname=resource,
        fontsize=FONT_SIZE,
        rotate=90,
        color=(0, 0, 0),
    )

    line_start = y_bottom - label_len - FILL_GAP_MM
    line_end = line_start - FILL_LINE_MM
    page.draw_line(
        fitz.Point(x_baseline * MM, line_start * MM),
        fitz.Point(x_baseline * MM, line_end * MM),
        color=(0, 0, 0),
        width=0.5,
    )


def draw_seal(page, page_number, lang="zh", repeat=False):
    """Draw the seal strip on one page.

    ``page_number`` is 0-based.  By default the whole strip is page 1 only;
    with ``repeat`` the line/circles/prompt continue on later pages while the
    personal info stays on page 1.
    """
    if page_number != 0 and not repeat:
        return

    font, resource, font_bytes = _seal_font(lang)
    page.insert_font(fontname=resource, fontbuffer=font_bytes)
    height_mm = page.rect.height / MM

    # Dashed line, full page height.
    page.draw_line(
        fitz.Point(SEAL_X_MM * MM, 0),
        fitz.Point(SEAL_X_MM * MM, page.rect.height),
        color=(0, 0, 0),
        width=0.8,
        dashes="[3 3] 0",
    )

    # Binding circles centred on the dashed line.
    for fraction in CIRCLE_FRACTIONS:
        page.draw_circle(
            fitz.Point(SEAL_X_MM * MM, (1.0 - fraction) * page.rect.height),
            CIRCLE_RADIUS_MM * MM,
            color=(0, 0, 0),
            width=0.5,
        )

    # "密封线内不得答题" / English equivalent.
    _draw_rotated_centered(
        page, SEAL_TEXT[lang], PROMPT_X_MM, PROMPT_FRACTION * height_mm, font, resource
    )

    # Personal info only on page 1.
    if page_number == 0:
        for label, fraction in zip(INFO_LABELS[lang], INFO_FRACTIONS):
            _draw_info_field(page, label, fraction, font, resource)


def _parse_paper(value):
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)\s*$", value)
    if not m:
        raise argparse.ArgumentTypeError("want WxH in mm, e.g. 420x297")
    return float(m.group(1)), float(m.group(2))


def _check_paper(doc, paper):
    """Fail early when --paper does not match the PDF (orientation bugs)."""
    got = (doc[0].rect.width / MM, doc[0].rect.height / MM)
    if abs(got[0] - paper[0]) > 1.0 or abs(got[1] - paper[1]) > 1.0:
        raise SystemExit(
            f"paper mismatch: PDF is {got[0]:.0f}x{got[1]:.0f}mm, "
            f"--paper says {paper[0]:.0f}x{paper[1]:.0f}mm"
        )


def _preflight(doc, paper):
    """Collect layout problems that would make the overlay unusable.

    Two failure modes are silent and produce a scrap paper:

    * body text inside the 22mm seal band -> the source was printed with the
      seal-off 18mm left margin, so the dashed line would run through questions;
    * ``/Rotate`` pages -> page.rect is rotated but drawing uses unrotated
      coordinates, so the strip lands in the wrong place.

    A mixed page size is reported too: ``--paper`` only vouches for one size.
    """
    problems = []
    sizes = sorted({(round(p.rect.width / MM), round(p.rect.height / MM))
                    for p in doc})
    if paper and len(sizes) > 1:
        problems.append(f"mixed page sizes {sizes}; --paper expects one size")

    band_mm = SEAL_X_MM - 1.0
    marks = {SEAL_TEXT["zh"], SEAL_TEXT["en"], *INFO_LABELS["zh"], *INFO_LABELS["en"]}

    def _is_seal_block(block):
        """True when every line is a seal prompt / info label (already stamped)."""
        lines = [ln.strip() for ln in block[4].splitlines() if ln.strip()]
        return bool(lines) and all(ln in marks for ln in lines)

    for page_number, page in enumerate(doc, 1):
        if page.rotation:
            problems.append(
                f"page {page_number}: /Rotate {page.rotation}; seal coordinates "
                f"assume rotation 0"
            )
        hits = [b for b in page.get_text("blocks")
                if b[0] < band_mm * MM and b[4].strip()]
        if not hits:
            continue
        already = [b for b in hits if _is_seal_block(b)]
        body = [b for b in hits if b not in already]
        if already and not body:
            problems.append(
                f"page {page_number}: already carries a seal overlay "
                f"(re-running would double-stamp it)"
            )
            continue
        if body:
            sample = body[0][4].strip().splitlines()[0][:20]
            problems.append(
                f"page {page_number}: {len(body)} text block(s) start inside the "
                f"left {band_mm:.0f}mm seal band (left margin must be 32mm with "
                f"seal); e.g. {sample!r}"
            )
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", help="source PDF (printed from the HTML fallback)")
    ap.add_argument("-o", "--output", help="output PDF (default: <stem>_sealed.pdf)")
    ap.add_argument("--paper", type=_parse_paper,
                    help="expected paper as WxH in mm, e.g. 420x297")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh",
                    help="seal text language (default: zh)")
    ap.add_argument("--repeat", action="store_true",
                    help="keep line/circles/prompt on every page "
                         "(LaTeX default); personal info stays on page 1")
    ap.add_argument("--force", action="store_true",
                    help="draw anyway when pre-flight checks fail "
                         "(rotated pages, text in the seal band)")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"file not found: {args.input}", file=sys.stderr)
        return 2

    output = args.output
    if not output:
        stem, ext = os.path.splitext(args.input)
        output = f"{stem}_sealed{ext or '.pdf'}"
    same_file = os.path.abspath(output) == os.path.abspath(args.input)

    doc = fitz.open(args.input)
    if doc.page_count == 0:
        print("input PDF has no pages", file=sys.stderr)
        return 2
    if args.paper:
        _check_paper(doc, args.paper)

    problems = _preflight(doc, args.paper)
    if problems:
        stream = sys.stderr
        if args.force:
            print("warning: pre-flight problems ignored (--force):", file=stream)
            for problem in problems:
                print(f"  - {problem}", file=stream)
        else:
            print("pre-flight check failed:", file=stream)
            for problem in problems:
                print(f"  - {problem}", file=stream)
            print("fix the layout, or re-run with --force to overlay anyway",
                  file=stream)
            return 3

    for page_number, page in enumerate(doc):
        draw_seal(page, page_number, args.lang, repeat=args.repeat)

    # Subset the embedded seal font; otherwise every page carries the full
    # ~3.5MB CJK font.
    if hasattr(doc, "subset_fonts"):
        try:
            doc.subset_fonts()
        except Exception as exc:  # noqa: BLE001 - never fail the delivery on this
            print(f"warning: font subsetting failed ({exc}); output will be large",
                  file=sys.stderr)

    if same_file:
        # Save to a sibling temp file, then replace atomically.
        fd, tmp = tempfile.mkstemp(suffix=".pdf", dir=os.path.dirname(output) or ".")
        os.close(fd)
        try:
            doc.save(tmp, garbage=4, deflate=True)
            doc.close()
            os.replace(tmp, output)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
    else:
        doc.save(output, garbage=4, deflate=True)
        doc.close()

    print(f"sealed PDF: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
