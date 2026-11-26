#!/usr/bin/env python3
"""Inject Chinese vocabulary definitions into lesson-page vocabulary tables.

Uses the source project's data exactly like its own app.js renderVocabRows:
  text = zh.d + ' · ' + zh.p, falling back to zh_words_full.js by English word
  when both are empty.

Chinese lesson titles are NOT added here; they belong in index.html only
(see tools/inject_index_titles.py).

Existing karaoke spans and Chinese dialogue lines are untouched.
Regenerate from scratch:

    git checkout -- html/ index.html
    python3 tools/inject_karaoke.py
    python3 tools/inject_zh.py
    python3 tools/inject_zh_toggle.py
    python3 tools/inject_zh_vocab.py
    python3 tools/inject_index_titles.py
"""

import html as htmlmod
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "html"
ZH_SOURCE = Path.home() / "Developer" / "englishpod_all" / "webapp" / "zh.js"
WORDS_SOURCE = Path.home() / "Developer" / "englishpod_all" / "webapp" / "zh_words_full.js"

TABLE_RE = re.compile(r"<table>.*?</table>", re.S)
ROW_RE = re.compile(r"<tr>.*?</tr>", re.S)
CELL_RE = re.compile(r"(<td[^>]*>)(.*?)(</td>)", re.S)
TAG_RE = re.compile(r"<[^>]+>")
CSS_MARKER = "englishpod-zh-vocab-style"


def load_js(path):
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw[raw.index("=") + 1:].strip().rstrip(";"))


def plain(value):
    return htmlmod.unescape(TAG_RE.sub("", value or "")).strip()


def word_key(word):
    return re.sub(r"\s+", " ", word.lower()).strip()


def definition(entry, word, words):
    parts = []
    for key in ("d", "p"):
        value = (entry.get(key) or "").strip() if entry else ""
        if value:
            parts.append(value)
    text = " · ".join(parts)
    if not text:
        item = words.get(word_key(word))
        if item and item.get("d"):
            text = item["d"].strip()
    return text


def rows(table):
    result = []
    for row in ROW_RE.finditer(table):
        cells = list(CELL_RE.finditer(row.group(0)))
        if len(cells) >= 3 and plain(cells[0].group(2)):
            result.append((row.group(0), cells))
    return result


def add_definitions(table, entries, words):
    result = table
    for index, (original_row, cells) in enumerate(rows(table)):
        if index >= len(entries):
            break
        row = original_row
        word = plain(cells[0].group(2))

        # Chinese name on the left, under the English word
        if 'class="zh-name"' not in cells[0].group(2):
            item = words.get(word_key(word))
            name = (item.get("n") or "").strip() if item else ""
            if name:
                name_html = '<span class="zh-name">%s</span>' % htmlmod.escape(name, quote=False)
                row = row[:cells[0].end(2)] + name_html + row[cells[0].end(2):]
                cells = list(CELL_RE.finditer(row))

        # Chinese definition on the right, under the English definition
        if 'class="zh-def"' not in cells[2].group(2):
            text = definition(entries[index], word, words)
            if text:
                addition = '<span class="zh-def">%s</span>' % htmlmod.escape(text, quote=False)
                row = row[:cells[2].end(2)] + addition + row[cells[2].end(2):]

        result = result.replace(original_row, row, 1)
    return result


def main():
    translations = load_js(ZH_SOURCE)
    words = load_js(WORDS_SOURCE)

    injected, skipped = [], []

    for n in range(1, 366):
        page = PAGES / ("englishpod_%04d.html" % n)
        text = page.read_text(encoding="utf-8")
        if 'class="zh-def"' in text:
            skipped.append(n)
            continue
        zh = translations.get(str(n))
        if not zh:
            skipped.append(n)
            continue

        key_entries = zh.get("kv", []) or zh.get("sv", [])  # lesson 168 has no kv
        supp_entries = zh.get("sv", [])

        matches = list(TABLE_RE.finditer(text))
        pieces, last = [], 0
        for index, match in enumerate(matches):
            pieces.append(text[last:match.start()])
            table = match.group(0)
            if index == 1:
                table = add_definitions(table, key_entries, words)
            elif index == 2:
                table = add_definitions(table, supp_entries, words)
            pieces.append(table)
            last = match.end()
        pieces.append(text[last:])
        text = "".join(pieces)

        css = (
            '<style id="%s">.zh-name{display:block;margin-top:2px;color:#888;'
            'font-size:.82em;line-height:1.35}'
            '.zh-def{display:block;margin-top:2px;color:#888;'
            'font-size:.82em;line-height:1.35}</style>\n    ' % CSS_MARKER
        )
        text = text.replace("</head>", css + "</head>", 1)
        page.write_text(text, encoding="utf-8")
        injected.append(n)

    print("injected: %d pages" % len(injected))
    print("skipped: %s" % skipped)


if __name__ == "__main__":
    main()
