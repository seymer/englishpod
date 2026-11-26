#!/usr/bin/env python3
"""Put Chinese lesson titles in index.html, right after each list link.

The 365 lesson pages themselves get no title translation.
Uses webapp/zh.js from the source project.
"""

import html as htmlmod
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
ZH_SOURCE = Path.home() / "Developer" / "englishpod_all" / "webapp" / "zh.js"
ITEM_RE = re.compile(r'(<li><a href="html/englishpod_\d{4}\.html">[^<]*</a>)(</li>)')
CSS = (
    '<style id="englishpod-index-zh">.zh-title{margin-left:.5em;color:#888;'
    'font-size:.85em;opacity:0;transition:opacity .15s}'
    'li:hover .zh-title,li:focus-within .zh-title{opacity:1}</style>\n    '
)


def main():
    raw = ZH_SOURCE.read_text(encoding="utf-8")
    translations = json.loads(raw[raw.index("=") + 1:].strip().rstrip(";"))
    text = INDEX.read_text(encoding="utf-8")
    if 'class="zh-title"' in text:
        print("already injected")
        return

    def replace(match):
        number = int(re.search(r"englishpod_(\d{4})", match.group(0)).group(1))
        title = htmlmod.escape((translations.get(str(number), {}).get("t") or "").strip(), quote=False)
        return match.group(1) + '<span class="zh-title">%s</span>' % title + match.group(2)

    new_text, count = ITEM_RE.subn(replace, text)
    new_text = new_text.replace("</head>", CSS + "</head>", 1)
    INDEX.write_text(new_text, encoding="utf-8")
    print("titles added:", count)


if __name__ == "__main__":
    main()
