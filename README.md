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

4. Technical Architecture (PHP + MySQL + Media Backend)
Database Schema (MySQL)

    stories Table

        id (INT, PK)

        title (VARCHAR)

        url (VARCHAR)

        popularity_score (FLOAT)

        publish_date (DATE)

    questions Table

        id (INT, PK)

        story_id (INT, FK)

        question_text (TEXT)

        source_type (ENUM: 'admin', 'crowdsourced')

        status (ENUM: 'pending', 'approved', 'rejected')

    poll_responses Table

        id (INT, PK)

        question_id (INT, FK)

        user_ip_or_session (VARCHAR)

        answer_value (VARCHAR / INT)

        created_at (TIMESTAMP)

    user_scores Table

        id (INT, PK)

        user_id (INT, FK)

        game_date (DATE)

        round_1_score (INT)

        round_2_score (INT)

        total_score (INT)

Backend (PHP) & Media API Integration

    Cron Job / Scheduler: Runs a daily PHP script (fetch_news.php) that queries external media APIs (e.g., NewsAPI, RSS feeds) to ingest the top stories and calculate the popularity metric.

    RESTful Endpoints:

        GET /api/daily-game: Serves today's 5 stories and active poll questions.

        POST /api/submit-round: Validates user guesses against stored results and records scores.

        POST /api/submit-question: Handles user-generated questions for the crowd-sourced queue.

    Admin Dashboard: A lightweight PHP panel built with a modern CSS framework (e.g., Tailwind) for reviewing queued questions, overriding scores, and viewing daily player analytics.