---
name: huggingnews
description: Search and read HuggingNews's public, source-linked AI news feed. Use for the latest AI news, recent developments about an AI company, lab, model, product, person, or topic, detailed story summaries and sources, the 24-hour TLDR brief, trending AI names, or monitoring the recent AI news cycle.
version: 0.0.5
---

# HuggingNews

Use the read-only JSON API anonymously. If `HUGGINGNEWS_API_KEY` is available, add
`-H "Authorization: Bearer $HUGGINGNEWS_API_KEY"` to every feed and search request for the paginated
feed and wider search.

Base endpoint: `https://api.huggingnews.com/api/stories`

## Retrieve stories

Fetch the latest AI news:

```bash
curl -fsS "https://api.huggingnews.com/api/stories"
```

Each day group holds every story published that Eastern Time day, ordered by importance, not time.
For the latest stories in publishing order, flatten the day groups and sort by `publishedAt`:

```bash
curl -fsS "https://api.huggingnews.com/api/stories" |
  jq '[.dayGroups[].stories[]] | sort_by(.publishedAt) | reverse'
```

Search results are cut at `limit` by importance within each day, so sorting them by `publishedAt`
only reorders the returned matches.

Search the recent feed:

```bash
curl -fsS --get "https://api.huggingnews.com/api/stories" \
  --data-urlencode "query=OpenAI agents" \
  --data-urlencode "limit=10"
```

Retrieve the next authenticated feed page using the returned cursor:

```bash
curl -fsS -H "Authorization: Bearer $HUGGINGNEWS_API_KEY" --get \
  "https://api.huggingnews.com/api/stories" \
  --data-urlencode "beforeDayKey=<nextBeforeDayKey>"
```

Filter latest or search results by fine-grained topic tags:

```bash
curl -fsS --get "https://api.huggingnews.com/api/stories" \
  --data-urlencode "tags=ai-model-releases,ai-products"
```

Comma-separated tags match any supplied tag. Parent tags also match stories assigned to their
descendants.

Available AI topic slugs:

- `ai-fundraising` — AI funding
- `ai-modeling` — AI models
  - `ai-model-releases` — model releases and capability updates
  - `ai-open-models` — open-weight and open-source models
  - `ai-research-evals` — research, benchmarks, and evaluations
- `ai-products` — AI products
  - `ai-agents-coding` — agents and coding tools
  - `ai-enterprise-tools` — enterprise AI tools
  - `ai-generative-media` — image, video, audio, and other generative media
- `ai-infrastructure` — AI infrastructure
  - `ai-compute-chips` — chips, data centers, power, and compute
  - `ai-inference-platforms` — inference, serving, deployment, and optimization
- `ai-governance` — AI regulation and governance
  - `ai-policy-regulation` — laws, rules, standards, and government oversight
  - `ai-legal-safety` — lawsuits, copyright, safety, misuse, and security risk
- `ai-sector-impact` — AI adoption, company strategy, labor, and industry impact

The root slug `ai` is valid but redundant because latest and search results already contain only AI
stories. Slugs returned in `topicTags[].slug` can also be used for cross-cutting filters.
`limit` is valid only with `query` and must be an integer from 1 through 50.

Fetch one selected story by its exact slug:

```bash
curl -fsS "https://api.huggingnews.com/api/stories/<slug>"
```

Fetch every tweet behind a story, newest first, 100 per page:

```bash
curl -fsS "https://api.huggingnews.com/api/stories/<slug>/tweets"
```

Page further with an API key (`offset` is an integer from 0; `limit` is an integer from 1 through
100, default 100):

```bash
curl -fsS -H "Authorization: Bearer $HUGGINGNEWS_API_KEY" --get \
  "https://api.huggingnews.com/api/stories/<slug>/tweets" \
  --data-urlencode "offset=100"
```

Fetch a story's lineage — earlier versions and follow-up developments — oldest to newest:

```bash
curl -fsS "https://api.huggingnews.com/api/stories/<slug>/chain"
```

## Retrieve the TLDR and trending entities

Fetch the TLDR, the site's ranked brief of the last 24 hours of AI news:

```bash
curl -fsS "https://api.huggingnews.com/api/tldr"
```

Fetch trending entities, the names whose mentions are rising in recent AI tweets:

```bash
curl -fsS "https://api.huggingnews.com/api/trending"
```

## Read responses

- Latest responses contain `dayGroups[]` objects with `dayKey` and `stories[]`, `hasMore`, and an
  optional `nextBeforeDayKey`. Each story contains `slug`, `title`, `publishedAt`,
  `eventTimeApprox`, `isFreshStory`, `tweetCount`, `authorCount`, `routingTopicKeys[]`,
  `primaryRoutingTopic`, and `topicTags[]` entries with `slug` and `name`; `lastUpdatedAt` may also
  be present at the top level. `tweetCount` and `authorCount` count the tweets and distinct authors
  behind the story. `isFreshStory` is true for an original story (not an update or a later version)
  whose event happened in the last 12 hours; the site labels these NEW. `primaryRoutingTopic` is the
  story's main routing topic, which is not always `ai`. When present, `tickers[]` lists tagged
  companies with `ticker`, `name`, `kind` (`equity` or `private`), `role` (`subject` or `related`),
  and `hubKey`. When present, `image` is the story's selected picture with `url` (large),
  `thumbnailUrl` (small), `mediaType` (`photo`, `video`, or `animated_gif`), `videoUrl` for playable
  clips, and `credit` with the source `handle` and `tweetUrl`. Follow `nextBeforeDayKey` while
  authenticated when `hasMore` is true.
- Search responses contain `query`, the same story objects in the top-level `stories[]`, and
  `truncated`; `lastUpdatedAt` may also be present. Check `truncated` before treating the result set
  as exhaustive.
- Story detail is a flat object containing the same story fields plus `summary`,
  `selectedTweets`, and `isSuperseded`. Selected-tweet entries contain `tweetId` and `role` and
  may contain `authorHandle`, `url`, `tweetedAt`, `bestBit`, `text`, and `quotedTweetText`.
  `bestBit` is the span of the tweet the writer picked as its strongest support for the story;
  quote it instead of the full `text` when you need one line per source. When present,
  `continuesFrom` references the earlier story this one is a new development of, and `supersedes`
  references the earlier version this story replaced; both are story references with `slug`,
  `title`, `publishedAt`, `eventTimeApprox`, `routingTopicKeys[]`, `tweetCount`, and `authorCount`.
- Tweets responses contain `total` (every tweet behind the story), `sourceCount` (distinct
  authors), `truncated` (more tweets beyond this page), and `tweets[]` entries with `tweetId`,
  `authorHandle`, `url`, `tweetedAt`, `text`, `media[]`, and optionally `authorDisplayName`,
  `quotedTweetText`, and `role`. Media entries carry `type`, `url`, and optionally `previewUrl`,
  `width`, and `height`. `role` appears only on the story's key-source tweets and is one of
  `source`, `support`, `engagement`, `signal`, `commentary`, or `analysis`. Anonymous requests get
  the first page only; `offset` greater than 0 requires an API key.
- Chain responses contain `truncated` and `stories[]` ordered oldest to newest: story references
  plus `isSuperseded` and, when present, `continuesFromSlug` and `supersedesSlug` pointing at
  earlier members. Superseded members are hidden from the feed; link the newest non-superseded
  member.
- TLDR responses contain `windowStart` and `windowEnd` (the 24 hours the brief covers),
  `materializedAt`, `bullets[]` in rank order, and `otherNews`. Each bullet contains `text`,
  `storySlug`, and `routingTopicKeys[]`. Fetch `/api/stories/<storySlug>` for the full story.
  `otherNews` holds the same run's top MarketBrief stories outside AI as `bullets[]` in the same
  format, or is null until they are ready.
- Trending responses contain up to 12 `entities[]` in rank order. Each entity contains
  `entityText`, `storyCount`, `storySlugs[]` (the stories that mention it), and `hubKey` when the
  entity has a hub page.
- TLDR and trending return 404 until their first snapshot is published.
- Anonymous latest and search cover the current and preceding two Eastern Time calendar dates.
  Authenticated feed requests can paginate older stories, and authenticated search covers the
  latest 21 Eastern Time calendar dates. An exact known slug can resolve any public story.
- `publishedAt`, `lastUpdatedAt`, `tweetedAt`, `windowStart`, `windowEnd`, and `materializedAt` are
  ISO 8601 UTC timestamps, the same format as `eventTimeApprox`. `dayKey` is an Eastern Time date.
- Prefer `eventTimeApprox` when describing when the reported event occurred.

## Answer with sources

Retrieve the detail object before answering about a specific story. Base factual summaries on
`summary` and the available content in `selectedTweets`.

For every reported story, including in news roundups, copy its complete `title` and `summary` exactly
as returned by the API without changing any word unless the user explicitly asks for a new summary,
paraphrase, or rewrite. Quote TLDR bullets the same way: copy `text` exactly as returned.

Link the HuggingNews story as `https://huggingnews.com/ai/<slug>`; TLDR bullets carry the slug in
`storySlug`. `otherNews` bullets are MarketBrief stories: link them as
`https://marketbrief.now/<topic>/<storySlug>`, where `<topic>` is their first `routingTopicKeys`
value, or `other-news` when the list is empty. Link a trending entity with a `hubKey` as
`https://huggingnews.com/entity/<hubKey>`. Also link relevant `selectedTweets[].url` values when
they directly support the answer.

If search returns no stories, say that no match was found in the recent feed; do not claim that the
event did not happen.
