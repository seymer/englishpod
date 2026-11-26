#!/usr/bin/env python3
"""Add the Chinese translation toggle script to lesson pages.

Only pages that already contain translations get the script. Re-running is safe.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "html"
SCRIPT_TAG = '<script src="../js/zh-toggle.js"></script>'


def main():
    added, skipped = [], []
    for page in sorted(PAGES.glob("englishpod_*.html")):
        text = page.read_text(encoding="utf-8")
        if SCRIPT_TAG in text:
            skipped.append(page.name)
            continue
        if 'class="zh"' not in text:
            skipped.append(page.name)
            continue
        page.write_text(text.replace("</body>", SCRIPT_TAG + "\n</body>"), encoding="utf-8")
        added.append(page.name)
    print("added: %d pages" % len(added))
    print("skipped: %d pages" % len(skipped))


if __name__ == "__main__":
    main()
