- Added global `processed_count` variable at module level in `extract_sessions.py` to track number of processed clients across the script.
- Declared `global processed_count` inside `extract_client_sessions` so the summary print in the `__main__` block has access to the correct value.
- Updated green cell parsing in `extract_sessions.py` to detect numeric-only text and ignore it; only non-numeric strings are now kept for the `extra` list.
- Added handling for green cells without accompanying dates: these are now counted as additional paid sessions (undated) and therefore reduce the `remaining` sessions figure.
  * Introduced `undated_paid_count` per client.
  * Stats and on-screen summary now include these undated paid sessions. 