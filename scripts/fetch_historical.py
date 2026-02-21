#!/usr/bin/env python
import argparse

from src.data.fetcher import fetch_recent_days

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=90)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    success, total = fetch_recent_days(args.days, force=args.force)
    print(f"Fetched {success}/{total} days successfully.")

if __name__ == '__main__':
    main()