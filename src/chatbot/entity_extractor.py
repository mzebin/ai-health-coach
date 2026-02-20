import re
from datetime import date, timedelta
from typing import Optional, Tuple, Union

# Import metric synonyms from templates (or define directly)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.chatbot.templates import METRIC_SYNONYMS

# Build reverse mapping: all synonyms -> canonical metric name
SYNONYM_TO_METRIC = {}
for canonical, synonyms in METRIC_SYNONYMS.items():
    for syn in synonyms:
        SYNONYM_TO_METRIC[syn.lower()] = canonical


def extract_metric(query: str) -> Optional[str]:
    """
    Extract metric name from query by looking for known synonyms.
    Returns canonical metric column name if found, else None.
    """
    query_lower = query.lower()
    for synonym, canonical in SYNONYM_TO_METRIC.items():
        if synonym in query_lower:
            return canonical
    return None


def extract_time_range(query: str, today: date = None) -> Optional[Tuple[str, Union[Tuple[date, date], int]]]:
    """
    Extract time range expression from query.
    Returns a tuple (range_type, value) where range_type is one of:
        - 'today': value = today's date
        - 'yesterday': value = yesterday's date
        - 'last_n_days': value = number of days
        - 'last_week': value = 7 days
        - 'last_month': value = 30 days (approx)
        - 'this_week': value = (start_of_week, today)
        - 'this_month': value = (start_of_month, today)
        - 'explicit_range': value = (start_date, end_date)
    If no time expression is found, returns None.
    """
    if today is None:
        today = date.today()
    query_lower = query.lower()

    # Check for explicit date range: from YYYY-MM-DD to YYYY-MM-DD
    pattern = r'from (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})'
    match = re.search(pattern, query_lower)
    if match:
        start = date.fromisoformat(match.group(1))
        end = date.fromisoformat(match.group(2))
        return ('explicit_range', (start, end))

    # Check for "last X days"
    pattern = r'last (\d+) days?'
    match = re.search(pattern, query_lower)
    if match:
        days = int(match.group(1))
        return ('last_n_days', days)

    # Check for "past X days"
    pattern = r'past (\d+) days?'
    match = re.search(pattern, query_lower)
    if match:
        days = int(match.group(1))
        return ('last_n_days', days)

    # Check for "previous X days"
    pattern = r'previous (\d+) days?'
    match = re.search(pattern, query_lower)
    if match:
        days = int(match.group(1))
        return ('last_n_days', days)

    # Check for "last week"
    if 'last week' in query_lower:
        return ('last_week', 7)

    # Check for "last month"
    if 'last month' in query_lower:
        return ('last_month', 30)

    # Check for "this week"
    if 'this week' in query_lower:
        # Start of current week (Monday)
        start = today - timedelta(days=today.weekday())
        return ('this_week', (start, today))

    # Check for "this month"
    if 'this month' in query_lower:
        start = today.replace(day=1)
        return ('this_month', (start, today))

    # Check for "yesterday"
    if 'yesterday' in query_lower:
        return ('yesterday', today - timedelta(days=1))

    # Check for "today" (or no explicit time -> assume today)
    if 'today' in query_lower or 'current' in query_lower:
        return ('today', today)

    # Default: if no time expression found, we might assume "today" for get_current,
    # but we'll handle that at a higher level. So return None.
    return None


def resolve_time_range(range_info: Tuple[str, Union[Tuple[date, date], int]], today: date = None) -> Tuple[date, date]:
    """
    Convert a range_info tuple into actual start_date and end_date (inclusive).
    """
    if today is None:
        today = date.today()
    range_type, value = range_info

    if range_type == 'today':
        return (value, value)
    elif range_type == 'yesterday':
        return (value, value)
    elif range_type == 'last_n_days':
        end = today - timedelta(days=1)  # up to yesterday
        start = end - timedelta(days=value - 1)
        return (start, end)
    elif range_type == 'last_week':
        end = today - timedelta(days=1)
        start = end - timedelta(days=6)
        return (start, end)
    elif range_type == 'last_month':
        end = today - timedelta(days=1)
        start = end - timedelta(days=29)
        return (start, end)
    elif range_type == 'this_week':
        return value  # already a (start, end) tuple
    elif range_type == 'this_month':
        return value
    elif range_type == 'explicit_range':
        return value
    else:
        # Fallback: last 7 days? Or just today? Better to raise.
        raise ValueError(f"Unknown range type: {range_type}")


# Example usage (if run directly)
# if __name__ == "__main__":
#     test_queries = [
#         "What is my recovery today?",
#         "Show me steps from 2025-02-01 to 2025-02-10",
#         "How was my sleep last 7 days?",
#         "Compare my HRV this week vs last week",
#         "What workout should I do?",
#         "Why did my HRV drop last week?",
#     ]
#     for q in test_queries:
#         metric = extract_metric(q)
#         time_info = extract_time_range(q)
#         print(f"Query: {q}")
#         print(f"  Metric: {metric}")
#         print(f"  Time info: {time_info}")
#         if time_info:
#             start, end = resolve_time_range(time_info)
#             print(f"  Resolved dates: {start} to {end}")
#         print()
