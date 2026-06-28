# Family World Cup 2026 Sweepstake App — Specification

> **Note:** The authoritative description of how the system works *today* is the
> "CURRENT STATE" section immediately below. Everything after it is a chronological
> change log (v0.1 → v2.8) kept as history — some early sections describe designs that
> were later superseded (e.g. the original live-fetch leaderboard, replaced by a static
> one; early single-source data, replaced by the three-source merge).

---

# CURRENT STATE (v2.8) — authoritative

## What it is
A family sweepstake companion for the 2026 FIFA World Cup. 24 players each own 2 teams
(48 total = the full field). Three published pages, hosted free on GitHub Pages from repo
**paulshep/worldcup2026**:
- **Message maker** — https://paulshep.github.io/worldcup2026/ (repo `index.html`)
- **Leaderboard** — https://paulshep.github.io/worldcup2026/leaderboard.html (static, auto-rebuilt)
- **Bracket** — https://paulshep.github.io/worldcup2026/bracket.html (knockout tree)

## Message-maker app (index.html) — 6 buttons
Generates copyable WhatsApp text in a chat-bubble UI (green pitch theme). Buttons:
1. **Yesterday's results** — last 24h, with player + flags + score.
2. **Today's matches** — next 24h, kickoff times in BST + UK TV channel (group stage).
3. **Tomorrow's matches** — the following 24h.
4. **Leaderboard** — full standings as text.
5. **Commentary** — a warm, witty round-up (results + table + fixture "duels").
6. **Match data** — feed diagnostics: when scores.json was published, build-job status, and per-match score availability for the last 24h.
- All time-windowed buttons use **rolling 24-hour windows** (not calendar dates), so a
  game-day whose late US kickoffs spill into the early-hours UK next day stays together.
- Pens-win-is-a-win throughout; score format `[a,b]` / `[a,b,"aet"]` / `[a,b,penA,penB]`.

## Commentary engine
Two tiers: a Claude-written path (only when the app runs somewhere it can reach Anthropic's
API, i.e. inside Claude) and a local phrase-bank writer (the fallback the hosted site always
uses). Both: group-stage-correct (no extra-time/penalty language before 28 Jun), accurate
per-fixture owner binding (no three-team conflation), recap of every finished last-24h match
(never silently dropped), correct tournament-vs-roundup game counts, anti-repetition, and a
leaderboard link appended to every message. Scores come from the authoritative scores.json
(see data architecture), so commentary always matches the leaderboard.

## Leaderboard (leaderboard.html) — static, auto-generated
Pre-rendered floodlit-night design (podium + 24-row table, shared positions on ties). Has
**no client-side fetching** — it's rebuilt and committed by the GitHub Action, so it loads
instantly and can't break. Footer shows last-updated time.

## Bracket (bracket.html) — standalone
Full 2026 knockout tree (R32 #73–88, R16 89–96, QF 97–100, SF 101–102, 3rd-place 103, Final
104) from the openfootball slot wiring. Round-tab nav (phone-first). Each tie shows both
teams (or italic placeholder), the sweepstake owner tags, score + winner highlight, venue/
date; auto-resolves W##/L## chains as results land. A "Sweepstake survivors" strip shows
which players still have teams alive (appears once knockouts begin). Currently all
placeholders (group stage). **Not yet cross-linked** to the leaderboard (deferred).

## Data architecture — three-source freshest-wins merge
A GitHub Action (`build_leaderboard_action.py`) runs **every 5 minutes** and:
- Pulls finished results from three feeds and merges them **per match** (union for coverage):
  **football-data.org** (authoritative primary, key from the `FOOTBALL_API_KEY` Actions
  secret) > **worldcup26.ir** (keyless real-time, currently flaky) > **openfootball**
  (keyless, lags). On overlap the more authoritative source wins, so the rebuild self-corrects.
  Only FINISHED/AWARDED scores accepted; pens parsed.
- Writes **leaderboard.html** (static), **scores.json** (canonical-team-keyed score map, the
  bridge the client reads), and **build-status.json** (per-source diagnostics incl.
  football-data.org's newest `lastUpdated`).
- Anti-regression guard: never blanks a populated page if all sources come back empty.
- The message-maker app reads **scores.json** (same-origin, keyless) as its authoritative
  score source — so it can't expose the football-data.org key, and stays in sync with the
  leaderboard. Max result lag ≈ 5 min (the rebuild cadence).

## Limits / why these choices
- football-data.org free: 10 req/min, **no daily cap**; we use 1 call/run. Its backend
  refreshes ~5-min, matching our cadence. API-Football was rejected (free tier blocks the
  2026 season). worldcup26.ir is real-time but hobby-hosted (has gone down). openfootball is
  reliable but ~daily-lagging — fine as a fallback.
- GitHub Actions: 5-minute cron floor (we're at it); free/unlimited minutes on public repos;
  "commit only if changed" means frequent runs add no repo noise.

## Security (hard rule)
**No secrets in the repo or any published file, ever.** The football-data.org key lives only
in the `FOOTBALL_API_KEY` Actions secret (added by the user directly). The Action commits via
GitHub's built-in token. Every push in this project was secret-scanned before committing.

## Deferred / future
- Cross-link leaderboard ↔ bracket (planned for later in the tournament).
- Knockout-stage UK TV channels (announced ~28 Jun) to embed then.
- Optionally fold the bracket into the Action as static (only worth it near the knockouts).
- If worldcup26.ir stays down, it can be dropped — football-data.org + openfootball suffice.

---

# HISTORY (chronological change log, v0.1 → v2.8)

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

## Commentary predictions rework (v1.4)
- Predictions are now sweepstake duels: each fixture names the two family owners with their current table positions ("Jonathan (4th) locks horns with George (20th)"), then states what a win could do ("an Ivory Coast win rockets Jonathan up to 2nd, while three points lifts George to 7th").
- Hypothetical position uses full tiebreak logic (points, then GD assuming a one-goal win, then GF) so early-tournament climbs read realistically rather than everyone "rocketing to 2nd".
- Special cases: one player owning both teams ("can't lose, can't win, totally zen"), knockout placeholders ("the table holds its breath"). a/an article handling for team names.
- Tone shifted folksier and warmer per user request — relentlessly optimistic coach energy layered over the commentator clichés; randomised kicker lines ("Pressure? Pressure is for tyres.", "Winner gets bragging rights; loser gets character."). Claude-path prompt updated to demand the same duel framing, table stakes, and warm humour.

## Change log (cont.)
- v1.4 — Duel-framed predictions with table stakes; folksy-optimist tone; published.

## Standalone leaderboard page (v1.5)
- New second file leaderboard.html published alongside index.html, for a shareable family link that shows only the standings.
- Distinct visual identity from the message-maker (deliberately not the same green): floodlit-night palette (deep navy + grass undertone), Bebas Neue display / Outfit body / Roboto Mono for stats. Signature element = a three-place podium with the leader raised centre, medal-coloured top edges, each plinth showing the player's two team flags.
- Full 24-row table below: position (shared on ties), player + flags, Played, W·D·L (colour-coded), GD (green/red), Points. Top three highlighted.
- Live + self-updating: fetches scores from openfootball on load, auto-refreshes every 5 minutes, plus a manual Refresh button with an "Updated HH:MM" UK stamp. Falls back to embedded fixtures if the fetch is blocked. Same pens-win-is-a-win and finished-match (KO+2h45) rules as the main app.
- Empty state before the first goal: "No goals yet — the table wakes up the moment the first whistle blows."
- Responsive to narrow phones; reduced-motion respected; design verified via screenshot.
- URL once Pages rebuilds: https://paulshep.github.io/worldcup2026/leaderboard.html

## Change log (cont.)
- v1.5 — Published standalone auto-refreshing leaderboard page with podium design.

## Live score source (v1.6)
- Root cause of "no goals yet": openfootball is updated by hand ~once a day (maintainer's own note), so day-1 results weren't in the feed. Confirmed the real results existed (Mexico 2-0 South Africa; South Korea 2-1 Czech Republic) while the feed still showed none.
- Added a real-time primary source: rezarahiminia / worldcup26.ir (free, no API key, World-Cup-specific live scores). Endpoint GET https://worldcup26.ir/get/games.
- Resolution chain now: live API scores (primary) overlaid onto base fixtures, with openfootball live JSON then the embedded snapshot as fallbacks. If the live API is unreachable or sends no usable scores, the page silently uses the base data — never worse than before.
- Mapping: API keys teams by numeric id; built REZA_TEAMS id→name map for all 48 (normalising Türkiye, Côte d'Ivoire, Czechia, Bosnia and Herzegovina, DR Congo full name, United States to our canonical names). Only the SCORE is taken from the live feed; authoritative kick-off date/time/venue stay from embedded data. Penalty fields consumed if present.
- Applied to BOTH files. Leaderboard footer shows "Updated HH:MM · live" when the live source succeeded. Verified end-to-end in headless browser with the two real day-1 results tallying correctly; no runtime errors.
- Caveat: rezarahiminia is a community/hobby host; reliability and CORS behaviour in real browsers are unproven over a full month, hence the layered fallback. If it proves flaky, the fallbacks keep the pages working.

## Change log (cont.)
- v1.6 — Added rezarahiminia/worldcup26.ir as real-time primary score source (both files), with openfootball + embedded fallback chain.

## Rolling 24-hour windows (v1.7)
- Problem: grouping matches by UK calendar date split a single FIFA gameday across two UK dates, because late US/Mexico kick-offs (e.g. 8pm local) land in the early hours of the next UK day. A morning "yesterday's results" recap missed those wrap-around matches.
- Fix: results and fixtures now use rolling 24h windows anchored on the moment the button is pressed, not calendar dates.
  - Yesterday's results / commentary recap: kick-off within the last 24h [now-24h, now).
  - Today's matches / commentary predictions: next 24h [now, now+24h).
  - Tomorrow's matches: [now+24h, now+48h).
  - Commentary "before" table (for overnight movers): finished matches older than 24h.
- Headers now derive from the matches actually in the window: a single UK date when they share one, or a range ("Friday 12 – Saturday 13 June") when a gameday straddles midnight. Empty windows say "No matches in the last/next 24 hours."
- Leaderboard unaffected (it always counts all finished matches).
- Note on timing: because the window is relative to press time, the family's habitual morning post captures the just-finished gameday cleanly. Pressing "today's matches" late in the evening will show the next 24h (i.e. tonight's late games + tomorrow morning's), which is the intended rolling behaviour.
- Tested: wrap-around gameday captured intact for both results and fixtures; rest-day empty states; full headless click-through of all five buttons with no errors.

## Change log (cont.)
- v1.7 — Switched summary generators (results, today, tomorrow, commentary) from calendar-date to rolling 24-hour windows so wrap-around gamedays stay intact.

## Leaderboard switched to static, daily-generated (v1.8)
- Decision: the leaderboard is now generated here (Claude, with reliable web-searched & confirmed scores) and published as fully static HTML, rather than fetching from the community live API in the browser. Reasons: the live API's uptime/CORS over a month were unproven, openfootball lags, and a sweepstake table doesn't need minute-by-minute liveness — once a day is ideal.
- leaderboard.html is now pure static: no fetch, no JS, no live API dependency. The podium + 24-row table are pre-rendered from standings computed at generation time. Displays instantly, can't break, works with JS disabled.
- Footer reads "Updated <date> · refreshed daily" (no live dot). Same floodlit design, podium, tie handling, pens-win rule.
- Generation script: gen_static_leaderboard.py — holds a RESULTS list (confirmed scores) and an UPDATED stamp; recomputes standings and re-emits the static page. To refresh: confirm the day's scores via search, append to RESULTS, bump UPDATED, regenerate, publish.
- Current standings baked in (as of 12 Jun, 2 matches): Lou 3pts (+2, Mexico 2-0), Nick 3pts (+1, South Korea 2-1); Laura 23rd (Czech Republic L), Carlotta 24th (South Africa L); all others level on 0.
- The main message-maker app (index.html) keeps its live/commentary features and the rolling-window logic; only the standalone leaderboard page became static.

## Change log (cont.)
- v1.8 — Standalone leaderboard regenerated as static HTML from confirmed scores; removed client-side live fetch from that page.

## Data source — final keyless architecture (v1.9)
- API-Football was evaluated and rejected: its free plan returned "Free plans do not have access to this season, try from 2022 to 2024" — the 2026 World Cup needs a paid tier. No money spent; the unused API_FOOTBALL_KEY secret can be deleted.
- Adopted a keyless two-source pipeline in the GitHub Action build script:
  - Primary: worldcup26.ir (rezarahiminia, real-time, no key). Team ids mapped to our canonical names (id-map + resolve()/alias normalisation for Türkiye, Côte d'Ivoire, United States, DR Congo, Korea, Bosnia, Cabo Verde, Czechia).
  - Fallback/merge: openfootball. Both sources are merged (live wins per match), so a gap in one is filled by the other.
  - Anti-regression guard retained: never blanks a populated page if both sources come back empty.
- The Action now also writes scores.json (keyed by our canonical names) and build-status.json (diagnostics: which source ran, counts, any unmatched names) and commits all three.
- The message-maker app (index.html) reads the published scores.json first (same-origin on GitHub Pages, keyless), then the live API, then embedded/Claude-search — so its results/leaderboard/commentary get the same reliable scores without any client-side key.
- Verified live: the Action pulled both real day-1 results (Mexico 2-0 South Africa, South Korea 2-1 Czech Republic) from worldcup26.ir with zero manual input, committed scores.json + a rebuilt leaderboard. build-status.json: worldcup26 "2 finished matches", played 2, no unmatched teams.
- Security: no API keys or secrets anywhere in the repo or any published file. Workflow uses GitHub's built-in token for commits; any future key would live only in Actions Secrets (added by the user directly), never committed.

## Change log (cont.)
- v1.9 — Rejected paid-only API-Football; built keyless worldcup26.ir + openfootball merge in the Action, publishing scores.json (consumed by the app) and build-status.json. Live-verified.

## Bracket page (v2.0)
- New standalone file bracket.html (published; not yet cross-linked to the leaderboard — links to be added later in the tournament per request).
- Renders the full 2026 knockout structure (new 48-team format): Round of 32 (matches 73-88), Round of 16 (89-96), Quarter-finals (97-100), Semi-finals (101-102), Third-place play-off (103), Final (104) — wiring taken from the openfootball feed (authoritative slot labels: 1A/2B winners-runners-up, 3A/B/C/D/F best-third slots, W##/L## feeders).
- Round-tab navigation (R32/R16/QF/SF/3rd/Final) — phone-first; avoids the unreadable tiny-tree problem. Each tie is a card: both teams (flag + name, or italic placeholder like "Winner Group E" / "3rd place (A/B/C/D/F)"), match number, date, venue, score when played, winner highlighted gold, penalties shown.
- Sweepstake hook: each known team shows its owner tag, and a "Sweepstake survivors" strip lists players whose teams are still alive (a team is dropped once it loses a knockout match). Hidden until the knockouts begin.
- Auto-populates: reads the live openfootball feed; resolves W##/L## chains so later rounds fill in as earlier results land. Falls back to embedded placeholders. Same floodlit design language as the leaderboard.
- Current state (group stage): all slots show placeholders with correct dates/venues, ready to populate from 28 June.
- TODO later: cross-link leaderboard <-> bracket; the daily Action could also rebuild a static bracket if desired (currently client-rendered).

## Change log (cont.)
- v2.0 — Added standalone bracket.html (knockout tree, owner tags, survivors strip), auto-populating from live data. Not yet linked from leaderboard.

## Commentary engine overhaul (v2.1)
- Why: on the hosted site the Claude-written path can't run (a static page can't auth to the Anthropic API), so the family always sees the LOCAL phrase-bank engine. That fallback was thin (2-option pools -> repeats with several matches) and wrongly referenced extra time, which can't occur in the group stage.
- Rewrote localCommentary():
  - Anti-repetition picker (makePicker): never reuses a template from a category within one message until that pool is exhausted; pools enlarged to 3-9 options each across openers, result colour, table talk, prediction kickers, signoffs.
  - Placeholder templates ({T}/{PL}/{B2} etc.) filled after selection, so variety + clean substitution.
  - Group-stage correctness: a knockout flag (true only from 28 Jun 2026) gates ALL extra-time/penalty/shootout language. In the group stage draws are framed as shared points; no ET/pens wording anywhere. Removed the old "even if it's just extra time" joke.
  - Data-driven colour: phrasing branches on margin (1/2/3+), clean sheet, goalless vs scoring draw; plus a computed "talking point of the day" (rout of the day when max margin >=3, or goal-fest when an aggregate >=5).
  - Recap only includes matches that have actually finished (kickoff + 2h45 < now), so in-play games aren't reported as results.
  - Mover line suppressed when no prior-window results existed (avoids meaningless "up 19 places" from alphabetical noise); top-3 players with no upward stake get a "protect Nth place" line.
  - Capitalisation fix on the stakes clause.
- Claude-written path (used on claude.ai) also updated: prompt now states the phase and forbids extra-time/penalty references during the group stage, and asks for varied, non-repeating phrasing.
- Verified: realistic current-day output (USA 4-1 rout, Canada 1-1 draw, table talk, four varied duel predictions) reads cleanly with no repeats and no ET language; full headless app test passes with no errors.

## Change log (cont.)
- v2.1 — Overhauled the local commentary engine: anti-repetition, richer data-driven phrasing, group-stage correctness (no extra-time references), finished-only recap.

## Commentary accuracy + journalist quality + leaderboard link (v2.2)
- Bug fixed: the Claude-written path could mangle a fixture into three teams (e.g. "USA face Qatar against Switzerland") because a player owning two teams (Kate: USA + Qatar) was passed only as "Kate vs Jonathan" with no binding to which team was in THIS match. The model grabbed the wrong team.
- Fix: each fixture (and each result) now passes explicit per-side binding \u2014 team_home/owner_home and team_away/owner_away, plus each owner's table position and a same_owner flag. The prompt was rewritten to broadsheet-football-journalist standard with STRICT accuracy rules: exactly two teams per fixture, never introduce a third team or a player's other teams, attribute owners correctly, use only provided data (no invented scores/events), respect the phase (no extra time/pens in the group stage), vary language, spell names exactly.
- Leaderboard link appended to EVERY commentary message (both Claude and local paths) via a LEADERBOARD_FOOTER constant: "\ud83d\udcca Full table: https://paulshep.github.io/worldcup2026/leaderboard.html".
- Verified: fixture data binds Qatar->Kate / Switzerland->Jonathan unambiguously; footer present on local-path output; full app test passes with no errors.

## Change log (cont.)
- v2.2 — Fixed three-team conflation in Claude commentary via explicit per-team owner binding + stricter journalist-grade prompt; appended leaderboard link to all commentary messages.

## Commentary roundup-count fix (v2.3)
- Bug: Claude-path opened with "Two games down and the tournament is already delivering" \u2014 only 2 games were in the last-24h recap window, but 4 had been played (2 match-days). The model read the recent-results count as the tournament total.
- Fix: data now passes games_in_this_roundup (last-24h count) AND games_played_in_tournament_total (all finished), with a roundup_note explaining the distinction, and a prompt rule forbidding the model from stating a tournament total from the recent batch or implying the tournament just started. Recap is framed as the latest match-day.

## Change log (cont.)
- v2.3 — Fixed commentary misstating tournament progress by separating the daily-roundup game count from the tournament total.

## Commentary completeness fix (v2.4)
- Bug: a finished match (Australia 2-0 Turkey, a late Vancouver kickoff) was omitted from the recap. Causes: (a) openfootball lacked its score at generation time, and (b) the journalist model silently skipped the scoreless game; additionally the strict kickoff+2h45 "finished" buffer could drop a very recently finished match entirely.
- Fixes: results window now includes a match if it HAS a score (definitely done) OR kickoff+2h45 has passed \u2014 so scored games are never dropped by the buffer. Journalist prompt now requires mentioning EVERY recent_results match, noting "result still to come" for any without a confirmed score instead of skipping it. (The local engine already listed unscored matches.) Once the hourly Action ingests the live 2-0, the real score replaces the placeholder.

## Change log (cont.)
- v2.4 — Recap no longer drops finished-but-unscored or very-recently-finished matches; journalist must mention every game.

## Match-data status button (v2.5)
- Added a sixth button on the message-maker page, "Match data" (under Commentary), a feed-diagnostics view (not a WhatsApp message).
- Shows: when scores.json was last published (relative + UK time, source, count of scored games); when the hourly build job last ran with its per-source finished-match counts and any unmatched names; then every match in the last 24 hours with kick-off (BST) and a status badge \u2014 \u2705 published / \u2705 in feed (not yet in published file) / \u23f3 finished, awaiting score / \ud83d\udd34 in play / \u23f1 upcoming.
- Purpose: makes score-publish lag visible (e.g. a late kickoff like Australia v Turkey showing "awaiting score" explains a commentary omission as a freshness issue, not a bug). Output is copyable for easy debugging.
- Reads scores.json + build-status.json same-origin (hosted site); degrades gracefully when run locally.

## Change log (cont.)
- v2.5 — Added "Match data" diagnostics button: published-data freshness + per-match score availability for the last 24h.

## Three-source freshest-wins data merge (v2.6)
- Added football-data.org as an authoritative source in the hourly Action (GET /v4/competitions/WC/matches, key from FOOTBALL_DATA_KEY secret \u2014 never committed; user rotates the key they pasted in chat).
- Merge is per-match for maximum freshness: a match counts as soon as ANY source has its confirmed final score (union of openfootball + worldcup26.ir + football-data.org). On overlap the more authoritative source wins, applied in order openfootball (base) -> worldcup26.ir -> football-data.org (last/authoritative), so a flaky source can't override a confirmed authoritative result and the rebuild self-corrects each hour. Only FINISHED/AWARDED scores are accepted; penalties parsed (duration PENALTY_SHOOTOUT).
- Team names resolved via the existing normalise/alias map (Korea Republic, United States, Cote d'Ivoire, Turkiye, Czechia, Cabo Verde, etc.); any unmatched names surface in build-status.json.
- Diagnostics: build-status.json now reports football-data.org's finished count AND its newest match lastUpdated timestamp, so the "Match data" button reveals football-data.org's real freshness in production \u2014 letting us empirically confirm whether it beats the others before relying on it.
- Free-tier note: football-data.org free is 10 req/min (1 call/run, fine) and covers the World Cup; its scores are "delayed" vs paid real-time, but for an hourly rebuild what matters is final-result latency, which the merge measures live. If it underperforms, the other two sources already cover us and it can be removed in one line.
- Activation: dormant until the FOOTBALL_DATA_KEY secret is added (reports "no key in env" meanwhile; other sources unaffected).

## Change log (cont.)
- v2.6 — Added football-data.org as authoritative source with a per-match freshest-wins merge across all three feeds; diagnostics expose its lastUpdated freshness.

## football-data.org validated in production (v2.6.1)
- Renamed env/secret to FOOTBALL_API_KEY to match the secret the user created.
- First live run (14 Jun 06:53 UTC) result: football-data.org returned 8 finished matches incl. Australia 2-0 Turkey (newest lastUpdated 06:03Z) \u2014 fresher AND more complete than openfootball (7, still missing Australia). worldcup26.ir FAILED this run (DNS/name-resolution error) \u2014 the hobby host was unreachable; football-data.org covered the gap. Merge label "football-data.org+openfootball", 8 games, no unmatched names. Leaderboard rebuilt to 8 matches; Euan (Australia) up to 3rd.
- Conclusion: football-data.org is the authoritative, reliable primary; the freshest-wins merge means it fills gaps and overrides flaky sources, while worldcup26.ir/openfootball remain as fallbacks. The earlier "missing Australia v Turkey" issue is resolved at the data layer.

## Change log (cont.)
- v2.6.1 — football-data.org live-validated as freshest/most reliable source (covered for worldcup26.ir outage); secret name aligned to FOOTBALL_API_KEY.

## Commentary now uses the football-data.org-backed scores.json (v2.7)
- Problem: the commentary/leaderboard-button score path (gatherAllScores) started from a persistent cache (cacheGet "wc26-scores") of earlier web-searched scores. Fresh data only overrode it on overlap, so stale/wrong cached values (e.g. an old Qatar 0-2 vs the real 1-1) and gaps could make the commentary diverge from the now-authoritative leaderboard.
- Fix: scores.json (football-data.org-backed, refreshed hourly) is now the authoritative base for gatherAllScores. It is re-fetched and mapped from its undated a|b keys to our dated mKey (a|b|d); m.s (already overlaid from scores.json + live in overlayLive) is used first, the fresh fetch backs it up, web-search is a last resort only for genuinely missing finished matches, and the local cache is consulted ONLY if the published file is unreachable and we have nothing. Cache key bumped to wc26-scores-v2 so any poisoned old cache is abandoned.
- Result: commentary standings/scores now match the leaderboard exactly (verified: poisoned cache 0-2 ignored, scores.json 1-1 used; 8 finished = 8 score entries; top 5 identical to leaderboard). Residual freshness bound is the hourly Action, same as the leaderboard (client can't call football-data.org directly \u2014 key stays server-side).

## Change log (cont.)
- v2.7 — Commentary scores now sourced authoritatively from the football-data.org-backed scores.json; stale-cache override bug removed (cache key bumped).

## Rebuild frequency increased to every 5 minutes (v2.8)
- Verified limits (football-data.org official policy docs): free plan = 10 requests/minute, a pure rate limit with NO daily/monthly cap. The Action makes 1 football-data call per run, so even at the max frequency usage is ~0.2 req/min \u2014 far under the limit.
- football-data.org's own backend recomputes ~every 5 minutes, so its free-tier data granularity is ~5 min; polling faster would be pointless.
- Binding constraint is GitHub Actions: scheduled workflows can't run more often than every 5 minutes. Set cron to */5 * * * * (was hourly).
- Cost/noise: GitHub Actions minutes are free/unlimited on public repos; the "commit only if changed" guard means no-op runs make no commits, so higher frequency adds no repo noise. worldcup26.ir/openfootball are hit each run too (fine; worldcup26.ir is a fallback).
- Effect: max result lag drops from ~60 min to ~5 min for both the leaderboard and the commentary (which reads the same scores.json). GitHub may occasionally delay a scheduled run under load; the next run catches up.

## Change log (cont.)
- v2.8 — Action frequency increased from hourly to every 5 minutes (GitHub's floor); confirmed well within football-data.org's 10 req/min, no daily cap.

## Commentary: time-aware greeting + flags after every country (v2.9)
- Greeting now reflects the actual UK time of day: GOOD MORNING/AFTERNOON/EVENING computed from Europe/London hour (was hard-coded "GOOD EVENING"). Night-specific sign-offs ("Good night", "nightmares") made time-neutral. The Claude-written path is told the current UK time-of-day and instructed to greet accordingly and never reference a different one.
- Every country/team mention is now followed by its flag emoji. New withFlags() post-processor appends each country's flag after every occurrence (longest names first to avoid partial matches; negative lookahead prevents double-flagging; handles tag-sequence flags like Scotland). Applied to BOTH commentary paths; the local scoreline switched from leading-flag to bare names so flags are uniform/trailing. Claude path also instructed to add trailing flags.
- Verified: morning/afternoon/evening greetings correct; flags appear in scorelines, colour prose, table talk and predictions; Scotland tag-flag works; no double flags; full app test passes, no errors.

## Change log (cont.)
- v2.9 — Commentary greeting is now time-of-day aware (UK), and every country mention is followed by its flag emoji (both writer paths).

## Group stage summary button (v3.0)
- New "Group stage" button on the message-maker page: a player-by-player WhatsApp summary of how each player's two teams have done and how many are through to the knockouts.
- Groups (A-L) are derived from the fixture list (first 72 games run in blocks of 6 = one group each), since the feed doesn't label groups and the knockout fixtures are still placeholder-coded. Each group's table is computed from the published scores (Pts, then GD, then GF; head-to-head not modelled - a reasonable approximation for a family pool).
- Qualification uses the real 2026 rules: top 2 of each completed group go through; once ALL groups are complete the 8 best third-placed teams are ranked and confirmed (24 + 8 = 32). Degrades honestly while games are outstanding: in-progress groups show "Nth so far", third-placed teams in finished groups show "best-third spot still to be decided" until everything is done.
- Per player: "N of 2 through" plus a status line per team (THROUGH as winners/runners-up / best third-placed; OUT; or current position). Footer totals confirmed qualifiers and players with both/one alive. withFlags() applied so every country gets its flag.
- Verified: group letters/membership correct; all-complete simulation yields exactly 32 through (24 top-2 + 8 best thirds), 4 thirds miss the cut; no errors in full app test.

## Change log (cont.)
- v3.0 — Added "Group stage" player-by-player summary button (group tables + 2026 top-2 + best-8-thirds qualification, progressive while group stage incomplete).

## Group stage summary: wry per-player one-liner (v3.1)
- The "Group stage" button now adds a one-line wry verdict per player (in the spirit of the Commentary button), shown in WhatsApp italics under the "N of 2 through" header, above the per-team status lines.
- Uses the shared makePicker() anti-repetition picker so phrasing varies across the 24 players. Categories: both-through (with sub-flavours for both-group-winners vs one-via-best-third), one-through (names who survives and who exits), both-out, and a provisional variant for when groups are still in progress. Specifics are drawn from each team's group position/record; withFlags() adds flags to country names inside the verdict.
- Verified across the completed group stage: lines are accurate to each player's situation and vary; no errors.

## Change log (cont.)
- v3.1 — Group stage summary gains a wry one-line-per-player verdict (commentary-style), with the factual team lines retained beneath it.

## Knockout fixtures integrated (knockouts.json) (v3.2)
- Root cause of two issues: the app's knockout fixtures were unresolved placeholders (2A, 1E, 3A/B/C/D/F...). The commentary/today/tomorrow therefore couldn't name knockout teams ("still to be decided"), and while the group-stage "through" count is computed from group tables (and works once all 72 group games are in), the bracket had no authoritative resolution.
- Fix: the Action now publishes knockouts.json (mirroring scores.json), built from football-data.org (authoritative bracket source; key stays server-side). Each fixture: {stage, utc, a, b, s|null}. Only fixtures with BOTH teams resolved are included (best-third-dependent slots appear as the feed assigns them; FIFA/football-data resolve those shortly after the group stage, so the file fills progressively and the frequent Action picks them up).
- Client: overlayKnockouts() reads knockouts.json and replaces placeholder knockout fixtures in the match list by matching kick-off instant (so schedule/venue/owner mapping are preserved), adding scores as games are played. Wired into both loadMatches paths. This feeds the results/today/tomorrow/commentary machinery real teams.
- Group button: in addition to the computed top-2 + best-8-thirds logic, any team the feed has placed in the Round of 32 is confirmed THROUGH (handles FIFA's exact best-third slotting authoritatively as it resolves). Computed remains primary (more complete than the partial early feed); R32 confirmation is a union.
- Verified: with current data, today's matches names "South Africa v Canada" (resolved 2A v 2B) with venue/owners intact; group button shows 32 through; no errors.

## Change log (cont.)
- v3.2 — Added knockouts.json (resolved bracket from football-data.org) and client overlayKnockouts(); knockout commentary/fixtures now name real teams, group button confirms via R32.

## Knockout source robustness (v3.3)
- Investigation: at the close of the group stage, NO provider had the full Round of 32 resolved. openfootball had ~3 of 16; football-data.org fluctuated 0-4 (it was observed dropping resolved ties back to 0 as the official best-third-placed slot assignment was being finalised). Later rounds are unresolvable until earlier ties are played.
- Problem this exposed: knockouts.json mirrored the live feed, so resolved ties could disappear when a feed momentarily dropped them.
- Fix: knockouts.json is now a UNION of football-data.org (authoritative) + openfootball, merged keyed by kick-off instant, and STICKY/anti-regression - it reads the previously published file and retains already-resolved ties (a resolved tie is factual and must not regress), lets openfootball fill gaps, and lets football-data overwrite teams + refresh scores. openfootball knockout times are converted to a UTC instant via the embedded "UTC±X" offset. Result: the file only accumulates toward the full 16 and survives feed churn (verified: retained all 4 ties when football-data returned 0).

## Change log (cont.)
- v3.3 — knockouts.json hardened: union of both feeds + sticky anti-regression so resolved ties never disappear during the post-group-stage bracket churn.

## Self-resolving Round of 32 from our own tables (v3.4)
- Problem: even after the group stage finished, no live data source we could reach was current. The football-data.org / openfootball feeds still lagged on the best-third slot assignments, and ESPN's free JSON API (`site.api.espn.com/.../fifa.world/scoreboard`) was checked and found *stale* — it served an early-tournament snapshot (16 June fixtures still "Scheduled") and ignored the `dates` parameter, so it was behind our own data, not ahead. Conclusion: no external API was more current than what we already had.
- Insight: once every group is complete, the Round of 32 is fully determined by the group tables, so we can resolve it ourselves with no feed dependency. Winner/runner-up slots come straight from the standings; the eight best-third slots follow FIFA's official **Annex C** allocation (the 495-combination table from the tournament regulations — regs column order 1A,1B,1D,1E,1G,1I,1K,1L). Our combination of qualifying-third groups is **{B,D,E,F,I,J,K,L}** = Annex C **row 67** → {1A:3E, 1B:3J, 1D:3B, 1E:3D, 1G:3I, 1I:3F, 1K:3L, 1L:3K}.
- Validation: the resulting 16 ties match the confirmed bracket reported by CBS / NBC / Sky / SI and the Wikipedia knockout-stage page (e.g. Germany v Paraguay, France v Sweden, USA v Bosnia, Argentina v Cape Verde). Computed from our own scores.json the bracket is: South Africa v Canada, Germany v Paraguay, Netherlands v Morocco, Brazil v Japan, France v Sweden, Ivory Coast v Norway, Mexico v Ecuador, England v DR Congo, USA v Bosnia & Herzegovina, Belgium v Senegal, Portugal v Croatia, Spain v Austria, Switzerland v Algeria, Argentina v Cape Verde, Colombia v Ghana, Australia v Egypt.
- Implementation:
  - **index.html** — new `wcStandings()` (group tables from our scores) + `ANNEX_C` table + `deterministicR32()`, called inside `overlayKnockouts()` *after* the feed pass. The feed (knockouts.json) still runs first and wins where present; the deterministic pass fills any slot it left as a placeholder. A safety de-dupe drops any exact duplicate knockout fixture. Only runs once all 12 groups are final and the combination is known.
  - **bracket.html** — embeds `GROUPS` (group→teams) + the same `ANNEX_C` + `r32FromGroups(scores)`, run in `loadResults()` after the openfootball feed. Computes the tables from scores.json, fills every R32 slot, and pulls each tie's score from scores.json when available. Previously the bracket only resolved slots from openfootball directly, so it showed mostly placeholders during the slotting delay.
- Net effect: both the app and the bracket show the complete, correct Round of 32 the instant the group stage ends, regardless of how slowly any external feed catches up. The feed-based knockouts.json remains as a cross-check and is what will carry later-round (R16+) resolutions as those ties are played.
- v3.4 — Round of 32 now self-resolves from our own group tables + FIFA Annex C (row 67 for the {B,D,E,F,I,J,K,L} third-place combination), in both index.html and bracket.html; feed-independent, feed still wins where present.

## Knockout ties in the group commentary (v3.5)
- The "Group stage" player-by-player button now folds the resolved Round of 32 into each verdict: under every through team it adds its actual knockout tie — opponent, the rival sweepstake player who owns them, and the kick-off in BST (e.g. "Bosnia & Herzegovina ✅ THROUGH … ↳ Round of 32: vs USA (Kate's) — Thursday 2 July, 1:00am"). A "(also <name>'s — a civil war!)" tag appears if one player happens to own both sides of a tie. Ties are read from the already-overlaid fixtures, so they use the same feed-first / Annex C-fallback resolution as everywhere else. A closing line confirms "The Round of 32 is set" once all 16 are known.
- v3.5 — Group summary names each survivor's R32 opponent (with owning player + BST kick-off).
