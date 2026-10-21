# Free Game Alerts DB

Canonical, machine-readable database of live free-game giveaways (Steam, Epic Games Store, more coming).

- `catalog.json`: full catalog. Each game has `id`, `title`, `platform`, `type`, `status`, `free_from` / `free_until` (when applicable), and `found_utc`.
- `state.json`: dedupe ledger used by the monitor (which items are already known).
- `monitor.py`: the scraper that populates this catalog, run hourly.

Agents: subscribe by polling `catalog.json` and alerting on rows whose `id` is new or whose `status` flips to `ACTIVE`. Raw URL: https://raw.githubusercontent.com/JocabimMugatu/free-game-alerts-db/main/catalog.json

Owner: Kevin Newman. Synced hourly from the Free Game Alerts engine.
