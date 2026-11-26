#!/usr/bin/env python3
"""Add print-only layout to lesson pages.

Print output:
  page 1: title + dialogue
  page 2: vocabulary tables
  audio player is never printed
  the 中/英 toggle IS printed, so the sheet shows whether Chinese is blank
  Chinese follows the toggle state (English-only mode leaves Chinese blank)

On-screen layout is unchanged.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "html"
MARKER = "englishpod-print-style"
BREAK = '<div class="print-break"></div>\n    '
HEADINGS = ("<h2>Key Vocabulary</h2>", "<h2>Supplementary Vocabulary</h2>")
STYLE = (
    '<style id="%s">\n'
    '@page{size:A4;margin:0}\n'
    '@media print{\n'
    '  body{border:0;margin:0;padding:15mm;max-width:none;background:#fff}\n'
    '  .player,audio{display:none !important}\n'
    '  .print-break{break-before:page;page-break-before:always}\n'
    '  a{color:inherit;text-decoration:none}\n'
    '}\n'
    '</style>\n    ' % MARKER
)


def main():
    added, skipped = [], []
    for page in sorted(PAGES.glob("englishpod_*.html")):
        text = page.read_text(encoding="utf-8")
        if MARKER in text:
            skipped.append(page.name)
            continue

        positions = [text.find(h) for h in HEADINGS if text.find(h) >= 0]
        if positions:
            at = min(positions)
            text = text[:at] + BREAK + text[at:]
        text = text.replace("</head>", STYLE + "</head>", 1)
        page.write_text(text, encoding="utf-8")
        added.append(page.name)

    print("added: %d pages" % len(added))
    print("skipped: %d pages" % len(skipped))


if __name__ == "__main__":
    main()
