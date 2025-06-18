- Added global `processed_count` variable at module level in `extract_sessions.py` to track number of processed clients across the script.
- Declared `global processed_count` inside `extract_client_sessions` so the summary print in the `__main__` block has access to the correct value.
- Updated green cell parsing in `extract_sessions.py` to detect numeric-only text and ignore it; only non-numeric strings are now kept for the `extra` list.
- Added handling for green cells without accompanying dates: these are now counted as additional paid sessions (undated) and therefore reduce the `remaining` sessions figure.
  * Introduced `undated_paid_count` per client.
  * Stats and on-screen summary now include these undated paid sessions.
- Replaced old `remaining` logic (package rounding) with exact count of undated paid sessions.
  * Added `paid_used` and `paid_remaining` fields in stats for clarity.
  * Updated summary log to reflect new breakdown.
- `save_to_json` now converts `paid` and `unpaid` lists into single comma-separated strings before writing the JSON, making each client's dates appear on one line.
- Added `sessions_statistics.py`: read-only utility to compute aggregate stats (total clients/sessions, ratios, top unpaid, top remaining, extra notes count) from the generated JSON output.
- Makefile: added `stats` target to run `sessions_statistics.py` and updated help.
- Added `_is_numeric_string` helper in `extract_sessions.py` to skip rows where the detected client name is a pure number (e.g., `200`, `230.0`). This prevents numeric strings from being treated as client names.
- Improved `determine_year_from_date` heuristic: now checks if the day/month are > threshold_days (default 183) in past or future relative to reference date, preventing old dates like 10.06.2024 from being mis-labelled as 2025.
- `enhance_session_dates` refined: starts timeline in previous year, bumps forward when needed, and if the entire timeline is still one year and ends within 3 months of today it shifts to current year—fixing mixed-year edge cases like Adriana Bazarea.
- Switched to dynamic `CURRENT_DATE_REF` (system today) for all date calculations and ensured no session date is pushed into the future; if a bumped year exceeds today it is reduced by 1.
- Extraction now reads numeric value immediately to the left of the first green cell per client as `previous_completed`; this is added to the `paid_used` count and reflected in summaries. 