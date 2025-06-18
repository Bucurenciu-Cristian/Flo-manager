#!/usr/bin/env python3
"""sessions_statistics.py

Generate quick aggregate statistics from the JSON output produced by
`extract_sessions.py` (e.g. `all_clients_sessions_enhanced.json`).

The script is **read-only** – it never modifies the JSON file.

USAGE
-----
$ python sessions_statistics.py all_clients_sessions_enhanced.json

If no filename is provided it defaults to the path above (in the same folder).
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Dict, Tuple, List


def load_clients(path: Path) -> Dict[str, dict]:
    """Load the JSON and return the dict of clients."""
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("clients", {})


def aggregate_stats(clients: Dict[str, dict]):
    """Compute useful summary statistics from client data."""
    total_clients = len(clients)

    total_used = total_remaining = total_unpaid = total_sessions = 0
    clients_with_extra = 0

    unpaid_counter: List[Tuple[str, int]] = []
    remaining_counter: List[Tuple[str, int]] = []

    for name, info in clients.items():
        stats = info.get("stats", {})
        used = stats.get("paid_used", 0)
        remaining = stats.get("paid_remaining", 0)
        unpaid = stats.get("unpaid", 0)
        tot = stats.get("total", 0)

        total_used += used
        total_remaining += remaining
        total_unpaid += unpaid
        total_sessions += tot

        if unpaid:
            unpaid_counter.append((name, unpaid))
        if remaining:
            remaining_counter.append((name, remaining))
        if "extra" in info:
            clients_with_extra += 1

    unpaid_counter.sort(key=lambda x: x[1], reverse=True)
    remaining_counter.sort(key=lambda x: x[1], reverse=True)

    return {
        "total_clients": total_clients,
        "total_sessions": total_sessions,
        "total_used": total_used,
        "total_remaining": total_remaining,
        "total_unpaid": total_unpaid,
        "clients_with_extra": clients_with_extra,
        "top_unpaid": unpaid_counter[:5],
        "top_remaining": remaining_counter[:5],
    }


def print_report(stats: dict):
    """Pretty-print the computed statistics."""
    print("\n📊 SESSION OVERVIEW")
    print("=" * 50)
    print(f"👥 Total clients           : {stats['total_clients']}")
    print(f"🗂  Total sessions          : {stats['total_sessions']}")
    print(f"✅ Paid sessions (used)     : {stats['total_used']}")
    print(f"⏳ Paid sessions remaining  : {stats['total_remaining']}")
    print(f"🚩 Unpaid sessions          : {stats['total_unpaid']}")
    print(f"📝 Clients with extra notes : {stats['clients_with_extra']}")

    # Ratios
    if stats['total_sessions']:
        pct_used = stats['total_used'] / stats['total_sessions'] * 100
        pct_remaining = stats['total_remaining'] / stats['total_sessions'] * 100
        pct_unpaid = stats['total_unpaid'] / stats['total_sessions'] * 100
        print("\nPercentage breakdown:")
        print(f"  • Used       : {pct_used:.1f}%")
        print(f"  • Remaining  : {pct_remaining:.1f}%")
        print(f"  • Unpaid     : {pct_unpaid:.1f}%")

    def _print_top(title: str, items: List[Tuple[str, int]]):
        if not items:
            return
        print(f"\n{title} (Top {len(items)})")
        for rank, (name, count) in enumerate(items, 1):
            print(f"  {rank}. {name} — {count}")

    _print_top("🚩 Clients with most unpaid sessions", stats['top_unpaid'])
    _print_top("⏳ Clients with most remaining prepaid sessions", stats['top_remaining'])


def main():
    parser = argparse.ArgumentParser(description="Generate quick statistics from extracted session JSON.")
    parser.add_argument("json_file", nargs="?", default="all_clients_sessions_enhanced.json",
                        help="Path to JSON file produced by extract_sessions.py")
    args = parser.parse_args()

    json_path = Path(args.json_file)
    if not json_path.exists():
        parser.error(f"File not found: {json_path}")

    clients = load_clients(json_path)
    stats = aggregate_stats(clients)
    print_report(stats)


if __name__ == "__main__":
    main() 