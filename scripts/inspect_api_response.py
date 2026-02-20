import sys
import json
from datetime import date

sys.path.append('.')
from src.api.client import fetch_daily_metrics

def main():
    today = date.today()
    try:
        response = fetch_daily_metrics(today)
        print("Full API response (pretty printed):")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    main()