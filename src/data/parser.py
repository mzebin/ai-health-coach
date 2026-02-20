import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_daily_metrics(api_response: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """
    Parse the Ultrahuman API response and extract relevant daily metrics.

    Expected response structure:
    {
        "data": {
            "metrics": {
                "2025-02-20": [
                    {"type": "recovery_index", "object": {"value": 65}},
                    {"type": "movement_index", "object": {"value": 64}},
                    {"type": "sleep", "object": { ... }},
                    {"type": "steps", "object": {"total": 3087}},
                    {"type": "avg_sleep_hrv", "object": {"value": 61}},
                    {"type": "night_rhr", "object": {"avg": 48}},
                    {"type": "active_minutes", "object": {"value": 0}},
                    {"type": "vo2_max", "object": {"value": 55}},
                    ...
                ]
            }
        }
    }
    """
    # Initialize all metrics with None
    metrics = {
        'recovery_score': None,
        'movement_score': None,
        'sleep_score': None,
        'total_sleep_min': None,
        'sleep_efficiency': None,
        'deep_sleep_min': None,
        'rem_sleep_min': None,
        'light_sleep_min': None,
        'avg_temperature': None,
        'total_steps': None,
        'hrv_avg': None,
        'rhr_avg': None,
        'active_minutes': None,
        'vo2_max': None,
    }

    # Navigate to the metrics list
    try:
        data = api_response.get('data', {})
        metrics_by_date = data.get('metrics', {})
        if not metrics_by_date:
            logger.warning("No metrics found in response.")
            return metrics
        # Get the first (and only) date key – we assume only one date is returned
        date_str = next(iter(metrics_by_date.keys()))
        metrics_list = metrics_by_date[date_str]
    except (KeyError, StopIteration, TypeError) as e:
        logger.error(f"Unexpected API response structure: {e}")
        return metrics

    # Process each metric object in the list
    for item in metrics_list:
        if not isinstance(item, dict):
            continue
        metric_type = item.get('type')
        obj = item.get('object', {})

        if metric_type == 'recovery_index':
            metrics['recovery_score'] = _safe_float(obj.get('value'))
        elif metric_type == 'movement_index':
            metrics['movement_score'] = _safe_float(obj.get('value'))
        elif metric_type == 'sleep':
            # Extract sleep-related metrics from the nested sleep object
            sleep_score_obj = obj.get('sleep_score', {})
            metrics['sleep_score'] = _safe_float(sleep_score_obj.get('score'))

            total_sleep_obj = obj.get('total_sleep', {})
            metrics['total_sleep_min'] = _safe_float(total_sleep_obj.get('minutes'))

            sleep_efficiency_obj = obj.get('sleep_efficiency', {})
            metrics['sleep_efficiency'] = _safe_float(sleep_efficiency_obj.get('percentage'))

            deep_sleep_obj = obj.get('deep_sleep', {})
            metrics['deep_sleep_min'] = _safe_float(deep_sleep_obj.get('minutes'))

            rem_sleep_obj = obj.get('rem_sleep', {})
            metrics['rem_sleep_min'] = _safe_float(rem_sleep_obj.get('minutes'))

            light_sleep_obj = obj.get('light_sleep', {})
            metrics['light_sleep_min'] = _safe_float(light_sleep_obj.get('minutes'))

            avg_temp_obj = obj.get('average_body_temperature', {})
            metrics['avg_temperature'] = _safe_float(avg_temp_obj.get('celsius'))
        elif metric_type == 'steps':
            metrics['total_steps'] = _safe_float(obj.get('total'))
        elif metric_type == 'avg_sleep_hrv':
            # This is the average HRV during sleep (already aggregated)
            metrics['hrv_avg'] = _safe_float(obj.get('value'))
        elif metric_type == 'night_rhr':
            # Resting heart rate average
            metrics['rhr_avg'] = _safe_float(obj.get('avg'))
        elif metric_type == 'active_minutes':
            metrics['active_minutes'] = _safe_float(obj.get('value'))
        elif metric_type == 'vo2_max':
            metrics['vo2_max'] = _safe_float(obj.get('value'))
        # Note: There are also types like 'hr', 'temp', 'spo2', 'sleep_rhr' which we may ignore
        # for our core metrics, but could be added later.

    return metrics


def _safe_float(value: Any) -> Optional[float]:
    """Convert value to float if possible, else return None."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
