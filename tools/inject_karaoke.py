#!/usr/bin/env python3
"""Inject word-level karaoke highlighting into the existing lesson pages.

Only one feature is added: words in the dialogue light up in sync with the
page's own <audio>. No separate player, controls, progress, TTS or UI changes.

For each lesson page this script:
  1. wraps aligned dialogue words in <span class="kw" data-wi="N">
  2. embeds window.EP2_WORDS = [[start, end], ...]
  3. loads ../js/karaoke.js before </body>

Pages with no alignment (lesson 66) are left untouched. Lines whose text does
not match the alignment token count are left plain (reported in the summary).

Already-injected pages are skipped. To regenerate from scratch:

    git checkout -- html/
    python3 tools/inject_karaoke.py
"""

import html as htmlmod
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "html"
ALIGN_SOURCE = Path.home() / "Developer" / "englishpod_all" / "webapp" / "align.jsonl"
SCRIPT_TAG = '<script src="../js/karaoke.js"></script>'

TABLE_RE = re.compile(r'(<div class="player">.*?</div>\s*)(<table>)(.*?)(</table>)', re.S)
ROW_RE = re.compile(r'<tr>.*?</tr>', re.S)
CELL_RE = re.compile(r'(<td[^>]*>)(.*?)(</td>)', re.S)
TAG_RE = re.compile(r'<[^>]+>')
TAG_SPLIT_RE = re.compile(r'(<[^>]+>)')  # keep tags in the output
WORD_RE = re.compile(r"\S+")
NON_ALNUM_RE = re.compile(r"[^a-z0-9']")


def is_word(token):
    return bool(NON_ALNUM_RE.sub("", htmlmod.unescape(token).lower()))


def visible_tokens(raw):
    return [t for t in WORD_RE.findall(TAG_RE.sub("", htmlmod.unescape(raw))) if is_word(t)]


def wrap_cell(raw, first_wi, expected):
    """Wrap up to `expected` words; return (new_html, wrapped_count)."""
    pieces = TAG_SPLIT_RE.split(raw)
    count = 0
    result = []

    for piece in pieces:
        if piece.startswith("<") and piece.endswith(">"):
            result.append(piece)
            continue

        def replace(match):
            nonlocal count
            token = match.group(0)
            if not is_word(token) or count >= expected:
                return token
            wi = first_wi + count
            count += 1
            return '<span class="kw" data-wi="%d">%s</span>' % (wi, token)

        result.append(WORD_RE.sub(replace, piece))

    return "".join(result), count


def transform_table(table, align):
    """Return (new_table, wrapped_total, skipped_lines)."""
    body = table.group(3)
    line = -1
    wrapped_total = 0
    skipped = 0

    def transform_row(match):
        nonlocal line, wrapped_total, skipped
        row = match.group(0)
        cells = list(CELL_RE.finditer(row))
        if len(cells) < 2:
            return row
        text_cell = cells[1]
        raw = text_cell.group(2)
        if not visible_tokens(raw):
            return row
        line += 1

        ranges = align["l"]
        if line >= len(ranges):
            skipped += 1
            return row
        start, end = ranges[line]
        expected = end - start
        if len(visible_tokens(raw)) != expected:
            skipped += 1
            return row

        new_inner, count = wrap_cell(raw, start, expected)
        if count != expected:
            skipped += 1
            return row
        wrapped_total += count
        return row[:text_cell.start(2)] + new_inner + row[text_cell.end(2):]

    new_body = ROW_RE.sub(transform_row, body)
    return table.group(1) + table.group(2) + new_body + table.group(4), wrapped_total, skipped


def main():
    if not ALIGN_SOURCE.exists():
        raise SystemExit("alignment source not found: %s" % ALIGN_SOURCE)
    align_by_lesson = {}
    with ALIGN_SOURCE.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                item = json.loads(line)
                align_by_lesson[item["n"]] = item

    processed, untouched, skipped_pages = [], [], []
    total_words = 0

    for n in range(1, 366):
        page = PAGES / ("englishpod_%04d.html" % n)
        text = page.read_text(encoding="utf-8")
        if "EP2_WORDS" in text:
            untouched.append(n)
            continue
        align = align_by_lesson.get(n)
        if not align or not align["w"]:
            skipped_pages.append(n)
            continue

        match = TABLE_RE.search(text)
        if not match:
            skipped_pages.append(n)
            continue
        new_table, wrapped, skipped_lines = transform_table(match, align)
        if wrapped == 0:
            skipped_pages.append(n)
            continue

        words_json = json.dumps(align["w"], ensure_ascii=False, separators=(",", ":"))
        injection = (
            "<script>window.EP2_WORDS=%s;</script>\n    %s\n" % (words_json, SCRIPT_TAG)
        )
        new_text = text[:match.start()] + new_table + text[match.end():]
        new_text = new_text.replace("</body>", injection + "</body>")
        page.write_text(new_text, encoding="utf-8")
        processed.append(n)
        total_words += wrapped
        if skipped_lines:
            print("lesson %d: %d line(s) left plain" % (n, skipped_lines))

    print("injected: %d pages, %d word spans" % (len(processed), total_words))
    print("no alignment: %s" % skipped_pages)
    print("already injected: %d" % len(untouched))


if __name__ == "__main__":
    main()
