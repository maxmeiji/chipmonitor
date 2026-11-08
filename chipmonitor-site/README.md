# ChipMonitor — local project bundle

React + TypeScript (Vinext) dashboard, HuggingNews downloader, real saved news snapshot, relationship CSVs, provided references, core-belief prompt and project documentation.

## Run the saved dashboard

Prerequisites: Node.js **22.13+**, npm, and Python **3.9+** for data preparation/checks. No API key is needed to view the bundled snapshot.

From this extracted folder:

```sh
cd chipmonitor-site
npm ci
npm run dev
```

Open **http://127.0.0.1:5173/**. Keep the terminal running; Ctrl+C stops it. If the port is occupied, use `npm run dev -- --port 5174` and open the printed address. The application is a local news snapshot, not a live feed. Start with **Analyst picks** for the eight shortlisted stories.

On Windows, use `py -3` instead of `python3` for Python commands if necessary. The npm data/check commands expect a `python3` executable; alternatively run their constituent commands from the project guide.

## Refresh news (optional)

Create `huggingnews/.env` by copying `huggingnews/.env.example`, then enter your own key:

```dotenv
HUGGINGNEWS_API_KEY=your_key_here
```

From the bundle root:

```sh
cd huggingnews
python3 fetch_news.py --start 2026-06-01 --end 2026-11-09
```

Choose your own dates for a new window. Start is inclusive, end exclusive, at Taipei midnight. An incomplete archive returns exit code 2 but can still save usable data; inspect `data/manifest.json` before deciding whether to prepare it. Back up `huggingnews/data/` before fetching if you want to retain this exact aggregate snapshot.

Then, from the bundle root:

```sh
cd chipmonitor-site
python3 scripts/prepare-news.py
npm run dev
```

The preparation script uses `../huggingnews/data/stories.json` and the bundled `../references/data/*.csv`. Refresh the browser after rebuilding. Keep the sibling folders together.

## Included documents

- **`prompts/C1-C7_Core_Belief_Prompt.md`** — current reusable analysis prompt, seven category definitions, C1–C7, branching, source rules and proposed JSON output.
- **`docs/ChipMonitor_Project_Details.md`** — setup, architecture, files, data definitions, reasoning behavior, checks and limitations.
- **`docs/ChipMonitor_Interesting_Stories.md`** — eight stories and their interesting mechanisms, original post links and validation questions.
- **`docs/ChipMonitor_Archive_Review.md`** — archive screening and candidate-by-candidate reasoning.
- **`references/`** — supplied PDFs, original design logic, both CSVs and original belief refinement.

The API key, Git history, `node_modules`, build caches and live Site identity are excluded. Dependencies are reinstalled with `npm ci`; the ZIP is source plus data, not a fully offline executable. No publishing, live account or Sites plugin is needed to run it locally.

The prompt is included for future integration. Current classification/reasoning uses transparent rules and templates, not an automated language-model API call. News and source posts may be wrong; directional colors are preliminary hypotheses.
