#!/usr/bin/env python3
"""Download HuggingNews history using the documented read-only API (Python 3.9+)."""
import argparse
import calendar
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, time, timedelta, timezone
from email.utils import parsedate_to_datetime
import json
import os
from pathlib import Path
import sys
import threading
import time as clock
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
API = "https://api.huggingnews.com/api/stories"
TAIPEI = ZoneInfo("Asia/Taipei")
EASTERN = ZoneInfo("America/New_York")


def read_key(path):
    """Read only this project's key; environment variables take precedence."""
    if "HUGGINGNEWS_API_KEY" in os.environ:
        return os.environ["HUGGINGNEWS_API_KEY"].strip()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            name, sep, value = line.strip().removeprefix("export ").partition("=")
            if sep and name.strip() == "HUGGINGNEWS_API_KEY":
                return value.strip().strip("\"'")
    return ""


def months_before(day, count=2):
    number = day.year * 12 + day.month - 1 - count
    year, month0 = divmod(number, 12)
    month = month0 + 1
    return day.replace(year=year, month=month,
                       day=min(day.day, calendar.monthrange(year, month)[1]))


def stamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("API timestamp has no timezone")
    return result


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


class Client:
    def __init__(self, key, delay=0.25):
        self.key = key
        self.delay = delay
        self.lock = threading.Lock()
        self.last_request = 0.0

    def get(self, suffix="", params=None):
        url = API + suffix + (("?" + urlencode(params)) if params else "")
        headers = {"Accept": "application/json", "User-Agent": "ChipMonitor-HuggingNews/0.1"}
        if self.key:
            headers["Authorization"] = "Bearer " + self.key
        for attempt in range(5):
            with self.lock:
                clock.sleep(max(0, self.delay - (clock.monotonic() - self.last_request)))
                self.last_request = clock.monotonic()
            try:
                with urlopen(Request(url, headers=headers), timeout=45) as response:
                    return json.load(response)
            except HTTPError as exc:
                if exc.code not in (429, 500, 502, 503, 504) or attempt == 4:
                    # Do not log response bodies or request headers (may contain secrets).
                    raise RuntimeError(f"HuggingNews HTTP {exc.code}; check key/access or retry later.") from None
                retry = exc.headers.get("Retry-After", "")
                try:
                    wait = float(retry)
                except ValueError:
                    try:
                        wait = (parsedate_to_datetime(retry) - datetime.now(timezone.utc)).total_seconds()
                    except (ValueError, TypeError):
                        wait = 2 ** attempt
                if wait > 60:
                    raise RuntimeError("Rate limited for over 60 seconds. Rerun later; cached details are retained.") from None
                clock.sleep(max(0, wait))
            except (URLError, TimeoutError):
                if attempt == 4:
                    raise RuntimeError("HuggingNews network request failed after five attempts.") from None
                clock.sleep(2 ** attempt)


def collect(client, start, end, out, details=True, max_pages=500, refresh=False, workers=4):
    """Bounds are Taipei midnights; end is exclusive; filter by publishedAt."""
    out.mkdir(parents=True, exist_ok=True)
    start_at = datetime.combine(start, time.min, TAIPEI)
    end_at = datetime.combine(end, time.min, TAIPEI)
    # Feed dayKey uses Eastern time. Include the entire boundary day before stopping.
    stop_day = start_at.astimezone(EASTERN).date().isoformat()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    raw_dir = out / "raw" / run_id
    stories, cursors = {}, set()
    cursor = None
    report = {"requested_start_inclusive": start.isoformat(),
              "requested_end_exclusive": end.isoformat(), "timezone": "Asia/Taipei",
              "filter_field": "publishedAt", "authenticated": bool(client.key),
              "history_complete": False, "details_complete": False,
              "pages_fetched": 0, "run_id": run_id,
              "raw_directory": str(raw_dir.relative_to(out)),
              "source": API, "limitations": []}
    detail_failures = []
    try:
        for page_num in range(max_pages):
            page = client.get(params={"beforeDayKey": cursor} if cursor else None)
            save_json(raw_dir / f"page-{page_num + 1:04d}.json", page)
            report["pages_fetched"] += 1
            groups = page.get("dayGroups")
            if not isinstance(groups, list):
                raise RuntimeError("Unexpected response: dayGroups is not an array.")
            days = []
            for group in groups:
                days.append(group["dayKey"])
                for story in group["stories"]:
                    published = stamp(story["publishedAt"])
                    if start_at <= published < end_at:
                        stories[story["slug"]] = dict(story)
            print(f"Page {page_num + 1}: {len(stories)} unique stories in requested window", flush=True)
            if days and min(days) <= stop_day:
                report["history_complete"] = bool(client.key)
                report["stop_reason"] = "Reached requested start day"
                break
            if not page.get("hasMore"):
                report["stop_reason"] = "API feed exhausted before requested start"
                report["limitations"].append("Requested start was not reached; available archive may be shorter than requested.")
                break
            next_cursor = page.get("nextBeforeDayKey")
            if not next_cursor or next_cursor in cursors:
                raise RuntimeError("Missing or repeated pagination cursor; refusing to claim complete coverage.")
            if not client.key:
                report["stop_reason"] = "API key required for historical pagination"
                break
            cursors.add(next_cursor)
            cursor = next_cursor
        else:
            report["stop_reason"] = "Page safety limit reached; increase --max-pages"

        if not client.key:
            report["limitations"].append("Anonymous feed covers only current and preceding two Eastern calendar dates. Enter API key and rerun for history.")
        if details:
            def fetch_detail(slug):
                # Slugs are remote data: encode them and keep cache filenames path-safe.
                encoded = quote(slug, safe="")
                cache = out / "details" / (encoded + ".json")
                detail = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() and not refresh else client.get("/" + encoded)
                if detail.get("slug") != slug or "summary" not in detail:
                    raise RuntimeError("Story detail is missing expected slug or summary.")
                save_json(cache, detail)
                return detail

            with ThreadPoolExecutor(max_workers=workers) as pool:
                pending = {pool.submit(fetch_detail, slug): slug for slug in sorted(stories)}
                for index, future in enumerate(as_completed(pending), 1):
                    slug = pending[future]
                    try:
                        stories[slug].update(future.result())
                    except (RuntimeError, ValueError, OSError) as exc:
                        detail_failures.append({"slug": slug, "error": str(exc)})
                    if index % 25 == 0 or index == len(stories):
                        print(f"Story details: {index}/{len(stories)} processed", flush=True)
            report["details_complete"] = not detail_failures
        else:
            report["limitations"].append("Details skipped: summaries and selected source tweets have not been fetched.")
    except (RuntimeError, ValueError, KeyError, OSError) as exc:
        report["error"] = str(exc)
    except KeyboardInterrupt:
        report["error"] = "Interrupted; rerun to reuse cached story details."
    finally:
        records = sorted(stories.values(), key=lambda s: (s["publishedAt"], s["slug"]))
        for record in records:
            record["huggingnews_url"] = "https://huggingnews.com/ai/" + quote(record["slug"], safe="")
        save_json(out / "stories.json", records)
        tmp = out / "stories.jsonl.tmp"
        tmp.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in records), encoding="utf-8")
        tmp.replace(out / "stories.jsonl")
        report.update({"story_count": len(records), "detail_failures": detail_failures,
                       "earliest_published_at": records[0]["publishedAt"] if records else None,
                       "latest_published_at": records[-1]["publishedAt"] if records else None,
                       "finished_at": datetime.now(timezone.utc).isoformat()})
        save_json(out / "manifest.json", report)
    return report


def main():
    today = datetime.now(TAIPEI).date()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat, default=months_before(today), help="Inclusive date, Taipei; default two calendar months ago")
    parser.add_argument("--end", type=date.fromisoformat, default=today + timedelta(days=1), help="Exclusive date, Taipei; default tomorrow (includes today)")
    parser.add_argument("--output", type=Path, default=ROOT / "data")
    parser.add_argument("--anonymous", action="store_true", help="Explicit public-feed probe; never reads/sends the key")
    parser.add_argument("--skip-details", action="store_true")
    parser.add_argument("--refresh-details", action="store_true")
    parser.add_argument("--max-pages", type=int, default=500)
    parser.add_argument("--workers", type=int, choices=range(1, 9), default=4, help="Concurrent detail requests (1–8); shared pacing limits request starts to four/second")
    args = parser.parse_args()
    if args.start >= args.end or args.max_pages < 1:
        parser.error("start must precede end and max-pages must be positive")
    key = "" if args.anonymous else read_key(ROOT / ".env")
    if not key and not args.anonymous:
        parser.error("Add HUGGINGNEWS_API_KEY to the project .env, or use --anonymous for a limited probe.")
    report = collect(Client(key), args.start, args.end, args.output,
                     not args.skip_details, args.max_pages, args.refresh_details, args.workers)
    print(f"Saved {report['story_count']} stories to {args.output}")
    print(f"History complete: {report['history_complete']}; details complete: {report['details_complete']}")
    print("See manifest.json for coverage, limitations, and errors.")
    return 0 if report["history_complete"] and report["details_complete"] and not report.get("error") else 2


if __name__ == "__main__":
    sys.exit(main())
