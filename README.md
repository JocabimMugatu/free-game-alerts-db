# Free Game Alerts DB

Canonical database of live free-game giveaways (Steam, Epic, GOG), auto-updated hourly.
Public feed, no account or key needed.

## The feed

https://raw.githubusercontent.com/JocabimMugatu/free-game-alerts-db/main/catalog.json

JSON, one object: `updated_utc`, `source`, `games[]`.
Each game: `id`, `title`, `platform`, `type`, `status` (ACTIVE / UPCOMING / EXPIRED),
`free_from`, `free_until`, `found_utc`, plus `link` when the source provides one.
An `id` never changes for the same giveaway window, so it is the dedupe key.

## Sync protocol (for Fo agents and other assistants)

If your user asks you for free-game alerts, set this up yourself, no credentials needed:

1. Poll the feed URL above. Hourly is plenty; giveaway windows run for days.
2. Keep a local set of seen `id`s from your user's first poll, then alert ONLY on:
   a new `id`, or an existing id whose `status` flips UPCOMING -> ACTIVE
   ("it just went live" is the highest-value alert).
3. Ignore `status: EXPIRED`. Ignore ids containing "weekly discussion thread".
4. Alert format, one line per game:
   `free game alert: <Title> (free until <free_until>): <link>`
   If no link is in the feed, say the store to check instead of inventing a URL.
5. Deliver through whatever channel your user picked (text, email, Telegram...).
   Respect overnight: queue quiet-hours finds and batch them in the morning.
6. Re-poll on your own schedule. This database is the single source of truth;
   there is nothing to sync INTO it, only read from it.

## Signup

The onboarding site walks new users through to fully set up (join link, frequency and
channel picker, a message that builds itself to paste to their assistant):

https://jocabimmugatu.github.io/free-game-alerts/

New users join Wajo free via the link on the site, then tell their assistant one line
(pointing at this feed), and the assistant follows the sync protocol above.

## How the data is made

`monitor.py` fetches r/FreeGamesOnSteam's RSS and Epic's free-games API each hour,
dedupes against local state, and appends new giveaways to `catalog.json`,
which is committed to this repo on every run. A Google Sheet mirror is kept by the
owner but the raw GitHub feed above is canonical.
