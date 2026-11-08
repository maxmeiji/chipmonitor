# HuggingNews historical database import

## Files and scope

- `raw_ai_market_huggingnews_story.csv`: 1,587 full historical stories from the saved aggregate, not the dashboard candidate subset.
- `raw_ai_market_huggingnews_story_key_source.csv`: 5,880 selected key-source entries. This is not every tweet counted by tweet_count.

Saved publication range, converted to Asia/Taipei: 2026-08-30 16:37:30 through 2026-11-08 00:22:48. Requested June/July history was not returned by the API. No completeness beyond the available snapshot is claimed.

## Audit columns

Both `create_user` and `update_user` are `huggingnews_import` on every row. Both audit datetimes are `2026-11-08 16:52:10` (Asia/Taipei), the export timestamp. These are not the story publication timestamps. The timezone column is `Asia/Taipei` throughout.

All original publication, event and tweet times have been converted from their timezone-aware values to UTC+8 and formatted `YYYY-MM-DD HH:MM:SS`. Fractional seconds are dropped because the supplied schema uses plain DATETIME.

## IDs, scores and missing fields

Official `storyId` values and importance scores were retrieved from the embedded data on the corresponding official HuggingNews story pages or a source-linked story record on another official page. No slug hashes, short slug suffixes or synthetic IDs were used. Metadata extraction parsed JavaScript syntax as data without executing page code. Scores are rounded to DECIMAL(10,6), half up. Other story/tweet content comes from the saved API snapshot rather than being silently refreshed.

`is_tldr` was absent from the available API and official metadata. As explicitly requested, it is **0 as an import placeholder** and every story remark says the historical TLDR status is unknown. It must not be interpreted as verified non-membership. `isFreshStory` was not substituted. `is_superseded` preserves the explicit value in the saved API snapshot; it is not inferred from UPDATE or supersedes.

Lineage maps `supersedes.slug` to `supersedes_story_id` and `continuesFrom.slug` to `previous_story_id`, using official IDs. There are 531 distinct predecessor IDs referenced outside this exported full-story set. They may already exist in your database. If your database enforces self-referential foreign keys, load those missing historical parent records first or import through a staging table. Do not manufacture parent rows or silently discard lineage. 0 lineage links could not be resolved; any such links have their target slug retained in remark.

The source table's AUTO_INCREMENT `id` is deliberately **omitted** from the source CSV; let the database assign it. All source story_id values exist in the story CSV. Tweet IDs remain exact strings, without spreadsheet rounding. Roles use Source, Support, Commentary, Analysis, Signal and Engagement. `best_bit` preserves the provider field; it is not replaced by a generated summary. When it is not a literal substring of returned text, the source remark records that fact without changing it. Full tweet text has no destination column in the supplied schema and is not inserted into best_bit.

## CSV settings

- Encoding: UTF-8, no BOM. Use a Unicode-capable database character set such as utf8mb4 for emoji and multilingual text.
- Delimiter: comma. Enclosure: double quote. Embedded quotes are doubled (RFC 4180).
- Records use CRLF. Summaries/best bits may contain quoted embedded newlines: use a real CSV importer, not line splitting.
- First row contains column names. Import by those header names, rather than physical database column order.
- SQL NULL marker: literal `\N`. Configure your importer to translate that marker to SQL NULL; do not store it as the two-character string or convert it to an empty numeric/date value.
- Import stories first, then key sources. Check pre-existing IDs and use your intended insert/upsert policy; these files do not delete or overwrite database rows on their own.

The optional SQL below maps the null marker explicitly. Review file paths and database permissions before running. It is provided only as a reference; no database import was executed.

```sql
LOAD DATA LOCAL INFILE '/absolute/path/raw_ai_market_huggingnews_story.csv'
INTO TABLE raw_ai_market_huggingnews_story
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"'
LINES TERMINATED BY 0x0d0a
IGNORE 1 LINES
(@story_id, @slug, @story_url, @title, @summary, @published_at, @event_time_approx, @tweet_count, @author_count, @story_score, @tickers, @is_tldr, @is_superseded, @supersedes_story_id, @previous_story_id, @remark, @update_user, @update_datetime, @create_user, @create_datetime, @timezone)
SET
  story_id = NULLIF(@story_id, CHAR(92,78)),
  slug = NULLIF(@slug, CHAR(92,78)),
  story_url = NULLIF(@story_url, CHAR(92,78)),
  title = NULLIF(@title, CHAR(92,78)),
  summary = NULLIF(@summary, CHAR(92,78)),
  published_at = NULLIF(@published_at, CHAR(92,78)),
  event_time_approx = NULLIF(@event_time_approx, CHAR(92,78)),
  tweet_count = NULLIF(@tweet_count, CHAR(92,78)),
  author_count = NULLIF(@author_count, CHAR(92,78)),
  story_score = NULLIF(@story_score, CHAR(92,78)),
  tickers = NULLIF(@tickers, CHAR(92,78)),
  is_tldr = NULLIF(@is_tldr, CHAR(92,78)),
  is_superseded = NULLIF(@is_superseded, CHAR(92,78)),
  supersedes_story_id = NULLIF(@supersedes_story_id, CHAR(92,78)),
  previous_story_id = NULLIF(@previous_story_id, CHAR(92,78)),
  remark = NULLIF(@remark, CHAR(92,78)),
  update_user = NULLIF(@update_user, CHAR(92,78)),
  update_datetime = NULLIF(@update_datetime, CHAR(92,78)),
  create_user = NULLIF(@create_user, CHAR(92,78)),
  create_datetime = NULLIF(@create_datetime, CHAR(92,78)),
  timezone = NULLIF(@timezone, CHAR(92,78));
```

```sql
LOAD DATA LOCAL INFILE '/absolute/path/raw_ai_market_huggingnews_story_key_source.csv'
INTO TABLE raw_ai_market_huggingnews_story_key_source
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"'
LINES TERMINATED BY 0x0d0a
IGNORE 1 LINES
(@story_id, @tweet_id, @role, @author_handle, @tweet_url, @tweeted_at, @best_bit, @remark, @update_user, @update_datetime, @create_user, @create_datetime, @timezone)
SET
  story_id = NULLIF(@story_id, CHAR(92,78)),
  tweet_id = NULLIF(@tweet_id, CHAR(92,78)),
  role = NULLIF(@role, CHAR(92,78)),
  author_handle = NULLIF(@author_handle, CHAR(92,78)),
  tweet_url = NULLIF(@tweet_url, CHAR(92,78)),
  tweeted_at = NULLIF(@tweeted_at, CHAR(92,78)),
  best_bit = NULLIF(@best_bit, CHAR(92,78)),
  remark = NULLIF(@remark, CHAR(92,78)),
  update_user = NULLIF(@update_user, CHAR(92,78)),
  update_datetime = NULLIF(@update_datetime, CHAR(92,78)),
  create_user = NULLIF(@create_user, CHAR(92,78)),
  create_datetime = NULLIF(@create_datetime, CHAR(92,78)),
  timezone = NULLIF(@timezone, CHAR(92,78));
```

## Validation

Exact CSV round-trip, header order, row counts, ID uniqueness, source-to-story references, field lengths, ticker JSON, audit-user values and timestamp syntax are checked. See `validation.json` for counts and checksums. Source claims remain unverified news.
