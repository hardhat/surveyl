# Surveyle.co.uk - a current events daily game

Overview

Inspired by the irreverent, statistically driven humor of 8 Out of 10 Cats, this proposal outlines a daily web game where players navigate current events through the lens of public opinion, polling data, and witty deduction.
1. Core Gameplay Loop

The game delivers a daily challenge structured into three distinct comedic/analytical rounds:

    Round 1: "What Are You Going On About?" (Top Stories Identification)

        Mechanic: Players are presented with scrambled headlines, satirical summaries, or visual clues corresponding to the top 5 trending news stories of the day.

        Goal: Select and rank the correct top 5 stories in order of popularity/impact.

    Round 2: "The Public Slag" (Poll Result Estimation)

        Mechanic: Players face specific poll questions derived from yesterday’s top stories (e.g., "What percentage of the public admits to falling asleep during a work Zoom call this week?").

        Goal: Guess the percentage or choose the top survey results from the previous day's public vote using a slider or multiple-choice interface.

    Round 3: "Have I Got Stats For You" (Today's Survey Participation)

        Mechanic: Players answer the newly generated survey questions for tomorrow's game based on today's top stories.

        Goal: Contribute to the crowd-sourced dataset that drives the next day's scoring engine.

2. Story Popularity & Metric Review

To dynamically select the top 5 news stories daily, the backend runs a scoring algorithm weighing multiple objective metrics:

    News Aggregator APIs (e.g., NewsAPI, GNews, or MediaStack): Tracks volume of coverage and frequency of keywords across major global and regional outlets.

    Social Velocity Score (Reddit/X/Bluesky APIs): Measures the rate of engagement (upvotes, reposts, comment velocity) within a 24-hour sliding window.

    Search Trend Multiplier (Google Trends API): Weights stories by sudden spikes in search volume to filter out slow-burn news in favor of viral talking points.

    Composite Popularity Formula:
    Score=(w1​⋅Media Volume)+(w2​⋅Social Velocity)+(w3​⋅Search Spike)

3. Question Generation Engine

For each of the top 5 stories selected by the popularity metric, the system generates targeted survey questions. To balance automation with editorial quality, two workflows are proposed:
Version A: The Crowd-Sourced Approach

    Workflow:

        Users submit potential survey questions while playing Round 3 or via an open suggestion portal.

        Submitted questions enter a Moderation & Voting Queue where players upvote or downvote community submissions.

        The system automatically selects the top-rated question per story that crosses a minimum engagement threshold.

    Pros: Highly organic, community-driven humor; endlessly scalable.

    Cons: Requires spam filtering, moderation tools, and content safeguards.

Version B: The Admin / AI-Assisted Approach

    Workflow:

        The backend fetches the raw article text and summaries via a media backend API.

        An LLM or content editor generates 3 potential multiple-choice or percentage-based questions tailored to the absurdity or debate surrounding the story.

        Admins review and approve questions through an internal dashboard (CMS) before they go live.

    Pros: Consistent quality control, safer brand tone, perfectly timed for daily releases.

    Cons: Higher administrative overhead or reliance on external LLM API stability.

## Deployment

Everything server-side lives on a single EC2 host (`ubuntu@surveyle.co.uk`, Ubuntu, Apache2 + PHP + Python) at `/opt/surveyle`, alongside a Supabase project. There are two independently deployable pieces:

- `infra/ec2/ingestion/` -- Python cron pipeline (news ingestion, ranking, daily assembly). Runs out of `/opt/surveyle/venv` per `infra/ec2/crontab`.
- `infra/ec2/admin/` -- plain-PHP admin dashboard (no framework/Composer deps). Apache serves `infra/ec2/admin/public` as its document root/alias; `src/`, `tests/`, and `templates/` sit outside the web root and are never directly reachable over HTTP.

Both read secrets from `/etc/surveyle/surveyle.env` (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `OPENAI_API_KEY`). Keep that file to *only* those four keys -- it's readable by both the `ubuntu` user (cron) and, via the `surveyle` group, the `www-data` user (Apache/PHP), so treat any addition to it as a deliberate, audited change.

### Local staging before deploying

Always run both test suites locally first, and use the PHP built-in server to click through the admin UI by hand before touching the production host:

```bash
# Python ingestion pipeline
source venv/bin/activate && python -m pytest infra/ec2/tests/ -q

# PHP admin dashboard
(cd infra/ec2/admin && phpunit)

# Manually click through the admin UI against a local/dev Supabase project:
#   cp /path/to/a/dev/surveyle.env /tmp/surveyle.env   # dev project's keys, never prod's
#   sudo mkdir -p /etc/surveyle && sudo cp /tmp/surveyle.env /etc/surveyle/surveyle.env
php -S localhost:8080 -t infra/ec2/admin/public
# then open http://localhost:8080/login.php
```

Only proceed to the deploy steps below once both suites are green and (for admin dashboard changes) you've smoke-tested the affected pages locally.

### Deploying

`/opt/surveyle` on the EC2 host is a real git checkout of this repo, pulled over SSH using a **read-only** deploy key (`~/.ssh/surveyle_deploy_ed25519` on the host, added under the repo's Settings -> Deploy keys with "Allow write access" left unchecked) via the `github-surveyle` SSH config alias. That key can only fetch this one repo -- it can't push, and it isn't valid for any other GitHub repo.

```bash
# 1. Make sure both test suites pass locally (see "Local staging" above), commit,
# and push to origin/main -- deploys always pull from origin/main, never from a
# local working tree.

# 2. Pull the latest commit onto the server.
ssh ubuntu@surveyle.co.uk 'cd /opt/surveyle && git pull --ff-only origin main'

# 3. Only if requirements.txt changed:
ssh ubuntu@surveyle.co.uk 'cd /opt/surveyle && venv/bin/pip install -q -r infra/ec2/requirements.txt'

# 4. Re-run both suites on the server itself as a final sanity check.
ssh ubuntu@surveyle.co.uk '
  cd /opt/surveyle &&
  venv/bin/python -m pytest infra/ec2/tests/ -q &&
  (cd infra/ec2/admin && phpunit)
'

# 5. Apache config only needs touching when infra/ec2/admin/surveyle-admin.conf
# (or the Alias block in /etc/apache2/sites-available/surveyle.co.uk-le-ssl.conf)
# changes -- otherwise step 2 alone is enough, since PHP is interpreted directly
# from the pulled files and Apache doesn't need a reload for code-only changes.
ssh ubuntu@surveyle.co.uk 'sudo apache2ctl configtest && sudo systemctl reload apache2'
```

`git pull --ff-only` deliberately refuses instead of merging/rebasing if the server's checkout ever diverges from origin (e.g. someone hand-edited a file on the host) -- investigate and reconcile manually rather than forcing it. The one file intentionally outside this checkout is the standalone `/opt/surveyle/heartbeat.py` + its own crontab entry, both untracked leftovers from before this repo's `infra/ec2/` layout existed; leave them alone unless asked to migrate them.

The admin dashboard is currently path-mounted at `https://surveyle.co.uk/admin/` (see the `Alias` block added to `surveyle.co.uk-le-ssl.conf`) since only a `surveyle.co.uk` TLS cert exists. `infra/ec2/admin/surveyle-admin.conf` is the reference vhost for moving it to its own `admin.surveyle.co.uk` subdomain once that DNS record and cert exist.

