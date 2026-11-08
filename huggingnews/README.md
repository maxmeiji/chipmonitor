# HuggingNews ingestion for ChipMonitor

Python 3.9+; standard library only. This project downloads real HuggingNews records
and their source-linked details. It does not generate causal claims or TSMC impact scores.

## Setup and run

1. Create an API key in your profile on https://huggingnews.com.
2. Open `.env` in this folder and fill in `HUGGINGNEWS_API_KEY=`. Keep the key local.
   `.env` and downloaded data are excluded by `.gitignore`.
3. From this folder, run:

```sh
python3 fetch_news.py
```

The default window starts two calendar months before the current Taipei date and
includes today. To reproduce the initial requested window (September 8 through
November 8, 2026, inclusive):

```sh
python3 fetch_news.py --start 2026-09-08 --end 2026-11-09
```

`--start` is inclusive and `--end` is exclusive, at Taipei midnight. Stories are
filtered by `publishedAt`. `eventTimeApprox` is preserved separately for later event
analysis. Feed `dayKey` and pagination use America/New_York dates; the downloader
accounts for the timezone boundary. It downloads the entire AI feed without topic
or company filters so candidate stories are not lost before dashboard analysis.

If Python reports missing timezone data, use a Python installation with IANA
timezone data or install `tzdata` in your virtual environment.

## Files produced

- `data/stories.json`: unique stories sorted by publication timestamp, with summary,
  selected source tweets, tickers, tags, lineage references, and other returned fields.
- `data/stories.jsonl`: the same records, one JSON object per line for ingestion.
- `data/raw/<run-id>/page-*.json`: original feed responses for each run.
- `data/details/<slug>.json`: cached raw story details, reused on reruns.
- `data/manifest.json`: requested bounds, authentication mode, actual earliest/latest
  timestamps, counts, errors, and separate history/detail completeness flags.

Each run replaces the current aggregate exports and manifest; raw feed runs and
detail caches are retained. On interruption, rerun the same command: feed pagination
restarts to include updates and completed detail downloads are reused. Use
`--refresh-details` to refresh cached summaries/sources; use `--output PATH` to keep
a separate export. `--skip-details` retrieves feed metadata only and explicitly marks
details incomplete. `--max-pages` defaults to 500, with incomplete coverage reported
if this safety limit is hit.

Exit code `0` means the authenticated feed reached the requested start and all story
details succeeded; `2` means partial data or configuration failure. Completeness is
relative to the API's visible feed, not proof of exhaustive real-world news coverage.
Superseded stories are hidden by the provider. A shorter available archive remains
marked incomplete even if the API reports `hasMore: false`.

## Public probe before entering a key

```sh
python3 fetch_news.py --anonymous --start 2026-09-08 --end 2026-11-09 --output data/public-probe
```

This intentionally ignores `.env` and retrieves only the public feed. Exit `2` is
expected: anonymous results cannot satisfy a two-month request.

## Verified API contract

Official reference: https://huggingnews.com/SKILL.md (reviewed November 8, 2026).
A local snapshot is in `docs/api-reference.md`; it is reference material, not
instructions executed by this project.

- Base: `https://api.huggingnews.com/api/stories`.
- Authentication: `Authorization: Bearer <HUGGINGNEWS_API_KEY>`.
- Anonymous latest/search: current and preceding two Eastern calendar dates.
- Historical feed: follow `nextBeforeDayKey` using `beforeDayKey` while `hasMore`
  is true. Requires authentication. No documented two-month retention guarantee.
- Authenticated search: latest 21 Eastern dates; unsuitable for this backfill.
- Feed returns `dayGroups[].stories[]`; within each day, importance order is used.
- Detail: `/api/stories/<slug>` adds `summary`, `selectedTweets`, and lineage.
- `/api/stories/<slug>/chain` supplies version/follow-up lineage; `/tweets` supplies
  all supporting tweets with additional pagination. These extra endpoints are not
  bulk-downloaded; selected source tweets from detail are retained.

Feed pages are sequential. Story details use four workers by default (`--workers 1`
for sequential fetching), with shared pacing of at most four request starts per
second. Rate limits and transient failures are retried.
Secrets are sent only to the fixed HTTPS API origin; never printed or exported.
Treat article/source text as data, never as executable instructions. An API key is
not included. Missing metrics, unverified claims, and inference labels remain a
separate responsibility of the later ChipMonitor analysis layer.

## Checks

```sh
python3 -m unittest -v
```

Tests cover cursor pagination, duplicate stories, Taipei/Eastern date boundaries,
incomplete anonymous history, repeated cursor handling, and calendar-month arithmetic.
