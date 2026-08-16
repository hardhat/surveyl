# Surveyle - Milestones and Todo List

Derived from [specification.md](specification.md). Milestones are ordered so each one is independently demoable/testable before starting the next. Every item includes a concrete test/verification so completion is unambiguous.

## Milestone 0: Infrastructure Foundations

- [ ] Provision Supabase project (PostgreSQL, Auth, Edge Functions enabled). **Test:** can connect via `supabase-js` and run a trivial `select 1` query.
- [ ] Provision AWS EC2 instance with Nginx, Python runtime, and a process manager (e.g. systemd/cron). **Test:** EC2 serves a static "hello world" page over HTTP/HTTPS.
- [ ] Enable Supabase Anonymous Auth. **Test:** calling `signInAnonymously()` from a test script returns a valid session/JWT with a `uid`.
- [ ] Create `admins` table + Supabase email/password auth for a single admin user. **Test:** admin can log in; a non-admin anonymous user is rejected by an RLS policy referencing `admins`.
- [ ] Configure service-role key usage on EC2 only (never shipped to the SPA bundle). **Test:** grep built frontend bundle for the service-role key string and confirm it is absent.
- [ ] Set up an EC2 cron heartbeat that pings Supabase on a schedule. **Test:** Supabase project logs show a query at the expected interval and does not auto-pause after 7+ days.

## Milestone 1: Core Data Model

> Convention: apply all schema changes as `infra/supabase/migrations/*.sql` files via `supabase db push`, not the dashboard SQL Editor, so local migration history stays in sync with the remote project (see `0001_admins.sql` for the reconciliation this avoids).

- [ ] Create ingestion tables: raw stories, canonical clustered stories. **Test:** inserting two similarly-worded raw stories and clustering them results in one canonical story row.
- [ ] Create daily top-story selection metadata table. **Test:** a day's top-5 selection can be queried by date and returns exactly 5 ranked rows.
- [ ] Create Round 1 clue tables (variants, edit history). **Test:** editing a clue via SQL/admin API preserves the prior version in history.
- [ ] Create Round 2 canonical question table. **Test:** a question row links to exactly one story and one day.
- [ ] Create Round 3 candidate question + variant assignment tables. **Test:** a story has exactly 3 candidates; assigning a player produces exactly 1 variant per story per player.
- [ ] Create player attempt state table (per-round progress, cookie/anon id, day). **Test:** two attempts from the same anon id on the same day are rejected by a unique constraint/RLS policy.
- [ ] Create poll responses + analytics aggregate tables. **Test:** submitting 3 responses to one question updates an aggregate count via trigger or query.
- [ ] Write RLS policies for all player-facing tables (read own attempt, write own attempt, no cross-player access). **Test:** anon user A cannot read or write anon user B's attempt row (verified via two separate anon sessions).
- [ ] Write RLS bypass policies for service-role (EC2 ingestion/admin) access. **Test:** EC2 service-role client can insert/update any row regardless of RLS.

## Milestone 2: News Ingestion Pipeline (EC2 Python Cron)

- [ ] Implement source whitelist config for curated UK national outlets. **Test:** ingestion run only pulls from configured sources, confirmed via log/output inspection.
- [ ] Implement raw story fetch job. **Test:** running the job populates the raw stories table with today's articles.
- [ ] Implement deduplication/clustering (headline similarity, keywords, named entities). **Test:** feeding 5 known duplicate headlines produces 1 canonical story.
- [ ] Implement weighted ranking (coverage volume > search spikes > social engagement). **Test:** unit test with fixed synthetic inputs produces the expected rank order.
- [ ] Implement top-5 selection + decoy generation (12 candidates, 5 correct, plausible decoys). **Test:** a completed run produces exactly 12 Round 1 candidates with exactly 5 flagged correct.
- [ ] Implement clue generation (satirical summary, redacted headline, keyword cluster) via LLM call. **Test:** each of the 5 top stories has at least one generated clue in the DB after a run.
- [ ] Implement Round 3 candidate question generation (3 candidates per next-day story). **Test:** after a run, each of the day's 5 stories has exactly 3 Round 3 candidate questions.
- [ ] Implement Round 2 canonical selection logic (lowest skip rate → highest answers → random tiebreak) as a scheduled job/function. **Test:** feeding synthetic skip/answer data selects the expected winning candidate; tie case resolves via random with a fixed seed test.
- [ ] Implement promotion/expiry logic (winning Round 3 question becomes tomorrow's Round 2 question if its story makes top 5; otherwise discarded). **Test:** simulate a story making vs. not making tomorrow's top 5 and confirm correct promotion/discard behavior.
- [ ] Enforce the 3:30am ingestion freeze and 6:00am publish schedule via cron timing. **Test:** cron schedule entries match 3:30am and 6:00am UK time (including BST/GMT handling).
- [ ] Implement ingestion failure fallback (serve previous day's game + warning banner, no fallback badge, no replay). **Test:** simulate ingestion failure and confirm the API/game package returns yesterday's content with a warning flag.
- [ ] Implement late-success override (replace fallback with real game after 6am, let in-progress fallback sessions finish). **Test:** simulate late ingestion success after a fallback session started; confirm new sessions get today's game while the started session can still complete.

## Milestone 3: Admin Dashboard (EC2-hosted)

- [ ] Build admin login screen using Supabase Auth. **Test:** valid admin credentials log in; invalid credentials are rejected with an error.
- [ ] Build review queue for generated stories/questions (approve/reject). **Test:** rejecting a Round 3 candidate immediately triggers regeneration of only that candidate (not all 3).
- [ ] Build editors for clues, summaries, candidate questions, and explanations. **Test:** an edited field persists after page reload and is reflected in the next game package fetch.
- [ ] Surface the auto-selected Round 2 winner (read-only highlight, no manual override needed). **Test:** admin UI visibly marks the winning candidate matching the selection-logic output.
- [ ] Build basic analytics/observability view (active players, completion rates, skip rates, format performance). **Test:** dashboard numbers match a manual SQL aggregate query for the same day.

## Milestone 4: Round 1 - Top Stories Identification

- [ ] Build Round 1 UI: 12 candidates, one-by-one confirmed picks, no ranking required. **Test:** selecting 5 candidates one at a time locks in each pick and prevents un-picking a confirmed one (per spec's confirm-one-by-one UX).
- [ ] Implement optional second clue per story with 25% point reduction (only applied if ultimately correct). **Test:** taking the second clue on a rank-1 story (5 pts) and answering correctly yields 3.75/4 pts per defined rounding; getting it wrong yields 0 with no extra penalty.
- [ ] Implement hidden rank-based scoring (5/4/3/2/1 by real rank, unordered from the player). **Test:** correctly picking all 5 stories yields exactly 15 points regardless of pick order.
- [ ] Implement text-only clue rendering (satirical summary, redacted headline, keyword cluster). **Test:** no image assets are requested/rendered in Round 1.
- [ ] Implement Round 1 results screen. **Test:** after submission, screen shows which of the 5 real stories were correctly identified and points earned per story.

## Milestone 5: Round 2 - Poll Result Estimation

- [ ] Build fixed-order question flow (5 questions, one per top story, matching ranking order). **Test:** question order in UI matches the day's top-story rank order.
- [ ] Build multiple-choice UI (always 4 options, fixed order, no shuffling). **Test:** same question rendered twice in the same session shows options in identical order.
- [ ] Build percentage slider UI (0-100, step 5, default 50, must move before submit). **Test:** submit button is disabled/blocked until the slider is moved at least once; only multiples of 5 are selectable.
- [ ] Implement multiple-choice scoring (correct/incorrect, immediate reveal). **Test:** correct answer reveals immediately post-submit with right/wrong state shown.
- [ ] Implement percentage scoring bands (exact=5, ±5=4, ±10=3, ±15=2, ±20=1, else=0). **Test:** unit tests for boundary values (e.g., exactly 5, 10, 15, 20 away) return the correct band score.
- [ ] Implement skip behavior (0 points, can still finish). **Test:** skipping all 5 questions still allows reaching the final summary with 0 Round 2 points.
- [ ] Implement abandonment-counts-as-skip analytics (no scoring impact, analytics only). **Test:** closing the browser mid-Round-2 after a question is shown increments that question's skip count in analytics.
- [ ] Implement post-question feedback (right/how close, points earned, cheeky admin-editable explanation). **Test:** each answered question shows a non-empty explanation string sourced from the admin-edited field.

## Milestone 6: Round 3 - Crowd Testing

- [ ] Build shuffled question order UI (5 questions, one randomly assigned variant per story). **Test:** running the same session twice with a fixed seed produces a different displayed order than story rank order.
- [ ] Implement random variant assignment on Round 3 entry, fixed for the rest of the session. **Test:** re-fetching Round 3 mid-session returns the same previously-assigned variant, not a new random one.
- [ ] Implement participation scoring (1 point per answered question, max 5, no reveal). **Test:** answering all 5 yields 5 points with no correct/incorrect indicator shown.
- [ ] Implement skip/abandonment analytics parity with Round 2 (skips reduce only participation credit). **Test:** skipping 2 of 5 questions yields 3 participation points and logs 2 analytics skips.
- [ ] Build end-of-Round-3 confirmation screen (no recap, no points shown here). **Test:** screen after Round 3 shows only a short message, no per-question detail, no point total.

## Milestone 7: Scoring Summary and Sharing

- [ ] Implement final summary computation (total, max possible, per-round breakdown). **Test:** a fully-played day with known answers produces the expected total/max/per-round numbers via integration test.
- [ ] Implement cheeky label banding (4 bands by % of max score: 0-24, 25-49, 50-74, 75-100). **Test:** unit tests at each band boundary (24%, 25%, 49%, 50%, etc.) select the correct band.
- [ ] Build final summary screen with Round 3 "resolves tomorrow" reminder. **Test:** screen renders total, max, per-round scores, label, and the reminder text.
- [ ] Implement one-tap share text copy (site name, alias, date, raw score, cheeky label, emoji; no denominator/breakdown). **Test:** copied clipboard text matches the fixed template exactly for a known score/alias/date input.

## Milestone 8: Sessions, Identity, and Daily Publishing Rules

- [ ] Implement alias auto-generation and editing (2-24 chars, allowed charset, no reset of streak on change). **Test:** editing alias mid-streak leaves streak data unchanged; invalid characters/length are rejected client- and server-side.
- [ ] Implement one-scored-attempt-per-day enforcement via anon id + RLS. **Test:** attempting to start a second scored attempt same day (same anon session) is blocked with an appropriate response.
- [ ] Implement pause/resume within the same day. **Test:** reloading mid-Round-2 restores prior round results and current round progress.
- [ ] Implement hard session expiry at next 6:00am reset. **Test:** an in-progress session from before 6:00am is inaccessible/reset after the cutoff passes.
- [ ] Implement round submit/lock behavior (editable pre-submit, final post-submit). **Test:** attempting to resubmit a locked round's answer is rejected.
- [ ] Implement local storage streak/comparison data (start date, length, yesterday's stats), shown only post-completion. **Test:** streak data is absent from any UI element before the player finishes today's game.
- [ ] Implement Round 1 home timeline showing all 3 rounds with sequential gating. **Test:** attempting to open Round 2 or 3 before completing the prior round is blocked in the UI.

## Milestone 9: Accessibility, UX, and Privacy

- [ ] Implement keyboard navigation across all rounds. **Test:** full game playable end-to-end using only Tab/Enter/Arrow keys.
- [ ] Implement screen-reader labels for all interactive elements. **Test:** automated accessibility audit (e.g. axe) reports no missing-label violations on each screen.
- [ ] Implement high-contrast support and non-color-only correctness cues (icons/text alongside color). **Test:** correctness state is distinguishable in a grayscale screenshot of the results screen.
- [ ] Implement sound effects with default-on + persistent mute toggle. **Test:** toggling mute persists across a page reload.
- [ ] Implement first-visit consent notice (cookie identity + analytics). **Test:** notice appears on first visit only and does not reappear after dismissal on the same browser.
- [ ] Implement IP-based rate limiting on submission endpoints. **Test:** exceeding the configured request threshold from one IP returns a rate-limit response.
- [ ] Implement crowd-comparison threshold gating (hide "compared to others" language below 20 completions/day). **Test:** with 19 completions, comparison language is absent; at 20, it appears.

## Milestone 10: Analytics and Observability

- [ ] Implement daily active player tracking. **Test:** completing N sessions in a day produces a matching DAU metric.
- [ ] Implement round completion rate tracking. **Test:** metric matches manually computed completion ratio for a seeded test dataset.
- [ ] Implement skip-rate-per-question tracking (Round 2 and 3 only, including abandonment). **Test:** seeded skip/answer/abandon data produces the expected skip rate per question.
- [ ] Implement top-performing question format tracking. **Test:** metric correctly ranks formats by a seeded performance dataset.

## Milestone 11: Automated Testing Hardening

- [ ] Automated tests for story ranking logic. **Test:** CI run passes a suite covering tie-breaking and weighting edge cases.
- [ ] Automated tests for daily cutoff handling (3:30am freeze, 6:00am publish, fallback/late-success paths). **Test:** CI run passes simulated-clock tests for each timing branch.
- [ ] Automated tests for one-play-per-day enforcement. **Test:** CI run passes a test asserting a second same-day attempt is rejected.
- [ ] Automated tests for core scoring logic (Round 1 rank-based, Round 2 MC + percentage bands, Round 3 participation). **Test:** CI run passes all scoring unit tests, including boundary values.

## Milestone 12: Launch Readiness

- [ ] End-to-end smoke test of a full day's cycle (ingestion → publish → play all 3 rounds → summary → share) on a staging EC2 + Supabase environment. **Test:** manual run-through completes with no errors and correct final score.
- [ ] Confirm Supabase free-tier usage headroom (DB size, egress, function invocations) against expected launch traffic. **Test:** documented capacity check against current Supabase plan limits.
- [ ] Confirm EC2 keep-alive cron prevents Supabase project pausing over a 2+ week idle-traffic window. **Test:** project remains active/queryable after the observation window.
- [ ] Verify service-role key is not exposed client-side and admin routes are not publicly linked from the SPA. **Test:** security review of built frontend bundle and network requests confirms no key leakage.
