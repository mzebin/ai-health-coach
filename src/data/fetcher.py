# src/data/fetcher.py
import time
from datetime import date, timedelta

from src.api.client import fetch_daily_metrics, get_token, get_email
from src.data.parser import parse_daily_metrics
from src.data.cache import insert_metrics, date_exists


def fetch_and_store_day(target_date: date, token: str, email: str = None, force: bool = False) -> bool:
    """Fetch data for a single day and store in cache if not already present."""
    if not force and date_exists(target_date):
        return True  # already exists, skip
    try:
        response = fetch_daily_metrics(target_date, token, email)
        metrics = parse_daily_metrics(response)
        insert_metrics(target_date, metrics, raw_json=response)
        return True
    except Exception:
        return False


def fetch_recent_days(days: int = 7, force: bool = False, delay: float = 0.5):
    """
    Fetch the last `days` days (excluding today) and store in cache.
    Returns (success_count, total_days)
    """
    token = get_token()
    email = get_email()
    today = date.today()
    success = 0
    total = 0
    for i in range(1, days + 1):
        day = today - timedelta(days=i)
        ok = fetch_and_store_day(day, token, email, force)
        if ok:
            success += 1
        total += 1
        time.sleep(delay)
    return success, total
