# Surveyle.co.uk - Product Specification

## 1. Product Summary

Surveyle is a mobile-first daily UK news web game with a mildly cheeky editorial tone. Each day presents players with a three-round experience based on the biggest UK news stories from the previous news cycle. The game is designed to be completed in under five minutes and uses a Supabase (PostgreSQL) backend with a Vue.js frontend consuming a JSON API, all hosted on an AWS EC2 instance.

The core loop is:

1. Identify the real top five UK news stories from clues.
2. Answer questions about those stories using the previous day's crowd-tested questions.
3. Answer today's crowd-testing questions that may become tomorrow's Round 2 questions.

Version 1 is UK English only, anonymous-only, current-day only, and optimized for mobile browsers.

## 2. Product Goals

### 2.1 Primary Goal

Create a daily replayable news game that mixes recognition, prediction, and participation around major UK stories.

### 2.2 Experience Goals

- Fast daily session, ideally under five minutes.
- Mobile-first interaction with large tap targets and minimal typing.
- Lightly cheeky tone without trivializing severe personal tragedy or targeting protected characteristics.
- Strong sense of daily rhythm and freshness.
- Sufficiently structured for reliable automated publishing with limited manual editorial intervention.

### 2.3 Non-Goals for V1

- No user accounts.
- No archive or replay of prior daily games.
- No public leaderboard.
- No public streak service.
- No community-submitted questions.
- No outbound article links.
- No multi-language support.
- No generated share image/card.
- No cross-day callback showing players how yesterday's Round 3 answers mapped to today's Round 2.

## 3. Audience and Editorial Tone

### 3.1 Target Audience

General news readers in the UK.

### 3.2 Tone

Mildly cheeky.

### 3.3 Editorial Safety Rules

Humor and copy should avoid:

- making light of active mass-casualty events
- sexual crimes
- child harm
- personal tragedies involving private individuals
- defamatory or unverifiable claims
- targeting protected characteristics
- implying facts that the poll itself cannot prove

Politics is allowed, but jokes should target absurdity, systems, media framing, or institutions rather than vulnerable individuals.

## 4. Platform and Technical Stack

### 4.1 Frontend

- Vue.js
- Mobile-first responsive web UI
- JSON API integration from day one
- Built SPA is served from the AWS EC2 instance

### 4.2 Backend

- Supabase project (PostgreSQL database, Auth, auto-generated REST API, Edge Functions)
- Row Level Security (RLS) policies enforce play rules (one attempt per day, round-lock behavior) directly in the database
- Supabase Anonymous Auth provides persistent per-browser identity in place of a custom cookie mechanism
- Scheduled ingestion and daily assembly jobs run as a python cron job on the AWS EC2 instance, writing to Supabase via a service-role key

### 4.3 Hosting

- A single AWS EC2 instance hosts:
	- the built Vue.js SPA (static files served via a web server such as Nginx)
	- the admin dashboard
	- the daily python cron job that performs news ingestion, ranking, and daily assembly
- Supabase hosts the PostgreSQL database, Auth, and auto-generated API only
- The EC2 python cron job also serves as a keep-alive so the Supabase free-tier project does not pause from inactivity

### 4.4 Locale

- UK English only in V1

## 5. Daily Publishing and Operational Rules

### 5.1 Publishing Cadence

- A new game publishes automatically every day at 6:00am UK time.
- Publication has no manual publish button in V1.

### 5.2 News Window

- Daily story selection uses a strict previous-day window.
- Overnight breaking stories that fall outside that window do not enter the day's game.

### 5.3 Ingestion and Review Timing

- News ingestion freezes at 3:30am UK time.
- Admin review window runs from 4:00am to 6:00am UK time.

### 5.4 Missed Review Behavior

- If admins miss the review cutoff, the game still publishes automatically.
- Auto-approved/generated content is used if necessary.

### 5.5 Ingestion Failure Fallback

If ingestion fails before the 6:00am publish:

- show the previous day's game instead
- show a short warning that it is the previous day's game
- do not add a dedicated fallback badge
- do not allow replay for players who already completed that previous-day game

If late ingestion succeeds after 6:00am:

- replace the fallback immediately with the real current-day game
- players who already started the fallback session can finish that fallback session
- the hard maximum session expiry still occurs at the next 6:00am reset

## 6. Identity, Sessions, and Storage

### 6.1 Identity Model

- Anonymous only in V1
- Identity is tracked via Supabase Anonymous Auth, which issues a persistent JWT/session stored client-side (cookie/local storage) on first visit
- No full account system
- Database access and one-play-per-day enforcement are backed by Postgres RLS policies keyed on the anonymous user's id, not just client-side checks

### 6.2 Alias Rules

- An alias is auto-generated on first visit
- Players can edit the alias at any time from settings or menu
- Alias changes do not reset local streak/history
- Alias is included in shared results

Alias constraints:

- minimum 2 characters
- maximum 24 characters
- allowed characters: letters, numbers, spaces, `-`, `_`, `.`
- no profanity/blocklist filtering in V1

### 6.3 Play Rules

- One scored attempt per day per browser/cookie identity
- Pause and resume is allowed on the same browser during the day
- Session expires hard at the next 6:00am reset
- Players can edit answers inside a round until that round is submitted or locked
- Once a round is submitted, answers in that round are final

### 6.4 Local Storage

Client local storage should retain a small JSON object containing:

- streak start date
- streak length in days
- yesterday's stats for comparison

This comparison is shown only after completing today's game.

## 7. Game Structure Overview

### 7.1 Round Order

The game has three rounds in fixed order:

1. Round 1: identify the top stories
2. Round 2: answer poll-result questions about those stories
3. Round 3: answer today's candidate questions for tomorrow

### 7.2 Home Screen

- Show all three rounds up front in a timeline
- Use house-style comedic names rather than plain utility labels
- Rounds remain sequentially gated even though they are visible in the timeline

### 7.3 Results Flow

- Show results after each round
- After Round 3, show a participation confirmation screen
- After that, show a separate final summary screen

## 8. Round 1 Specification

### 8.1 Player Goal

Identify the real top five stories from a candidate list using clues.

### 8.2 Candidate Set

- Show 12 candidate stories total
- Exactly 5 are correct
- Players identify which 5 are real top stories
- Players do not rank them

### 8.3 Story Selection

- Top 5 stories are selected automatically by ranking logic
- No daily human approval is required for the top-story shortlist in V1

### 8.4 Clues

Clue formats in V1:

- satirical summaries
- redacted headlines
- keyword clusters

Constraints:

- text only
- no images in V1
- clue sequence can vary by story
- clue text is admin-editable

### 8.5 Optional Second Clue

- Supported per story
- If used, it applies only to that specific story
- Taking the second clue reduces the available points for that story by 25 percent
- Penalty only matters if the story is ultimately identified correctly
- No extra penalty is applied if the player still gets it wrong

### 8.6 Selection UX

- Story picks are confirmed one by one
- This is preferred for mobile usability and pacing

### 8.7 Decoys

- Decoys should include intentionally plausible similar stories
- Decoys are not limited to simple ranks 6 to 12
- Decoys are generated automatically in V1
- No manual decoy curation is required in V1

### 8.8 Scoring

Each correct story is worth hidden points based on its actual internal rank:

- rank 1 story = 5 points
- rank 2 story = 4 points
- rank 3 story = 3 points
- rank 4 story = 2 points
- rank 5 story = 1 point

Because players do not rank the stories themselves, they earn the hidden value for each real story they correctly identify.

## 9. Round 2 Specification

### 9.1 Overview

- One question per top story
- 5 questions total
- Questions appear in fixed order matching the top-story ranking

### 9.2 Source of Questions

- Each Round 2 question is the automatically selected winner from the previous day's Round 3 candidate testing for that story
- This promotion path is invisible to players

### 9.3 Question Types

Round 2 can contain:

- percentage questions
- single-correct-answer multiple-choice questions
- other survey styles where appropriate

In practice, format mix is whatever emerges from the previous day's Round 3 winners.

Rules:

- no daily quota for specific formats
- no balancing rule such as forcing alternation
- it is acceptable if all five promoted winners are the same format type

### 9.4 Skip and Abandonment Rules

- Players may explicitly skip Round 2 questions
- A skipped question is worth 0 points
- Players can still finish even if they skip questions
- For internal analytics, if a player is shown a Round 2 question and abandons the game without answering, that also counts as a skip for that question

### 9.5 Canonical Question Selection Logic

For each story, the canonical Round 2 question is selected automatically from the three approved candidates using:

1. lowest skip rate
2. highest total answers as tiebreaker
3. random selection if still tied

Additional rules:

- always select from available data
- no minimum sample-size fallback rule in V1
- admin does not manually promote the winner
- admin UI highlights the selected winner
- admin UI does not need to expose the selection reasoning in V1

### 9.6 Multiple-Choice Requirements

- Always 4 answer options in V1
- Fixed editorial answer order
- No per-player shuffling
- Correct answer is revealed immediately after submission

### 9.7 Percentage Question Requirements

- Input is a slider
- Range is 0 to 100
- Step size is 5 percentage points
- Default visual position is 50
- Player must move the slider at least once before submission
- Exact correct percentage is revealed immediately after submission

### 9.8 Percentage Scoring

Score bands are fixed, not a smooth falloff:

- exact = 5 points
- within 5 points = 4 points
- within 10 points = 3 points
- within 15 points = 2 points
- within 20 points = 1 point
- otherwise = 0 points

### 9.9 Post-Question Feedback

After each Round 2 question, show:

- whether the player was right or how close they were
- points earned
- a short cheeky explanation of the real answer

These explanations are admin-editable.

## 10. Round 3 Specification

### 10.1 Purpose

Round 3 is the participation round that tests candidate questions for stories likely to appear the next day.

### 10.2 Story Basis

- Round 3 candidate questions belong to the next day's story set, generated by the news-ingestion pipeline
- For each future story, there must be 3 candidate questions

### 10.3 Candidate Set

- 3 candidate questions per story
- 5 stories total from the future story set
- Each player sees 1 randomly assigned question per story

### 10.4 Formats

- Candidate questions for a single story may use mixed formats
- They do not have to all be the same type

### 10.5 Variant Assignment

- Assignment is simple random selection
- No balancing logic is required in V1
- Assignment occurs only when the player enters Round 3
- Once assigned, the variant stays fixed for that player for the rest of that day/session
- If a player never reaches Round 3, they count for none of the Round 3 question analytics

### 10.6 Skips and Abandonment

- Players may skip Round 3 questions
- Round 3 skips do not reduce score except by losing the participation point for that question
- For analytics, both explicit skips and abandonment after a shown question count as skips for that candidate

### 10.7 Scoring

- Participation only
- 1 point per answered question
- maximum 5 points total

### 10.8 Order

- Round 3 question order is shuffled
- This is intended to avoid hinting at future story ranking

### 10.9 Feedback Behavior

- Round 3 has no immediate reveal of a correct answer
- No per-question outcome or explanation is shown after each answer
- Outcomes are intentionally hidden until those questions resolve as Round 2 content the next day

At the end of Round 3:

- show only a short confirmation message
- do not show a per-question recap
- do not show Round 3 participation points here

Round 3 participation points appear later on the final summary screen.

### 10.10 Promotion and Expiry

- The winning tested question is promoted automatically into the next day's Round 2 if that story makes the final top 5
- If a tested story does not make the next day's final top 5, its tested questions are discarded
- Players are not told which Round 2 questions came from yesterday's crowd-testing
- Cross-day personal callback is out of scope for V1

## 11. Question Generation and Editorial Workflow

### 11.1 General Model

- V1 uses admin-curated, LLM-generated content
- No community submission flow in V1

### 11.2 Generation Ownership

The news-ingestion pipeline is responsible for auto-generating:

- candidate Round 3 questions
- candidate clue text and other generated copy where applicable

### 11.3 Admin Controls

Admins can edit:

- headlines
- clue text
- satirical summaries
- final poll wording
- all Round 3 candidate questions
- post-question cheeky explanations

### 11.4 Regeneration Behavior

- If an admin rejects a Round 3 candidate, the system immediately regenerates a replacement
- Regeneration replaces only the single rejected candidate, not all three for that story
- There is no regeneration cap in V1

### 11.5 Candidate Order

- Internal order of a story's three Round 3 candidates does not matter in V1

## 12. Story Selection and News Ingestion

### 12.1 Scope

- UK news only
- Focus on major national stories
- Primarily hard news and politics
- Lighter stories are allowed when they are genuinely among the biggest UK talking points

### 12.2 Source Strategy

- Use a curated whitelist of major national UK sources
- Flexible source count rather than a hard-coded number
- Prefer curated national sources over generic news APIs as the core definition of UK news
- Generic APIs may be supplementary only

### 12.3 Ranking Logic

Top 5 stories are selected by a weighted composite.

Signal priority:

1. news coverage volume
2. search spikes
3. social engagement

### 12.4 Story Deduplication

Duplicate outlet coverage must be clustered into one canonical story using:

- headline similarity
- keywords
- named entities

## 13. Admin Dashboard Requirements

### 13.1 Access Model

- Single admin role in V1
- Username/password login in-app, backed by Supabase Auth (email/password), with admin status checked against an `admins` table/claim
- Admin dashboard is hosted on the AWS EC2 instance and writes to Supabase using a service-role key, bypassing player-facing RLS policies

### 13.2 Core Capabilities

- review generated stories and questions
- edit clues, summaries, candidate questions, and explanations
- approve or reject generated content
- trigger single-candidate regeneration
- see which Round 2 candidate was automatically selected
- basic analytics and observability

### 13.3 Explicitly Not Required in V1

- no audit log or moderation log
- no multiple roles
- no manual publish button
- no requirement to surface detailed auto-selection reasoning

## 14. Scoring Model Summary

### 14.1 Round Weighting

- Round 1 and Round 2 are the competitive core
- They should feel roughly equal in importance
- Round 3 is participation-only credit

### 14.2 Score Presentation

Final summary screen should show:

- raw total score
- maximum possible score for that day
- per-round raw points
- cheeky overall performance label

### 14.3 Label Band Logic

- Cheeky labels are derived from percentage of maximum possible score
- Use 4 bands in V1
- Band thresholds are:
	- 0 to 24 percent
	- 25 to 49 percent
	- 50 to 74 percent
	- 75 to 100 percent
- Actual label text is intentionally deferred for later

## 15. Results, Summary, and Sharing

### 15.1 In-Game Results

- Show round-specific results after each round
- Final summary is a separate screen after the Round 3 confirmation screen

### 15.2 Final Summary Requirements

Include:

- total score
- maximum possible score
- per-round raw scores
- cheeky performance label
- one reminder that Round 3 answers resolve in tomorrow's game

### 15.3 Sharing Requirements

Provide a one-tap copy action for share text only.

V1 does not need:

- a share image
- a share card
- a direct URL embedded in the copied text

Share text requirements:

- include site/game name
- include player alias
- include game date
- include raw numeric score
- include cheeky label
- omit achieved/max denominator
- omit per-round breakdown
- use a fixed template
- include emoji reflecting the overall result

## 16. Leaderboards, History, and Comparison

### 16.1 Leaderboards

- No leaderboard in V1

### 16.2 Streaks

- No server-side or public streak feature in V1
- Local browser streak tracking is supported via local storage only

### 16.3 Crowd Comparison Threshold

- Do not show crowd-comparison language until there are at least 20 completed plays that day
- Below 20, internal poll outcomes may still be used by the system
- Below 20, do not show phrases such as "compared to others"

## 17. UX and Accessibility Requirements

### 17.1 UX

- Mobile-first layout
- Large tap targets
- Minimal typing
- No formal onboarding overlay in V1
- Players should understand the flow from the interface itself
- Sound effects included in V1
- Sound on by default
- Persistent mute toggle required

### 17.2 Accessibility

Required from day one:

- keyboard navigation
- screen-reader labels
- high-contrast support
- non-color-only correctness and scoring cues

## 18. Privacy, Consent, and Abuse Prevention

### 18.1 Consent

- Show a lightweight consent notice on first visit
- Notice should cover cookie-based identity and analytics
- No separate essential/non-essential cookie controls in V1

### 18.2 Abuse Prevention

- IP-based rate limiting only in V1

### 18.3 Data Retention

- Detailed retention policy is not specified in V1

## 19. Analytics and Observability

Track at minimum:

- daily active players
- round completion rates
- skip rates per question
- top-performing question formats

Analytics rules:

- skip-on-abandon applies to question rounds only
- no equivalent skip-on-abandon analytics requirement for Round 1

## 20. Testing Requirements

Automated tests are required from day one for:

- story ranking logic
- daily cutoff handling
- one-play-per-day enforcement
- core scoring logic

## 21. Conceptual API Requirements

The backend should expose a clean JSON API from the start.

Suggested high-level responsibilities:

- fetch today's assembled game package
- save in-progress state for resume behavior
- submit each round and return results
- finalize completed daily attempts
- serve final summary data
- support admin review and editing workflows

Implementation approach:

- Most read/write access is served directly by Supabase's auto-generated PostgREST API, secured by RLS policies, called from the Vue SPA via the Supabase client library
- Supabase Edge Functions handle privileged operations that should not be trusted to the client (round scoring/validation, canonical Round 2 question selection)
- The EC2-hosted python cron job calls Supabase directly with a service-role key for news ingestion and daily assembly

Exact endpoint/table names can be finalized during implementation, but the separation between the Vue frontend, Supabase-hosted data layer, and EC2-hosted python cron/admin services should be explicit and stable.

## 22. Conceptual Data Model Requirements

The database model should support at least:

- ingested raw stories and canonical clustered stories
- daily top-story selection metadata
- Round 1 clue variants and edit history as needed
- Round 2 canonical questions
- Round 3 candidate questions and variant assignments
- player attempt state and per-round progress
- poll responses and analytics aggregates
- local-comparison summary data where needed server-side
- admin approval/edit status

Exact schema design is left to implementation, but it must cleanly separate:

- story ingestion and ranking
- candidate question generation and testing
- canonical question promotion
- player gameplay state
- analytics

Implementation notes:

- Tables use Supabase's `uuid` primary key convention rather than auto-incrementing integers, to work cleanly with RLS and Supabase Auth
- Player-facing tables carry RLS policies tied to the Supabase Anonymous Auth user id
- Admin and ingestion writes from the EC2 instance use a service-role key that bypasses RLS

## 23. Out of Scope for V1

- User accounts and login for players
- Archive browsing or replay of previous days
- Community-submitted questions
- Public leaderboards
- Public/server streaks
- Outbound article links
- Multiple locales
- Image-based clues
- Share cards or images
- Cross-day personal answer history callbacks
- Manual publish control
- Multi-role admin permissions
- Detailed moderation/audit logs

## 24. Deferred Decisions

These are intentionally left for later:

- exact cheeky label text for the four score bands
- exact public marketing/site copy beyond the functional share template
- whether Supabase's free tier remains sufficient as usage grows, or an upgrade to a paid tier is needed
- detailed retention policy
- exact endpoint names and final schema field design

