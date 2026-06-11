# Family World Cup 2026 Sweepstake App — Specification

## Purpose
A single web page supporting a family sweepstake for the 2026 FIFA World Cup. It generates ready-to-paste text messages for the family WhatsApp chat.

## Sweepstake data (hard-coded)
- 24 players, each assigned 2 teams (48 teams total — the full 2026 field).
- Assignments are fixed for the whole tournament and hard-coded into the app.
- Status: **AWAITING DATA** — player names + team assignments to be provided.
- Each team must be validated as a confirmed 2026 World Cup participant before hard-coding.

## UI
Two buttons:
1. **"Yesterday's results"** — generates WhatsApp text listing each match played yesterday with:
   - Both teams with their flag emojis
   - Final score
   - The sweepstake player assigned to each team
2. **"Today's matches"** — generates WhatsApp text listing each match scheduled today with:
   - Both teams with their flag emojis
   - The sweepstake player assigned to each team
   - Kick-off time converted to **BST (UK time)**

Generated text shown in a copyable text area (plus a one-tap Copy button).

## Match data source — DECIDED (v0.2)
- **Primary:** openfootball/worldcup.json (public-domain GitHub dataset, no API key)
  - URL: `https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json`
  - Verified working 2026-06-11: contains all 104 fixtures with date, kick-off time + UTC offset, teams, group, venue. Scores are added to each match as `"score": {"ft": [a, b]}` as the tournament progresses.
  - CORS-friendly (raw.githubusercontent.com allows browser fetch), so the web page fetches it live on each button press.
  - Known limitation: community-maintained, so results may lag a few hours after full time. Acceptable for a next-morning "yesterday's results" message.
- Alternatives considered: API-Football / football-data.org / Sportmonks (need API keys, rate limits, or paid tiers — rejected for a simple family page); rezarahiminia/worldcup2026 REST API (unproven uptime — kept as fallback).
- Knockout-stage placeholders (e.g. "1A", "W73") appear in fixtures until teams are known; the app shows them as-is with no player attribution until resolved.

## Validated 2026 participants (48, extracted from data source)
Algeria, Argentina, Australia, Austria, Belgium, Bosnia & Herzegovina, Brazil, Canada, Cape Verde, Colombia, Croatia, Curaçao, Czech Republic, DR Congo, Ecuador, Egypt, England, France, Germany, Ghana, Haiti, Iran, Iraq, Ivory Coast, Japan, Jordan, Mexico, Morocco, Netherlands, New Zealand, Norway, Panama, Paraguay, Portugal, Qatar, Saudi Arabia, Scotland, Senegal, South Africa, South Korea, Spain, Sweden, Switzerland, Tunisia, Turkey, USA, Uruguay, Uzbekistan.
Player team assignments must use these exact names (the app will map them to flag emojis).

## Technical
- Single self-contained HTML/JS page (artifact).
- "Yesterday" and "today" computed in UK time (BST during the tournament).

## Change log
- v0.1 — Initial spec from project goals. Awaiting player/team data and match-data-source decision.
- v0.2 — Researched data sources; selected openfootball/worldcup.json (verified live). Documented the 48 validated participants. Still awaiting the 24 player/team assignments.

## Sweepstake draw — HARD-CODED (v0.3)
24 players × 2 teams, exactly covering all 48 participants (verified: no duplicates, no team unassigned). Five names normalised from the supplied list to match the data source exactly: Bosnia & Herzegovia→Bosnia & Herzegovina, Columbia→Colombia, The Netherlands→Netherlands, Curacao→Curaçao, DRC→DR Congo.

Ali: Iran, Japan · Carlotta: Cape Verde, South Africa · Dan: Bosnia & Herzegovina, Argentina · Elliot: Algeria, France · Euan: Australia, Colombia · George: Netherlands, Ecuador · Hannah: Jordan, Germany · Jack: Curaçao, Saudi Arabia · Jan: Belgium, Spain · Joseph: Tunisia, Sweden · Josh: Uruguay, Iraq · Jonathan: Ivory Coast, Switzerland · Jenny: Croatia, Egypt · Kate: USA, Qatar · Katie: Paraguay, Morocco · Laura: Uzbekistan, Czech Republic · Lou: Mexico, Brazil · Matt: Ghana, Haiti · Mike: New Zealand, Scotland · Nick: England, South Korea · Patrick: Norway, Senegal · Paul: Portugal, Turkey · Sophie: Panama, Austria · Vic: Canada, DR Congo

## Day-grouping rule (v0.3 decision)
"Today" and "yesterday" are defined by the **kick-off moment in UK time**, not the stadium-local date. Late North American kick-offs (e.g. 20:00 in Mexico = 3:00am BST next day) therefore appear on the UK day the family actually watches them. Verified against real fixtures.

## Message formats (v0.3)
Results message:
  ⚽ WORLD CUP 2026 — RESULTS / <weekday day month> / blank line /
  per match: "🇲🇽 Mexico 2–1 🇿🇦 South Africa" + "(Lou v Carlotta)".
  Handles aet and penalty shoot-outs; "result not posted yet" if score missing;
  "(both X!)" if one player owns both teams; player note omitted for knockout placeholders.
Fixtures message:
  ⚽ WORLD CUP 2026 — TODAY'S MATCHES / <weekday day month> (all times UK) /
  per match: "8:00pm BST — 🇲🇽 Mexico v 🇿🇦 South Africa" + "(Lou v Carlotta)", sorted by kick-off.

## Implementation (v0.3)
- Single self-contained page: sweepstake.html (no build step, no API key).
- Fetches the openfootball JSON fresh on every button press (cache:no-store).
- Output rendered as a WhatsApp-style bubble with a one-tap Copy button (clipboard API + fallback).
- Collapsible roster table showing the full draw with flags.
- Graceful errors: fetch failure message; "No matches today/yesterday" messages.
- Tested: time parsing for all UTC offsets in dataset; UK-date grouping incl. midnight crossover.

## Change log (cont.)
- v0.3 — Hard-coded validated draw (5 spellings normalised). Built sweepstake.html. Defined UK-time day-grouping rule and message formats. Logic tested against live data.

## Deployment (v0.4)
- The page must run in a normal browser. Claude's artifact preview sandbox blocks external fetches, so "Couldn't fetch data" appears there — this is a sandbox restriction, not an app bug (data source CORS verified: access-control-allow-origin: *).
- Recommended: host the single file on Netlify Drop or GitHub Pages and bookmark it / add to home screen. Opening the downloaded file directly in Safari/Chrome also works.

## Change log (cont.)
- v0.4 — Diagnosed preview-sandbox fetch failure; documented deployment route.

## Architecture rework (v0.5) — works inside Claude's sandbox
Direct fetch failed in the user's environment, so the app no longer depends on it:
1. **Fixtures hard-coded.** All 104 matches (date, kick-off, teams; snapshot 2026-06-11) are embedded in the page. "Today's matches" needs no network at all.
2. **Scores via layered fallback.** "Yesterday's results" first tries the openfootball JSON directly (works in normal browsers, 6s timeout); if blocked, it asks the Anthropic API (claude-sonnet-4 + web search — allowed inside the artifact sandbox) for the missing scores, requesting strict JSON keyed to the exact team names. Unconfirmed matches say "result not confirmed yet" rather than guessing.
3. Knockout fixtures embedded as placeholders (1A, W73…); they resolve automatically when live fetch works, and the web-search path covers scores either way.

Tested: embedded data integrity (104 matches, all 48 teams flagged + assigned), today's fixture message, missing-score flow with graceful degradation.

## Change log (cont.)
- v0.5 — Embedded full fixture schedule; added Claude-API web-search score lookup as sandbox-safe fallback. App now works as a Claude artifact, a local file, or hosted.

## Leaderboard (v0.6)
Third button: **"Leaderboard"** — WhatsApp-ready standings across all 24 players.
- Each player's row aggregates BOTH their teams: P, W, D, L, goal difference, points (W=3, D=1).
- Sort: points → goal difference → goals for → name. Tied players share a position; top three get 🥇🥈🥉.
- A match counts once kick-off + 2h45 has passed and both teams are known (placeholders excluded until resolved).
- Score gathering: embedded/live scores first, then Claude web-search lookups in batches of 12 for anything missing. Confirmed scores are cached in artifact persistent storage (window.storage, feature-detected — silently skipped when hosted outside Claude) so the leaderboard doesn't re-search the whole tournament every press.
- Finished matches without confirmed scores are excluded from the table and flagged in a footnote.
- W/D/L is taken from the recorded final score (knockout penalty handling to be refined once those rounds approach).

## Change log (cont.)
- v0.6 — Added Leaderboard button with per-player standings, batched score lookup, and persistent score cache. Aggregation logic tested with simulated results.

## UK TV channels (v0.7)
- Investigated the data source: match objects contain only round, date, time, teams, group, venue (+ match number for knockouts). No broadcaster data exists in it.
- UK coverage facts: every match is free-to-air, split between BBC (54 games) and ITV (51), final simulcast; assignments announced progressively with some knockout picks TBD.
- Implementation: "Today's matches" now looks up each match's UK channel via the Claude web-search route (same mechanism as scores), shown as "📺 ITV1" on the fixture line. Channels are cached per match in persistent storage so each is only ever searched once; unconfirmed channels are omitted rather than guessed. Lookup failure never blocks the message.
- Cache keys: "wc26-scores" (results), "wc26-tv" (channels). Cache helpers generalised to take a key.

## Change log (cont.)
- v0.7 — Documented available JSON fields. Added UK TV channel lookup with per-match caching to the fixtures message. Tested success and failure paths.

## Venues + TV diagnostics (v0.8)
- Embedded data regenerated to include each match's host city (and refreshed from source — no scores posted yet as of the opener). Live-fetch path also carries venue.
- Fixture line format now: "8:00pm BST — 🇲🇽 Mexico v 🇿🇦 South Africa 📺 ITV1" / "(Lou v Carlotta) · 📍 Mexico City". Stadium suffixes in parentheses are trimmed for WhatsApp brevity (e.g. "Los Angeles (Inglewood)" → "Los Angeles").
- TV channel lookup failures are no longer silent: the status line reports the error, with a specific hint when the failure pattern indicates the page is running outside Claude's artifact environment (the Anthropic API route only works there).

## Change log (cont.)
- v0.8 — Added host city to fixtures. Surfaced TV-lookup errors with environment hint. Tested both paths.

## API call hardening (v0.9)
- Refactored the two Claude lookups (scores, TV channels) into one shared askClaude() helper.
- Added the standard "anthropic-version: 2023-06-01" header (previously missing — prime suspect for the "invalid response format" failure seen in the Claude app).
- Full diagnostic error chain: network failures, non-2xx HTTP (with body snippet), API error bodies, non-JSON replies, and missing/bad JSON in the model's text are each reported distinctly in the status line (truncated to 220 chars).
- Parser tolerates tool-use/search-result content blocks and markdown fences. All failure modes unit-tested.

## Change log (cont.)
- v0.9 — Shared API helper, anthropic-version header, detailed error surfacing.

## Runtime compatibility probe (v0.10)
- "network: Invalid response format" indicated the Claude app's fetch proxy rejected the request before any response — not an API error. Reverted the request to the exact documented artifact shape (Content-Type header only; the anthropic-version header added in v0.9 was a likely trigger).
- askClaude() now degrades stepwise: (1) documented shape WITH web search; (2) on proxy/4xx rejection, retry WITHOUT web search (answers limited to model knowledge, instructed to return null rather than guess); (3) if both fail, status reports both errors side by side.
- Status line states when the limited no-search mode was used so missing channels/scores are explainable. All three paths unit-tested.

## Change log (cont.)
- v0.10 — Reverted to documented API request shape; added tools→no-tools fallback with mode reporting.

## Embedded TV schedule (v0.11)
- Confirmed root cause: the Claude *mobile app* artifact sandbox blocks ALL network requests — GitHub and the Anthropic API alike. Web-based lookups can never run there.
- Solution: embedded the announced UK broadcaster for all 72 group-stage matches (sourced from the published UK TV guide, updated 8 Jun 2026), keyed by team pair, order-insensitive. Specific channels where announced (ITV1, BBC One), network otherwise (BBC/ITV).
- Channel resolution order: embedded schedule → cached lookups → Claude web search (knockouts, on capable runtimes). Knockout broadcasters are TBC until the bracket forms.
- "Today's matches" is now 100% offline for the whole group stage: fixtures, kick-offs, venues, players, AND channels.
- Remaining mobile-app limitation (by design of the sandbox): scores cannot update on mobile. Working options: run the artifact on claude.ai in a browser (web-search route works), host the file on the web (direct openfootball fetch works), or return to this project for a refreshed embedded-score snapshot.

## Change log (cont.)
- v0.11 — Embedded 72 announced group-stage UK channels; offline-first channel resolution; documented mobile-app network reality.

## Deployment — LIVE (v1.0)
- Hosted on GitHub Pages: https://paulshep.github.io/worldcup2026/ (repo paulshep/worldcup2026, public, deploy-from-branch main:/, build verified 11 Jun 2026).
- index.html (the app) and SPEC.md are both in the repo.
- In the hosted environment: fixtures/venues/channels work from embedded data; scores fetch live from openfootball directly (no Claude needed for the group stage).
- Update routes: push a new index.html via a fresh short-lived PAT, edit via GitHub's web editor, or regenerate here.
- Pending future work: embed knockout TV channels when announced (~late June); decide penalty-shootout W/D/L rule before Round of 32 (28 June).

## Change log (cont.)
- v1.0 — Published to GitHub Pages; deployment verified via API.

## Knockout result rules — DECIDED (v1.1)
- User ruling: **a win on penalties is a win.** Leaderboard W/D/L: higher score after 90/120 mins wins; if level and a shootout occurred, the shootout winner takes the W and the loser the L (no points for the 120-min draw beyond the 3 for the W; goal difference uses goals only, never pens).
- Score storage format extended: [a,b] = 90-min result; [a,b,"aet"] = decided in extra time; [a,b,pa,pb] = pens. Backwards-compatible with cached 2-element scores.
- Results message renders " aet" and " (4–3 pens)" suffixes. Embedded data generator, live-fetch normaliser, and the Claude score-lookup prompt all carry extra-time and shootout detail.
- Tested: pens W/L attribution, aet display, GD unaffected by shootouts.

## Change log (cont.)
- v1.1 — Penalty-shootout and extra-time handling throughout, per user ruling.

## Tomorrow's matches (v1.2)
Fourth button: **"Tomorrow's matches"** — identical format to today's fixtures (kick-off BST, flags, 📺 channel, players, 📍 city) for the next UK day, headed "TOMORROW'S MATCHES". Fixture builder label parameterised; rest days say "No matches tomorrow".

## Change log (cont.)
- v1.2 — Added Tomorrow's matches button; published.

## Commentary (v1.3)
Fifth button: **"Commentary"** — a WhatsApp message in the voice of a traditional British football commentator covering (1) yesterday's results with dramatic colour crediting team owners, (2) the state of the sweepstake table (leader, biggest overnight climber, sympathy for the bottom), and (3) tongue-in-cheek predictions for today's fixtures.
- Two-tier generation: where the Anthropic API is reachable (claude.ai artifact), Claude writes bespoke commentary from a structured data payload (results, top 5, fixtures; <200 words). Everywhere else (the GitHub Pages site, mobile app), a built-in phrase-bank engine assembles commentary locally — randomised cliché selection varies the output day to day; tone scales with margin of victory (odd-goal thriller → demolition), shootouts get maximum drama.
- Standings logic refactored into tallyTable()/computeRows(), shared by leaderboard and commentary (which diffs the table before/after yesterday to find movers). Leaderboard regression-tested.

## Change log (cont.)
- v1.3 — Commentary button: Claude-written where possible, local cliché engine everywhere; published.
