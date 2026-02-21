import os
import sys
from datetime import date, timedelta
from typing import Optional, Tuple, List, Dict

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.chatbot.entity_extractor import resolve_time_range
from src.data.cache import fetch_metrics, get_latest_metrics


def format_value(metric: str, value: Optional[float]) -> str:
    """Format a metric value with appropriate units or rounding."""
    if value is None:
        return "No data available"

    # Add units or formatting based on metric type
    if metric in ['sleep_efficiency']:
        return f"{value:.1f}%"
    elif metric in ['avg_temperature']:
        return f"{value:.1f}°C"
    elif metric in ['total_steps']:
        return f"{int(value)}"
    elif metric in ['total_sleep_min', 'deep_sleep_min', 'rem_sleep_min', 'light_sleep_min', 'active_minutes']:
        # Convert minutes to hours and minutes for better readability
        hours = int(value) // 60
        minutes = int(value) % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    elif metric in ['hrv_avg', 'rhr_avg', 'vo2_max', 'recovery_score', 'movement_score', 'sleep_score']:
        return f"{int(value)}"
    else:
        return f"{value:.2f}"


def get_current_response(metric: str, latest_row: Optional[Dict]) -> str:
    """Generate response for get_current intent."""
    if not latest_row:
        return f"I don't have any data for {metric} yet."

    value = latest_row.get(metric)
    if value is None:
        return f"I don't have {metric} data for the latest date ({latest_row['date']})."

    formatted = format_value(metric, value)
    return f"Your latest {metric} on {latest_row['date']} is {formatted}."


def get_history_response(metric: str, start_date: date, end_date: date, rows: List[Dict]) -> str:
    """Generate response for get_history intent."""
    if not rows:
        return f"I don't have any {metric} data from {start_date} to {end_date}."

    # Extract values for the requested metric, filtering out None
    values = []
    for row in rows:
        val = row.get(metric)
        if val is not None:
            values.append(val)

    if not values:
        return f"I don't have {metric} data in the selected period ({start_date} to {end_date})."

    avg_val = sum(values) / len(values)
    min_val = min(values)
    max_val = max(values)

    avg_fmt = format_value(metric, avg_val)
    min_fmt = format_value(metric, min_val)
    max_fmt = format_value(metric, max_val)

    return (f"Over {len(values)} days from {start_date} to {end_date}, "
            f"your {metric} averaged {avg_fmt} (min: {min_fmt}, max: {max_fmt}).")


def compare_response(metric: str, rows: List[Dict]) -> str:
    """Generate response for compare intent (simple version: compare most recent two days)."""
    if len(rows) < 2:
        return f"Not enough data to compare {metric}. I need at least two days of data."

    # Sort by date descending (most recent first)
    sorted_rows = sorted(rows, key=lambda r: r['date'], reverse=True)
    latest = sorted_rows[0]
    previous = sorted_rows[1]

    val_latest = latest.get(metric)
    val_previous = previous.get(metric)

    if val_latest is None or val_previous is None:
        missing = []
        if val_latest is None: missing.append(latest['date'])
        if val_previous is None: missing.append(previous['date'])
        return f"Missing {metric} data for {', '.join(missing)}."

    diff = val_latest - val_previous
    direction = "increased" if diff > 0 else "decreased" if diff < 0 else "remained the same"
    abs_diff = abs(diff)

    latest_fmt = format_value(metric, val_latest)
    prev_fmt = format_value(metric, val_previous)
    diff_fmt = format_value(metric, abs_diff)

    if diff == 0:
        return f"Your {metric} stayed the same at {latest_fmt} on {latest['date']} compared to {previous['date']}."
    else:
        return (f"Your {metric} {direction} from {prev_fmt} on {previous['date']} "
                f"to {latest_fmt} on {latest['date']} (a change of {diff_fmt}).")


def generate_response(intent: str, metric: Optional[str], time_range_info: Optional[Tuple[str, Tuple[date, date]]]) -> str:
    """
    Main entry point: generate a response based on intent and extracted entities.
    """
    today = date.today()

    # Resolve date range based on intent and time_range_info
    if intent == 'get_current':
        # For current, we want the latest data (today or most recent)
        latest_row = get_latest_metrics()
        if latest_row:
            row_dict = dict(latest_row)
            return get_current_response(metric, row_dict)
        else:
            return "I don't have any data yet. Please fetch some historical data first."

    elif intent in ['get_history', 'compare']:
        # For these, we need to determine a date range
        if time_range_info:
            try:
                start, end = resolve_time_range(time_range_info, today)
            except Exception as e:
                return f"Could not understand the time range: {e}"
        else:
            # Default range: last 7 days for history/compare
                # Default to last 7 days
                end = today - timedelta(days=1)
                start = end - timedelta(days=6)

        # Fetch data from cache for the range
        rows = fetch_metrics(start, end)
        if not rows:
            return f"No data available from {start} to {end}."

        # Convert rows to list of dicts
        rows_dict = [dict(row) for row in rows]

        if intent == 'get_history':
            return get_history_response(metric, start, end, rows_dict)
        elif intent == 'compare':
            return compare_response(metric, rows_dict)
        else:
            return "I'm not sure how to answer that."
    else:
        return "I don't know how to handle that intent."