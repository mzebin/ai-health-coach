import os
import re
import sys
from datetime import date, timedelta
from typing import Optional, Tuple, Union

import dateparser

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.chatbot.templates import METRIC_SYNONYMS

# Build reverse mapping: all synonyms -> canonical metric name
SYNONYM_TO_METRIC = {}
for canonical, synonyms in METRIC_SYNONYMS.items():
    for syn in synonyms:
        SYNONYM_TO_METRIC[syn.lower()] = canonical

# Add more synonyms manually (optional)
EXTRA_SYNONYMS = {
    'recovery_score': ['recovery level', 'readiness'],
    'movement_score': ['activity score', 'movement level'],
    'sleep_score': ['sleep quality', 'sleep rating'],
    'total_sleep_min': ['sleep duration', 'time asleep', 'hours of sleep'],
    'sleep_efficiency': ['sleep efficiency percentage'],
    'deep_sleep_min': ['deep sleep duration'],
    'rem_sleep_min': ['rem duration'],
    'light_sleep_min': ['light sleep duration'],
    'avg_temperature': ['skin temp', 'body temp'],
    'total_steps': ['step count'],
    'hrv_avg': ['heart rate variability', 'hrv'],
    'rhr_avg': ['resting heart rate', 'night rhr'],
    'active_minutes': ['active time'],
    'vo2_max': ['vo2', 'cardio fitness'],
}
for canonical, extras in EXTRA_SYNONYMS.items():
    for syn in extras:
        SYNONYM_TO_METRIC[syn.lower()] = canonical

def extract_metric(query: str) -> Optional[str]:
    """Extract metric name from query."""
    query_lower = query.lower()
    for synonym, canonical in SYNONYM_TO_METRIC.items():
        if synonym in query_lower:
            return canonical
    return None

def parse_date_str(date_str: str, today: date) -> Optional[date]:
    """Parse a date string like '2025-02-20' or 'yesterday' or 'last monday'."""
    parsed = dateparser.parse(date_str, settings={'RELATIVE_BASE': today})
    if parsed:
        return parsed.date()
    # Fallback to explicit ISO format if dateparser fails
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        return None

def extract_time_range(query: str, today: date = None) -> Optional[Tuple[str, Union[Tuple[date, date], int, date]]]:
    """
    Extract time range expression from query.
    Returns a tuple (range_type, value) where range_type can be:
        - 'today', 'yesterday', 'single_date': value = date
        - 'last_n_days': value = number of days
        - 'explicit_range': value = (start_date, end_date)
        - 'since_date': value = start_date (end is today-1? or today? We'll decide)
        - 'last_week', 'last_month' (handled as last_n_days with 7 or 30)
        - 'this_week', 'this_month' (range from start of week/month to today)
    """
    if today is None:
        today = date.today()
    query_lower = query.lower()

    # Check for explicit date range: from X to Y or between X and Y
    patterns = [
        r'from (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})',
        r'between (\d{4}-\d{2}-\d{2}) and (\d{4}-\d{2}-\d{2})',
    ]
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            start_str, end_str = match.group(1), match.group(2)
            start = parse_date_str(start_str, today)
            end = parse_date_str(end_str, today)
            if start and end:
                return ('explicit_range', (start, end))

    # Check for "since DATE" (from that date to yesterday)
    pattern = r'since (\d{4}-\d{2}-\d{2})'
    match = re.search(pattern, query_lower)
    if match:
        start_str = match.group(1)
        start = parse_date_str(start_str, today)
        if start:
            end = today - timedelta(days=1)  # up to yesterday
            return ('explicit_range', (start, end))

    # Check for "last X days" / "past X days" / "previous X days"
    pattern = r'(last|past|previous) (\d+) days?'
    match = re.search(pattern, query_lower)
    if match:
        days = int(match.group(2))
        return ('last_n_days', days)

    # Check for "last week" / "last month"
    if 'last week' in query_lower:
        return ('last_n_days', 7)
    if 'last month' in query_lower:
        return ('last_n_days', 30)

    # Check for "this week" / "this month"
    if 'this week' in query_lower:
        start = today - timedelta(days=today.weekday())  # Monday of this week
        return ('explicit_range', (start, today))
    if 'this month' in query_lower:
        start = today.replace(day=1)
        return ('explicit_range', (start, today))

    # Check for single date references
    single_date_terms = ['today', 'yesterday']
    for term in single_date_terms:
        if term in query_lower:
            if term == 'today':
                return ('single_date', today)
            elif term == 'yesterday':
                return ('single_date', today - timedelta(days=1))

    # Try to parse any date-like string (e.g., "2025-02-20" alone)
    iso_match = re.search(r'(\d{4}-\d{2}-\d{2})', query_lower)
    if iso_match:
        d = parse_date_str(iso_match.group(1), today)
        if d:
            return ('single_date', d)

    return None

def resolve_time_range(range_info: Tuple, today: date = None) -> Tuple[date, date]:
    """
    Convert range_info into actual start_date and end_date (inclusive).
    """
    if today is None:
        today = date.today()
    range_type, value = range_info

    if range_type == 'single_date':
        return (value, value)
    elif range_type == 'last_n_days':
        end = today - timedelta(days=1)  # up to yesterday
        start = end - timedelta(days=value - 1)
        return (start, end)
    elif range_type == 'explicit_range':
        return value
    else:
        raise ValueError(f"Unknown range type: {range_type}")