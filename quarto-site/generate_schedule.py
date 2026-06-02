#!/usr/bin/env python3
"""
generate_schedule.py  —  Maker-X pre-render script
Fetches the class schedule from a published Google Sheets CSV and writes
_schedule_generated.html, which schedule.qmd includes at build time.

Setup:
  1. In Google Sheets: File → Share → Publish to web → Sheet 1 → CSV → Publish
  2. Copy the published CSV URL into SHEET_URL below
  3. Run `quarto render` — the script fetches, caches, and generates the HTML
"""

import csv
import html
import io
import os
import sys
from pathlib import Path

# ── CONFIGURATION ────────────────────────────────────────────────────────────
SHEET_URL   = "YOUR_GOOGLE_SHEETS_CSV_URL_HERE"   # paste published CSV URL here
CACHE_FILE  = Path("_schedule_data.csv")           # local fallback / cache
OUTPUT_FILE = Path("_schedule_generated.html")     # included by schedule.qmd
# ─────────────────────────────────────────────────────────────────────────────

# Week display metadata
WEEK_META = {
    "1": {"title": "CONCEIVE",    "zh": "构思", "cls": "w1-hdr"},
    "2": {"title": "DESIGN",      "zh": "设计", "cls": "w2-hdr"},
    "3": {"title": "BUILD",       "zh": "制造", "cls": "w3-hdr"},
    "4": {"title": "PITCH IT ★",  "zh": "展示", "cls": "w4-hdr"},
}

# Instructor badge HTML
BADGES = {
    "liang":     '<span class="b b-liang">梁俊睿</span>',
    "shimon":    '<span class="b b-shimon">Shimon</span>',
    "daniel":    '<span class="b b-daniel">Daniel</span>',
    "junjun":    '<span class="b b-junjun">JunJun</span>',
    "espressif": '<span class="b b-esp">Espressif</span>',
    "zhou":      '<span class="b b-zhou">Prof. Zhou</span>',
    "all":       '<span class="b b-all">All</span>',
}

# Row highlight CSS classes
HIGHLIGHT_CLASSES = {
    "guest":  "row-guest",
    "poster": "row-poster",
    "demo":   "row-demo",
    "zhou":   "row-zhou",
}


def render_badges(instructors_str: str) -> str:
    """Convert comma-separated instructor keys to badge HTML."""
    if not instructors_str.strip():
        return ""
    parts = [p.strip() for p in instructors_str.split(",")]
    return " ".join(BADGES.get(p, html.escape(p)) for p in parts if p)


def fetch_sheet() -> str | None:
    if SHEET_URL == "YOUR_GOOGLE_SHEETS_CSV_URL_HERE":
        print("[schedule] No sheet URL configured — using cached CSV.")
        return None
    try:
        import urllib.request
        with urllib.request.urlopen(SHEET_URL, timeout=12) as resp:
            data = resp.read().decode("utf-8")
        CACHE_FILE.write_text(data, encoding="utf-8")
        print(f"[schedule] Fetched {len(data):,} bytes from Google Sheets.")
        return data
    except Exception as exc:
        print(f"[schedule] Warning: could not fetch sheet ({exc})")
        return None


def load_rows() -> list[dict]:
    csv_text = fetch_sheet()
    if csv_text is None:
        if CACHE_FILE.exists():
            print(f"[schedule] Using cached data: {CACHE_FILE}")
            csv_text = CACHE_FILE.read_text(encoding="utf-8")
        else:
            print("[schedule] ERROR: no SHEET_URL set and no cache file found.")
            sys.exit(1)
    return list(csv.DictReader(io.StringIO(csv_text)))


def group_rows(rows: list[dict]):
    """Return nested dict: week → session → {meta, blocks: {block_name: [rows]}}."""
    weeks: dict = {}
    for row in rows:
        w = row["week"].strip()
        s = row["session"].strip()
        b = row["block"].strip()
        weeks.setdefault(w, {})
        weeks[w].setdefault(s, {
            "date": row["date"].strip(),
            "day":  row["day"].strip(),
            "blocks": {},
        })
        weeks[w][s]["blocks"].setdefault(b, [])
        weeks[w][s]["blocks"][b].append(row)
    return weeks


def session_label(s_num: str, day: str, date: str, sessions_blocks: dict) -> str:
    """Build the session header label, appending ★ DEMO DAY when applicable."""
    label = f"SESSION {s_num} &nbsp;·&nbsp; {day.upper()} &nbsp;·&nbsp; {date.upper()}"
    # Auto-detect demo day: any period with highlight=demo
    for period_rows in sessions_blocks.values():
        for r in period_rows:
            if r.get("highlight", "").strip().lower() == "demo":
                label += " &nbsp;·&nbsp; ★ DEMO DAY"
                return label
    return label


def build_html(weeks: dict) -> str:
    out = ['<div class="sched-wrap">']

    for w_num in sorted(weeks, key=int):
        meta = WEEK_META.get(w_num, {
            "title": f"WEEK {w_num}", "zh": "", "cls": "w1-hdr"
        })
        out.append('<div class="sched-week-block">')
        out.append(
            f'  <div class="sched-week-header {meta["cls"]}">'
            f'WEEK {w_num} &nbsp;·&nbsp; {meta["title"]} &nbsp;/&nbsp; {meta["zh"]}'
            f'</div>'
        )

        for s_num in sorted(weeks[w_num], key=int):
            sess = weeks[w_num][s_num]
            out.append(
                f'  <div class="sched-session-label">'
                f'{session_label(s_num, sess["day"], sess["date"], sess["blocks"])}'
                f'</div>'
            )
            out.append('  <table class="sched-table">')
            out.append('    <thead><tr><th>#</th><th>Time</th><th>Topic</th><th>Instructor(s)</th></tr></thead>')
            out.append('    <tbody>')

            for block_name, period_rows in sess["blocks"].items():
                out.append(f'      <tr class="block-hdr"><td colspan="4">▸ {html.escape(block_name)}</td></tr>')
                for r in period_rows:
                    period  = r.get("period", "").strip()
                    time    = html.escape(r.get("time", "").strip())
                    topic   = html.escape(r.get("topic", "").strip())
                    is_guest = r.get("guest", "").strip().lower() in ("yes", "y", "true", "1")
                    instrs  = r.get("instructors", "").strip()
                    hl      = r.get("highlight", "").strip().lower()

                    if is_guest:
                        topic = f"<strong>Guest:</strong> {topic}"

                    row_cls = HIGHLIGHT_CLASSES.get(hl, "")
                    row_attr = f' class="{row_cls}"' if row_cls else ""

                    out.append(f'      <tr{row_attr}>')
                    out.append(f'        <td class="p-num">{html.escape(period)}</td>')
                    out.append(f'        <td class="p-time">{time}</td>')
                    out.append(f'        <td class="p-topic">{topic}</td>')
                    out.append(f'        <td class="p-who">{render_badges(instrs)}</td>')
                    out.append('      </tr>')

            out.append('    </tbody>')
            out.append('  </table>')

        out.append('</div>')  # /week block

    out.append('</div><!-- /sched-wrap -->')
    return "\n".join(out)


if __name__ == "__main__":
    # Always run from the script's own directory (quarto-site/)
    os.chdir(Path(__file__).parent)
    rows  = load_rows()
    weeks = group_rows(rows)
    html_out = build_html(weeks)
    OUTPUT_FILE.write_text(html_out, encoding="utf-8")
    print(f"[schedule] Generated {OUTPUT_FILE} ({len(html_out):,} bytes, {len(rows)} periods).")
