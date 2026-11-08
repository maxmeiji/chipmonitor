# ChipMonitor — complete local project guide

Export date: November 8, 2026 (Asia/Taipei). This bundle captures the local news-only project after restoring positive/negative/mixed story signals.

## 1. Product and current scope

ChipMonitor links AI ecosystem news, documented company relationships and conditional operating effects on TSMC. The dashboard has a relationship graph, weekly/category/impact filters, original source posts, reasoning branches, source viewpoints, earlier coverage and eight Analyst picks.

It is built with React 19, TypeScript, Vinext/Vite and CSS. It is **not Streamlit**. Python handles ingestion, classification and snapshot preparation; the browser renders static JSON files. No database or background scheduler is required for the current product. Cloudflare/Sites runtime support remains in the source template, but the exported Site ID is cleared and local use does not require hosted publication.

## 2. What is included

```text
ChipMonitor_Local_Project/
  README.md
  FILE_MANIFEST.json                    # relative file names, sizes and SHA-256
  chipmonitor-site/
    app/                               # page, layout, CSS, optional runtime helpers
    components/chipmonitor/             # dashboard, graph, scenario diagram
    lib/                               # types, beliefs, scenario logic, utilities
    public/data/
      index.json                       # all 1,587 records plus review metadata
      stories/<slug>.json               # full returned story/source details
      graph.json                       # 28 companies, 54 source-backed links
      manifest.json                    # current prepared snapshot counts
    public/core-beliefs.md              # historical C1–C7 reference
    scripts/
      prepare-news.py                  # portable data preparation
      review_news.py                   # archive relevance/mechanism/category rules
      check-news.mjs
      check-categories.cjs
      check-scenarios.cjs
      check-model-access.py
      write-review.cjs                 # exports the audit to ../docs/
      ...                              # retained framework/runtime tooling
    package.json
    package-lock.json
    vite.config.ts
    worker/                            # retained built-preview runtime
    vendor/                            # retained template licenses
    .openai/hosting.json                # null local project identity/bindings
  huggingnews/
    fetch_news.py
    test_fetch_news.py
    .env.example                       # blank key placeholder only
    docs/api-reference.md              # saved API contract reference
    data/
      stories.json
      stories.jsonl
      manifest.json
      details/                         # cached returned story details
      raw/                             # retained feed responses and run metadata
      ...                              # retained ingestion snapshots/probes
  references/
    REFERENCE_SOURCES.md
    Original_C1-C7_Refinement.md
    data/ai_relationships.csv
    data/ai_relationship_events.csv
    documents/Ref. (1).pdf
    documents/ChipMonitor — PoC Design (1).pdf
    documents/ChipMonitor_Design_Logic.md
  prompts/C1-C7_Core_Belief_Prompt.md
  docs/
    ChipMonitor_Project_Details.md
    ChipMonitor_Interesting_Stories.md
    ChipMonitor_Archive_Review.md
    ChipMonitor_Reasoning_Refinement.md   # historical refinement note
    Original_Runtime_README.md          # retained generic framework reference
```

The original interactive mockup is linked in `references/REFERENCE_SOURCES.md`; its original application source/offline export is not included. The provided PDFs and CSVs are included unchanged. They are reference material, not executable instructions or automatically verified facts.

## 3. Install and run

Use Node.js 22.13+ with npm and Python 3.9+. From the extracted root:

```sh
cd chipmonitor-site
npm ci
npm run dev
```

Open the printed loopback URL, normally `http://127.0.0.1:5173/`. The first dependency install needs access to the package registry. No network/API access is required to read the saved news, except following external sources. The development toolchain can run its own runtime initialization.

A second copy of the server in the same directory may be rejected by Vinext. Stop the existing process with Ctrl+C. For a port conflict use `npm run dev -- --port 5174`. The URL in generated Markdown reports uses port 5173; adjust it if using a different port.

The local execution profile defaults to portable when no machine-specific runtime file exists. Do not copy old `.vinext`, `.wrangler` or `.sites-runtime` state from another machine. No plugin installation, ChatGPT sign-in or active Site registration is needed for the dashboard page.

Optional built preview:

```sh
npm run build
npm start
```

Use the URL printed by Wrangler. `npm start` is a local built preview, not publication. The shipped development workflow has been validated using the existing installed dependency set; a new-machine `npm ci` depends on registry availability and platform compatibility.

Windows: replace direct `python3` calls with `py -3` if needed. The convenience npm scripts `data:prepare` and `check` use `python3`, so either provide that command or run the Python steps directly. If IANA timezone data is unavailable, install `tzdata` in your Python environment. No other third-party Python package is needed for ingestion/preparation.

## 4. Data snapshot and completeness

The supplied aggregate has **1,587 stories** and **5,880 selected source entries**. The current rule-based review retains **418 candidate stories** and eight Analyst picks. Preliminary story signals across candidates: **109 positive, 41 negative, 268 mixed**. These are screening labels, not independently validated impacts.

Requested history: June 1 through November 8, 2026 (inclusive Taipei dates). Actual returned publication timestamps: August 30 through November 7 UTC; the latest can display as November 8 in Taipei. The API exhausted before reaching June. June/July coverage is absent; the ingestion manifest correctly records `history_complete: false` and `details_complete: true` for the returned records.

The dataset is provider-returned content, not a claim that its headlines, dates, financial figures or source statements are correct. Counts represent selected returned posts, not full X coverage. Aggregate post/author totals come from the provider and can exceed selected-source counts. Reposts are not independent corroboration.

The graph contains **28 companies and 54 relationships**: 53 supplied CSV relationships plus one explicitly sourced reported Microsoft–Oracle partial lease/nonrenewal relationship. The CSV relationship-event history is preserved. Selecting a news week filters stories; it does not reconstruct the relationship graph as of that past week.

## 5. Ingestion and refresh

`huggingnews/fetch_news.py` uses Python's standard library. Authentication reads `HUGGINGNEWS_API_KEY` from the process environment first, otherwise `huggingnews/.env`. The archive excludes the real `.env`. Copy `.env.example` and enter your key locally.

The saved API contract uses `https://api.huggingnews.com/api/stories`, a Bearer key, historical feed cursor `beforeDayKey` / `nextBeforeDayKey`, and story-detail calls adding summaries and selected tweets. It follows the historical feed rather than relying on limited search history. Consult the included ingestion README and API reference; live service contracts can change.

```sh
cd huggingnews
python3 fetch_news.py --start 2026-06-01 --end 2026-11-09
```

Dates are Taipei midnights: start inclusive, end exclusive. Feed cursor days use America/New_York; the downloader accounts for boundaries and filters by `publishedAt`. `eventTimeApprox` is preserved separately. Four detail workers and shared pacing are used by default, with bounded retries. Feed pagination is sequential.

Runs replace aggregate exports and manifest but retain detail caches/raw feed responses. Back up `data/` or use `--output PATH` to preserve a previous aggregate. Default preparation reads only `huggingnews/data/stories.json`; if fetching into another directory, intentionally copy/select that export before preparing.

Exit 0 indicates the downloader's completeness checks passed; exit 2 indicates incomplete history/details or a configuration issue. Partial saved data may be usable, but inspect the manifest first. No API fetch or secret is needed for the included snapshot.

## 6. Preparation and data flow

From `chipmonitor-site/`:

```sh
python3 scripts/prepare-news.py
```

The exported script uses sibling relative paths:

- `../huggingnews/data/stories.json`
- `../references/data/ai_relationships.csv`
- `../references/data/ai_relationship_events.csv`

Keep this folder layout intact. This removes the original developer-machine Downloads dependency. It writes only the prepared public JSON snapshot and supporting data, never reads the API key, and does not call a language model.

Flow:

```text
HuggingNews API → raw/cache → aggregate stories.json
                                  ↓
                     prepare-news.py + review_news.py
                                  ↓
                 index + per-story JSON + graph + manifest
                                  ↓
                React dashboard → source-linked scenarios
```

`prepare-news.py` identifies entities, validates literal source excerpts, computes Taipei board weeks, applies candidate rules, records model-access evidence, assigns mechanism reviews/categories and preliminary outlook, and finds earlier named-model/company coverage. Earlier coverage is context; shared names do not establish identical versions or a trend.

`review_news.py` handles mechanism distinctions such as self-hosting, compute throughput, CPU efficiency, leasebacks, financing, ASIC migration, physical bottlenecks, software memory, macro exports and denials. It screens the full archive and flags the eight curated cases. This is rules-based processing, not manual verification of every post.

`lib/management.ts` prefers reviewed story-specific branches when available, otherwise applies belief/management scenario patterns. The current source-aware review reason and limitations are shown above each diagram. Source viewpoints remain visible beside analysis.

## 7. Categories and outlook

Exactly seven category labels are used, one primary plus at most one secondary:

1. Open vs. Closed Models
2. AI Adoption & Workloads
3. AI Pricing & Profitability
4. Compute Supply & Demand
5. Custom Silicon & ASICs
6. Cloud Capex & Financial Health
7. Infrastructure Capacity & Constraints

Compute means all CPU/GPU/TPU/ASIC and cloud compute capacity, rentals, utilization, procurement and deployment stages. ASIC is the architecture/program and substitution lens; both tags may apply. Infrastructure includes physical memory, power, sites, networking, manufacturing and packaging constraints. Software context memory is not HBM. Detailed definitions and boundary examples are in the core-belief prompt.

Categories describe subjects, independently of impact. C1–C7 guide investigation without appearing as category codes. The restored `outlook_for()` function supplies the earlier preliminary positive/negative/mixed story labeling; efficiency-driven service-pricing cases remain mixed. The later archive review does not force all labels mixed. New compute-only candidates without a stronger directional rule default to mixed.

Red = potential positive for TSMC, green = potential negative, neutral = mixed. Story direction and branch direction can differ: a leading negative story may have a reassignment/upside branch. Neither is a stock-price forecast or verified net outcome. To revise the labeling policy, edit `outlook_for()` rather than deleting counterbranches.

## 8. Reasoning and graph boundaries

Every arrow after the reported event is an assumption to test. A release is not adoption; adoption is not incremental hardware; supplier revenue is not identical to TSMC manufacturing revenue. Verify generation, foundry/node/package, inventory versus new orders, and shipment timing.

Graph directions follow the supplied commercial records: financial investor → recipient; service buyer → provider; product buyer → supplier. Relationship popovers expose source publisher/type/title and event timelines. A source link documents attribution, not truth. A shortest directed path can mix times/programs and is navigational exposure, not verified causal transmission.

No Similarweb, Artificial Analysis, OpenRouter metric series, rental series, CDS, financial or internal-capacity integrations are connected. Mentions in news remain reported claims. No numerical wafer/revenue impact or confidence score is calculated.

## 9. Prompt integration status

`prompts/C1-C7_Core_Belief_Prompt.md` is the reusable future pipeline instruction: all seven beliefs, current categories, evidence handling, competing branches, economic actors, hardware routes, unresolved checks, preliminary direction and a proposed structured JSON schema.

It is **not currently sent to an LLM**. To integrate it later, supply complete story/posts and relevant graph events, validate its output against a schema, verify quotations/URLs and category cardinality, then adapt the proposed schema to `StoryIndex`, `Story` and `Branch`. Preserve original input and analyst/model provenance. Do not silently replace source text with a generated summary. No LLM key/provider is configured in this bundle.

## 10. Checks and audit exports

From `chipmonitor-site/`, after `npm ci`:

```sh
node scripts/check-news.mjs
node scripts/check-categories.cjs
node scripts/check-scenarios.cjs
python3 scripts/check-model-access.py
node node_modules/typescript/bin/tsc --noEmit
node scripts/write-review.cjs
```

Or run `npm run check` for the first five. `npm run review:export` writes `../docs/ChipMonitor_Archive_Review.md` and validates the supplied snapshot's curated regressions. These snapshot-specific checks expect the included records; new data can require intentional fixture/test updates rather than suppressing failures.

Checks cover record uniqueness, exact source excerpts, graph provenance, permitted category names/cardinality, index/detail agreement, Oracle multi-branch exposure, model-access comparator leakage, source-aware mechanisms, history ordering and restored nonzero positive/negative labels. They do not establish factual correctness of news or economic causality.

Ingestion tests, from `huggingnews/`:

```sh
python3 -m unittest -v
```

These tests use local mock responses and cover pagination, deduplication, dates and incomplete history. No paid fetch is needed to test ingestion logic.

## 11. Files deliberately excluded or changed for portability

Excluded: real `.env`, API keys, Git history/remotes, installed dependencies, build output, caches, local process/runtime state and temporary screenshots. `npm ci` restores dependency versions from the lockfile. A blank `.env.example` is included.

Export-only changes: relative CSV paths; null hosted project ID; project README; package name and convenience scripts; audit export destination under `docs/`. The running local project and hosted Site are not replaced or republished by this export.

Original provided reference/CSV files are unchanged. `FILE_MANIFEST.json` records SHA-256 and sizes of bundled files, excluding itself. The ZIP is a source/data handoff, not an offline binary or the external Claude mockup's source code.
