#!/usr/bin/env python3
"""Inject Chinese dialogue translations into the existing lesson pages.

Adds a .zh line under each English dialogue line, using webapp/zh.js from the
source project. Word-level karaoke spans added by inject_karaoke.py are kept.

Already-injected pages are skipped. To regenerate from scratch:

    git checkout -- html/
    python3 tools/inject_karaoke.py
    python3 tools/inject_zh.py
"""

import html as htmlmod
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "html"
ZH_SOURCE = Path.home() / "Developer" / "englishpod_all" / "webapp" / "zh.js"

TABLE_RE = re.compile(r'(<div class="player">.*?</div>\s*)(<table>)(.*?)(</table>)', re.S)
ROW_RE = re.compile(r'<tr>.*?</tr>', re.S)
CELL_RE = re.compile(r'(<td[^>]*>)(.*?)(</td>)', re.S)
TAG_RE = re.compile(r'<[^>]+>')
CSS_MARKER = "englishpod-zh-style"


def visible_text(raw):
    return htmlmod.unescape(TAG_RE.sub("", raw)).strip()


def escape_zh(text):
    return htmlmod.escape(text, quote=False)


def main():
    if not ZH_SOURCE.exists():
        raise SystemExit("translation source not found: %s" % ZH_SOURCE)
    raw = ZH_SOURCE.read_text(encoding="utf-8")
    translations = json.loads(raw[raw.index("=") + 1:].strip().rstrip(";"))

    injected, skipped = [], []

    for n in range(1, 366):
        page = PAGES / ("englishpod_%04d.html" % n)
        text = page.read_text(encoding="utf-8")
        if 'class="zh"' in text:
            skipped.append(n)
            continue
        zh = translations.get(str(n))
        if not zh or not zh.get("dlg"):
            skipped.append(n)
            continue

        table = TABLE_RE.search(text)
        if not table:
            skipped.append(n)
            continue

        line = -1

        def transform_row(match):
            nonlocal line
            row = match.group(0)
            cells = list(CELL_RE.finditer(row))
            if len(cells) < 2:
                return row
            cell = cells[1]
            if not visible_text(cell.group(2)):
                return row
            line += 1
            if line >= len(zh["dlg"]):
                return row
            translation = escape_zh(zh["dlg"][line])
            addition = '<span class="zh" lang="zh-CN">%s</span>' % translation
            return row[:cell.end(2)] + addition + row[cell.end(2):]

        new_body = ROW_RE.sub(transform_row, table.group(3))
        if new_body == table.group(3):
            skipped.append(n)
            continue

        new_text = text[:table.start()] + (
            table.group(1) + table.group(2) + new_body + table.group(4)
        ) + text[table.end():]

        css = (
            '<style id="%s">.zh{display:block;margin-top:2px;color:#888;'
            'font-size:.82em;line-height:1.35}</style>\n    ' % CSS_MARKER
        )
        new_text = new_text.replace("</head>", css + "</head>", 1)
        page.write_text(new_text, encoding="utf-8")
        injected.append(n)

    print("injected: %d pages" % len(injected))
    print("skipped: %s" % skipped)


if __name__ == "__main__":
    main()
