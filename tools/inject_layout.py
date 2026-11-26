#!/usr/bin/env python3
"""Add small readability / print tuning to lesson pages.

Does not touch css/style.css. Only adds one inline style block per page.
Screen: roomier dialogue rows, easier bilingual reading.
Print: tighter rows, no split rows, highlighted words keep their background.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "html"
MARKER = "englishpod-layout-style"
STYLE = """<style id="englishpod-layout-style">
.player + table td{padding:6px 8px;line-height:1.5}
.player + table td:first-child{white-space:nowrap;vertical-align:top;color:#555;font-weight:600}
.zh,.zh-name,.zh-def{line-height:1.5;font-size:.85em;margin-top:3px}
@media print{
  .player + table td{padding:4px 6px;line-height:1.4}
  .zh,.zh-name,.zh-def{font-size:.8em;margin-top:2px}
  tr{break-inside:avoid;page-break-inside:avoid}
  .kw.on{-webkit-print-color-adjust:exact;print-color-adjust:exact}
}
</style>
    """


def main():
    added, skipped = [], []
    for page in sorted(PAGES.glob("englishpod_*.html")):
        text = page.read_text(encoding="utf-8")
        if MARKER in text:
            skipped.append(page.name)
            continue
        page.write_text(text.replace("</head>", STYLE + "</head>", 1), encoding="utf-8")
        added.append(page.name)
    print("added: %d pages" % len(added))
    print("skipped: %d pages" % len(skipped))


if __name__ == "__main__":
    main()
