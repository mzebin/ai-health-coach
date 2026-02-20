#!/usr/bin/env python
"""
Script to fetch historical daily metrics from Ultrahuman API and populate the SQLite cache.
"""
import sys
import os
import time
from datetime import date, timedelta
import argparse

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.api.client import fetch_daily_metrics, get_token, get_email
from src.data.parser import parse_daily_metrics
from src.data.cache import init_db, insert_metrics, date_exists


def fetch_and_store_day(target_date: date, token: str, email: str = None, force: bool = False):
    """Fetch data for a single day and store in cache if not already present."""
    if not force and date_exists(target_date):
        print(f"Data for {target_date} already exists. Skipping (use --force to overwrite).")
        return True

    try:
        print(f"Fetching {target_date}...")
        response = fetch_daily_metrics(target_date, token, email)
        metrics = parse_daily_metrics(response)
        insert_metrics(target_date, metrics, raw_json=response)
        print(f"Stored {target_date}: {metrics}")
        return True
    except Exception as e:
        print(f"Error fetching {target_date}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Fetch historical Ultrahuman data.')
    parser.add_argument('--days', type=int, default=90, help='Number of past days to fetch (default: 90)')
    parser.add_argument('--start-date', type=str,
                        help='Start date (YYYY-MM-DD). If not provided, calculate from --days back from today.')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD). Default: yesterday.')
    parser.add_argument('--force', action='store_true', help='Force re-fetch and overwrite existing data.')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between requests in seconds (default: 0.5)')
    args = parser.parse_args()

    # Resolve date range
    today = date.today()
    if args.end_date:
        end = date.fromisoformat(args.end_date)
    else:
        end = today - timedelta(days=1)  # yesterday, because today might be incomplete

    if args.start_date:
        start = date.fromisoformat(args.start_date)
    else:
        start = end - timedelta(days=args.days - 1)  # inclusive count

    if start > end:
        print("Error: start date must be <= end date.")
        sys.exit(1)

    # Initialize database
    init_db()
    print(f"Database initialized at data/ultrahuman.db")

    # Get credentials
    try:
        token = get_token()
        email = get_email()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Fetching data from {start} to {end} (total {(end - start).days + 1} days)")

    current = start
    success_count = 0
    while current <= end:
        ok = fetch_and_store_day(current, token, email, args.force)
        if ok:
            success_count += 1
        current += timedelta(days=1)
        time.sleep(args.delay)

    print(f"Done. Successfully processed {success_count} days.")


if __name__ == '__main__':
    main()
