from datetime import date
import json
from pathlib import Path
import tempfile
import unittest

from fetch_news import collect, months_before


def story(slug, published):
    return {"slug": slug, "publishedAt": published, "title": slug}


class FakeClient:
    def __init__(self, pages, key="test-key"):
        self.key, self.pages, self.calls = key, iter(pages), []

    def get(self, suffix="", params=None):
        self.calls.append((suffix, params))
        if suffix:
            return {"slug": suffix[1:], "summary": "source summary", "selectedTweets": []}
        return next(self.pages)


class FetchTests(unittest.TestCase):
    def test_pagination_deduplication_and_taipei_boundary(self):
        latest = story("latest", "2026-11-07T10:00:00Z")
        client = FakeClient([
            {"dayGroups": [{"dayKey": "2026-11-07", "stories": [latest]}],
             "hasMore": True, "nextBeforeDayKey": "2026-11-07"},
            {"dayGroups": [{"dayKey": "2026-09-07", "stories": [latest,
                story("boundary", "2026-09-07T16:00:00Z"),
                story("too-old", "2026-09-07T15:59:59Z")]}], "hasMore": True}])
        with tempfile.TemporaryDirectory() as temp:
            result = collect(client, date(2026, 9, 8), date(2026, 11, 9), Path(temp))
            self.assertTrue(result["history_complete"])
            self.assertTrue(result["details_complete"])
            self.assertEqual(result["story_count"], 2)
            self.assertEqual(client.calls[1][1], {"beforeDayKey": "2026-11-07"})
            self.assertEqual(len(json.loads((Path(temp) / "stories.json").read_text())), 2)

    def test_anonymous_exhaustion_is_incomplete(self):
        client = FakeClient([{"dayGroups": [], "hasMore": False}], key="")
        with tempfile.TemporaryDirectory() as temp:
            result = collect(client, date(2026, 9, 8), date(2026, 11, 9), Path(temp))
            self.assertFalse(result["history_complete"])
            self.assertTrue(result["limitations"])

    def test_repeated_cursor_saves_partial_data_and_error(self):
        page = {"dayGroups": [{"dayKey": "2026-11-07", "stories": []}],
                "hasMore": True, "nextBeforeDayKey": "same"}
        with tempfile.TemporaryDirectory() as temp:
            result = collect(FakeClient([page, page]), date(2026, 9, 8), date(2026, 11, 9), Path(temp))
            self.assertFalse(result["history_complete"])
            self.assertIn("repeated", result["error"])
            self.assertTrue((Path(temp) / "manifest.json").exists())

    def test_calendar_months(self):
        self.assertEqual(months_before(date(2026, 4, 30)), date(2026, 2, 28))

    def test_cached_details_are_reused_without_network_requests(self):
        page = {"dayGroups": [{"dayKey": "2026-09-07", "stories": [
            story("cached", "2026-09-08T08:00:00Z")]}], "hasMore": False}
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            (out / "details").mkdir()
            (out / "details/cached.json").write_text(json.dumps(
                {"slug": "cached", "summary": "preserved summary", "selectedTweets": []}))
            client = FakeClient([page])
            result = collect(client, date(2026, 9, 8), date(2026, 11, 9), out)
            self.assertTrue(result["details_complete"])
            self.assertEqual(len(client.calls), 1)
            self.assertEqual(json.loads((out / "stories.json").read_text())[0]["summary"], "preserved summary")

    def test_detail_failure_preserves_feed_and_marks_incomplete(self):
        class FailedDetailClient(FakeClient):
            def get(self, suffix="", params=None):
                if suffix:
                    raise RuntimeError("HuggingNews HTTP 503")
                return super().get(suffix, params)

        page = {"dayGroups": [{"dayKey": "2026-09-07", "stories": [
            story("failed", "2026-09-08T08:00:00Z")]}], "hasMore": False}
        with tempfile.TemporaryDirectory() as temp:
            result = collect(FailedDetailClient([page]), date(2026, 9, 8), date(2026, 11, 9), Path(temp))
            self.assertTrue(result["history_complete"])
            self.assertFalse(result["details_complete"])
            self.assertEqual(result["story_count"], 1)
            self.assertEqual(result["detail_failures"][0]["slug"], "failed")


if __name__ == "__main__":
    unittest.main()
