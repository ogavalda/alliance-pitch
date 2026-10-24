# Alliance pitch page

A one-page storytelling site, generated from plain files so you can change **text, numbers and charts** without touching HTML.

```
content/text.yaml      all the words (and the lists: jobs, roles, options, questions...)
content/numbers.yaml   all the numbers and chart inputs (stats, network nodes, slider, feeder profile)
content/tools.yaml     the tool landscape (one entry per tool) and the five shared-core layers
content/budget.yaml    the budget (costs and incomes per year); build.py warns if totals do not add up
content/layout.yaml    which sections show up, and in what order (chapters are numbered automatically)
src/charts.py          how the charts are drawn (SVG, generated in Python)
src/templates/         HTML templates (one file per section)
src/static/            style.css and app.js (look and behaviour)
assets/logos/          logo files (embedded into the page at build time)
build.py               builds docs/index.html
docs/index.html        the result: one self-contained file, no internet needed
```

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python build.py            # writes docs/index.html
python build.py --serve    # live preview at http://localhost:8000, rebuilds when you save a file
```

Open `docs/index.html` in any browser. To publish, push the repo to GitHub and enable Pages on the `docs/` folder.

## What to edit

| I want to change... | Edit |
| --- | --- |
| a headline, paragraph, tab, table or question | `content/text.yaml` |
| the big statistics (9 → 90 GW, 8,000+) | `content/numbers.yaml` > `stats` (the explanation under each is in `text.yaml` > `why.cards`) |
| the network picture (dots, positions, colours) | `numbers.yaml` > `network`, `palette` |
| the budget chapter, its charts and table | `content/budget.yaml` (text in `text.yaml` > `budget`) |
| the feeder-load chart (optional section) | `numbers.yaml` > `feeder`; set `demo` to `enabled: true` in `layout.yaml` |
| add or correct a tool, change the core layers | `content/tools.yaml` (a `?` means not documented; `diagram: true` puts a tool in the stack diagram). `python export_tools.py` writes `tools_register.xlsx` |
| section order, hide a section | `content/layout.yaml` |
| chart styling | `src/charts.py` |
| colours, fonts, spacing | `src/static/style.css` (palette at the top, in `:root`) and `numbers.yaml` > `palette` for the charts |
| logos | drop the files in `assets/logos/` (`ngci.png`, `irec.png`) and list them in `text.yaml` > `logos` |

Rules for the YAML files: keep the indentation, put text with colons inside double quotes, and use `<b>`, `<em>` for emphasis. After editing, run `python build.py` (or use `--serve`). If something is wrong, the build tells you which section is missing.

## Add a new section

1. Add a block with the section id in `content/text.yaml` and its label in `nav`.
2. Create `src/templates/sections/<id>.j2` (copy `roadmap.j2` as a starting point).
3. List the id in `content/layout.yaml`.

## Check

```bash
python tests/test_build.py     # or: python -m pytest -q
```

## Notes

Theme: Concordia palette (burgundy 93002D, pink E90065, blue 1598D6, green 00776F, orange E83F21) and Arial throughout.

Charts are illustrations with hypothetical numbers unless stated; keep that wording if you change them. Placeholders written as `[?]` are for you to fill in.
