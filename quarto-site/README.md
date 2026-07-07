# Maker-X Course Website

This is the source for the Maker-X course website — a Quarto static site for ShanghaiTech University's summer Maker-X program (a joint offering across the School of Creativity & Art, School of Information Science & Technology, School of Entrepreneurship and Management, and Kedao College).

The site is built once from plain text/markdown files and deployed automatically whenever you push to GitHub. You do not need to know HTML or web development to maintain it — most updates are small edits to `.qmd` files or a CSV.

---

## 1. The big picture

- **Quarto** (https://quarto.org) is the tool that turns the `.qmd` (Quarto Markdown) files in this folder into the actual HTML website, in a folder called `_site/`.
- The site is deployed in **two parallel places**:
  - **Vercel** — the primary deployment, at `courses-maker-x.vercel.app`. It rebuilds automatically every time you `git push`.
  - **GitHub Pages** — a secondary deployment, pushed manually with `quarto publish gh-pages`.
- All source files live in this folder (`quarto-site/`), inside the git repository rooted one level up, at `1 - MakerX/`.
- You never need to hand-edit anything inside `_site/` — that folder is regenerated every time you run `quarto render` and gets overwritten.

---

## 2. What each file does

| File / folder | Purpose |
|---|---|
| `_quarto.yml` | Site-wide configuration: navbar links, sidebar, footer, theme. |
| `index.qmd` | Homepage. |
| `schedule.qmd` | Full class schedule page. The table itself is generated automatically — see Section 4. |
| `setup.qmd` | "Get Ready for the Course" — pre-course setup checklist for students. |
| `team.qmd` | Instructors and guest lecturers. |
| `resources.qmd` | Tools and resource links. |
| `week1.qmd` … `week4.qmd` | Weekly content pages. |
| `custom.scss` | Visual styling overrides (colors, fonts, spacing). |
| `generate_schedule.py` | Script that builds the schedule table. Runs automatically before every render. |
| `_schedule_data.csv` | The data behind the schedule table (topics, instructors, dates, times). **Edit this to change the schedule.** |
| `_schedule_generated.html` | Auto-generated output of the script above. Never edit this by hand — it gets overwritten every render. |
| `images/` | Logo, team photo, and other images used on the site. |
| `vercel.json` | Tells Vercel where to find the built site (`_site/`). |

---

## 3. Day-to-day workflow: editing any page

Every normal update follows the same four steps.

1. **Open the relevant `.qmd` file** in any text editor (e.g. VS Code, TextEdit, or even Claude). `.qmd` files are mostly plain Markdown — the same `**bold**`, `### Heading`, `- bullet list` syntax used everywhere — with occasional chunks of HTML for things like colored badges.
2. **Make your edit** and save the file.
3. **Rebuild the site**, in Terminal:
   ```bash
   cd "/Users/shimonshmueli/Documents/ShanghaiTech/My Courses/1 - MakerX/quarto-site"
   quarto render
   ```
   This regenerates everything in `_site/`. (Optional: run `quarto preview` instead to open a live local preview in your browser while you edit.)
4. **Commit and push**, in Terminal:
   ```bash
   cd "/Users/shimonshmueli/Documents/ShanghaiTech/My Courses/1 - MakerX"
   git add quarto-site/
   git commit -m "Describe what you changed"
   git push
   ```
   Vercel picks this up automatically and the live site updates within a minute or two. No further action needed for Vercel.

5. **(Optional) Also update GitHub Pages**, since it doesn't auto-deploy from `git push`:
   ```bash
   cd "/Users/shimonshmueli/Documents/ShanghaiTech/My Courses/1 - MakerX/quarto-site"
   quarto publish gh-pages
   ```

---

## 4. How to update the class schedule

The schedule table on `schedule.qmd` is **not** typed directly into that file — it's generated from a data file, so you can update the whole term's schedule without touching any HTML.

### Option A — Edit the CSV directly (current setup)

Open this file in a spreadsheet app (Excel, Numbers, Google Sheets — open and re-export) or a text editor:

```
quarto-site/_schedule_data.csv
```

Each row is one class period. Columns:

| Column | Meaning | Example |
|---|---|---|
| `week` | Week number | `1` |
| `session` | Session number, 1–8 across the course | `3` |
| `date` | Display date | `July 8` |
| `day` | Day of week | `Wednesday` |
| `block` | `Morning` or `Afternoon` | `Morning` |
| `period` | Period number within the block, 1–6 | `2` |
| `time` | Display time range | `10:15–11:00` |
| `topic` | What's covered in that period | `ESP32 hands-on` |
| `guest` | `yes` if this is a guest-led period (prefixes topic with "Guest:") | `yes` or blank |
| `instructors` | Who's teaching, comma-separated. **Use quotes if more than one person**, e.g. `"shimon,daniel"` | `daniel` or `"liang,shimon,daniel"` |
| `highlight` | Special row styling: `guest`, `poster`, `demo`, `zhou`, or blank | `demo` |

Valid instructor keys: `liang`, `shimon`, `daniel`, `junjun`, `espressif`, `zhou`, `all`.

After editing the CSV, rebuild and push exactly as in Section 3 (steps 3–4). The schedule page will reflect your changes — no other file needs to change.

### Option B — Connect a live Google Sheet (not yet active)

The generator script already supports pulling from a published Google Sheet instead of the local CSV, for cases where someone other than you needs to edit the schedule without touching a CSV file or git.

To turn this on:

1. In Google Sheets, recreate the same columns as the CSV above (one row per period).
2. **File → Share → Publish to web**, choose **Comma-separated values (.csv)**, and publish. Copy the resulting URL.
3. Open `quarto-site/generate_schedule.py` and find this line near the top:
   ```python
   SHEET_URL = "YOUR_GOOGLE_SHEETS_CSV_URL_HERE"
   ```
   Replace the placeholder with the published CSV URL.
4. From then on, every `quarto render` fetches the latest sheet data automatically and writes a local cached copy to `_schedule_data.csv`. If the sheet is ever unreachable at render time (no internet, sheet unpublished, etc.), the script falls back to that cached CSV so the build never breaks.

You don't have to choose this now — the CSV-only workflow in Option A works fine indefinitely.

---

## 5. Common edits, explained

- **Add a new guest lecturer or instructor bio** → edit `team.qmd`. Copy an existing instructor's HTML block as a template.
- **Add or change a resource link** → edit `resources.qmd` (general tools) or the "Resources for Week N" section at the bottom of the relevant `weekN.qmd`.
- **Change colors, fonts, spacing** → edit `custom.scss`. Each rule is scoped to a CSS class — search for the class name (e.g. `.navbar-logo`) shown in browser dev tools if you're not sure which rule controls something.
- **Replace the team photo** → save the new image as `quarto-site/images/team.png` (same filename, so no code change is needed), then render and push.
- **Add a new navbar or sidebar link** → edit the `navbar:` and `sidebar:` sections in `_quarto.yml`.

---

## 6. Troubleshooting

**"Another git process seems to be running" / `index.lock` error**
A previous git command was interrupted and left a stale lock file. As long as nothing else is actively running git, it's safe to remove:
```bash
cd "/Users/shimonshmueli/Documents/ShanghaiTech/My Courses/1 - MakerX"
rm -f .git/index.lock
```

**Working folder looks empty, but you know you've made changes**
Your edits are very likely still safe in git history even if files vanished from disk. Check first:
```bash
cd "/Users/shimonshmueli/Documents/ShanghaiTech/My Courses/1 - MakerX"
git status
git log --oneline -5
```
If `git status` lists your files as "deleted" (rather than git itself looking broken), restore them with:
```bash
git checkout -- .
```

**A style change isn't showing up on the live site**
1. Confirm you ran `quarto render` after editing `custom.scss` or any `.qmd` file — edits to source files do nothing to the live site until rendered.
2. Confirm you committed and pushed `quarto-site/` (not just rendered locally).
3. Hard-refresh your browser (Cmd+Shift+R) — stale browser cache is a common false alarm.
4. If a CSS property seems to have no effect, check whether a more specific rule elsewhere is overriding it (this happened with the navbar logo size, which required overriding both `height` and `max-height`).

**Vercel is showing an old version of the site**
Vercel only deploys what's actually committed and pushed to GitHub. Run `git status` locally to check for uncommitted or unpushed changes before assuming Vercel is broken.

---

## 7. Quick reference: full render-and-publish command block

```bash
cd "/Users/shimonshmueli/Documents/ShanghaiTech/My Courses/1 - MakerX/quarto-site"
quarto render
cd ..
git add quarto-site/
git commit -m "Describe your change"
git push
```

That's it — Vercel updates automatically. Add `quarto publish gh-pages` (run from inside `quarto-site/`) if you also want to push to the GitHub Pages mirror.
