#!/usr/bin/env python
"""
Entry point for AI Health Coach.
Runs the chat loop and optionally fetches recent data if cache is empty.
"""

from datetime import date, timedelta
from src.chatbot.cli_chat import main as chat_main
from src.data.cache import get_latest_metrics, init_db
from src.api.client import fetch_daily_metrics, get_token, get_email
from src.data.parser import parse_daily_metrics
from src.data.cache import insert_metrics


def ensure_data():
    """Check if cache has data; if not, fetch last 7 days."""
    init_db()
    latest = get_latest_metrics()
    if not latest:
        print("No data found in cache. Fetching last 7 days of data...")
        token = get_token()
        email = get_email()
        today = date.today()
        for i in range(1, 8):
            day = today - timedelta(days=i)
            try:
                print(f"Fetching {day}...")
                resp = fetch_daily_metrics(day, token, email)
                metrics = parse_daily_metrics(resp)
                insert_metrics(day, metrics, raw_json=resp)
                print(f"Stored {day}")
            except Exception as e:
                print(f"Error fetching {day}: {e}")
        print("Initial data fetch complete.")


if __name__ == "__main__":
    ensure_data()
    chat_main()