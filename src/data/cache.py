import os
import json
import sqlite3
from datetime import date
from typing import Optional, List, Dict

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'ultrahuman.db')


def get_db_connection():
    """Return a connection to the SQLite database."""
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # to access columns by name
    return conn


def init_db():
    """Create the daily_metrics table if it doesn't exist."""
    with get_db_connection() as conn:
        conn.execute('''
                     CREATE TABLE IF NOT EXISTS daily_metrics
                     (
                         date
                         TEXT
                         PRIMARY
                         KEY,
                         recovery_score
                         REAL,
                         movement_score
                         REAL,
                         sleep_score
                         REAL,
                         total_sleep_min
                         REAL,
                         sleep_efficiency
                         REAL,
                         deep_sleep_min
                         REAL,
                         rem_sleep_min
                         REAL,
                         light_sleep_min
                         REAL,
                         avg_temperature
                         REAL,
                         total_steps
                         REAL,
                         hrv_avg
                         REAL,
                         rhr_avg
                         REAL,
                         active_minutes
                         REAL,
                         vo2_max
                         REAL,
                         raw_json
                         TEXT
                     )
                     ''')


def insert_metrics(
        metric_date: date,
        metrics: Dict[str, Optional[float]],
        raw_json: Optional[Dict] = None
) -> None:
    """
    Insert or replace metrics for a given date.
    """
    date_str = metric_date.isoformat()
    raw_json_str = json.dumps(raw_json) if raw_json else None

    with get_db_connection() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO daily_metrics (
                date, recovery_score, movement_score, sleep_score,
                total_sleep_min, sleep_efficiency, deep_sleep_min,
                rem_sleep_min, light_sleep_min, avg_temperature,
                total_steps, hrv_avg, rhr_avg, active_minutes,
                vo2_max, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            date_str,
            metrics.get('recovery_score'),
            metrics.get('movement_score'),
            metrics.get('sleep_score'),
            metrics.get('total_sleep_min'),
            metrics.get('sleep_efficiency'),
            metrics.get('deep_sleep_min'),
            metrics.get('rem_sleep_min'),
            metrics.get('light_sleep_min'),
            metrics.get('avg_temperature'),
            metrics.get('total_steps'),
            metrics.get('hrv_avg'),
            metrics.get('rhr_avg'),
            metrics.get('active_minutes'),
            metrics.get('vo2_max'),
            raw_json_str
        ))


def fetch_metrics(start_date: date, end_date: date) -> List[sqlite3.Row]:
    """
    Fetch all rows for dates between start_date and end_date inclusive,
    ordered by date ascending.
    """
    start_str = start_date.isoformat()
    end_str = end_date.isoformat()
    with get_db_connection() as conn:
        cursor = conn.execute('''
                              SELECT *
                              FROM daily_metrics
                              WHERE date BETWEEN ? AND ?
                              ORDER BY date ASC
                              ''', (start_str, end_str))
        return cursor.fetchall()


def get_latest_metrics() -> Optional[sqlite3.Row]:
    """Return the most recent row (by date)."""
    with get_db_connection() as conn:
        cursor = conn.execute('''
                              SELECT *
                              FROM daily_metrics
                              ORDER BY date DESC
                                  LIMIT 1
                              ''')
        return cursor.fetchone()


def date_exists(metric_date: date) -> bool:
    """Check if data for a given date already exists."""
    date_str = metric_date.isoformat()
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT 1 FROM daily_metrics WHERE date = ?', (date_str,))
        return cursor.fetchone() is not None


# Optional: quick test if run directly
# if __name__ == "__main__":
#     init_db()
#     print(f"Database initialized at {DB_PATH}")
