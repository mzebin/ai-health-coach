import os
import json
from datetime import date
from typing import Any, Dict, Optional

import requests


def get_config():
    """Load configuration from config.json if it exists."""
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


def get_token():
    """Get Ultrahuman API token: first from env, then from config."""
    token = os.environ.get('ULTRAHUMAN_TOKEN')
    if not token:
        config = get_config()
        token = config.get('ultrahuman_token')
    if not token:
        raise ValueError("ULTRAHUMAN_TOKEN not found in environment or config.json")
    return token


def get_email():
    """Get Ultrahuman email (optional) from env or config."""
    email = os.environ.get('ULTRAHUMAN_EMAIL')
    if not email:
        config = get_config()
        email = config.get('ultrahuman_email')
    return email


def fetch_daily_metrics(
        query_date: date,
        token: Optional[str] = None,
        email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch daily metrics from Ultrahuman API for a given date.

    Args:
        query_date: The date to fetch (datetime.date object)
        token: API token (if None, will try to load from env/config)
        email: Optional email parameter for the API

    Returns:
        JSON response as dict

    Raises:
        Exception on API error or missing data.
    """
    if token is None:
        token = get_token()

    url = "https://partner.ultrahuman.com/api/v1/partner/daily_metrics"
    headers = {"Authorization": token}
    params = {"date": query_date.isoformat()}
    if email:
        params["email"] = email
    else:
        # Try to get email from config if not provided
        email_from_config = get_email()
        if email_from_config:
            params["email"] = email_from_config

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"API request failed with status {response.status_code}: {response.text}")

    data = response.json()
    # Optional: check if response contains expected data
    if not data or 'data' not in data:
        raise Exception(f"Unexpected API response format: {data}")

    return data


# test: fetch today's data
# if __name__ == "__main__":
#     try:
#         today = date.today()
#         result = fetch_daily_metrics(today)
#         print("Success! Response keys:", result.keys())
#     except Exception as e:
#         print("Error:", e)
