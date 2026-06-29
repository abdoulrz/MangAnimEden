import requests
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def fetch_popads_dashboard_data(api_key):
    """
    Fetches Current Balance and Daily Revenue from PopAds API.
    Uses caching (15 minutes) to avoid rate limits and improve page speed.
    """
    if not api_key:
        return None

    cache_key = "popads_dashboard_data"
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    result = {
        'balance': 0.00,
        'chart_labels': [],
        'chart_data': []
    }

    try:
        # 1. Fetch Current Balance (user_status endpoint)
        status_url = f"https://www.popads.net/api/user_status?key={api_key}"
        headers = {'Accept': 'application/json'}
        status_response = requests.get(status_url, headers=headers, timeout=5)
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            if 'user' in status_data and 'balance' in status_data['user']:
                result['balance'] = round(float(status_data['user']['balance']), 2)

        # 2. Fetch Report (report_publisher endpoint for last 7 days)
        report_url = "https://www.popads.net/api/report_publisher"
        report_data_payload = {'key': api_key, 'quick': 'last_7_days', 'groups': 'datetime:day'}
        report_response = requests.post(report_url, data=report_data_payload, headers=headers, timeout=5)
        
        if report_response.status_code == 200:
            report_data = report_response.json()
            
            # The report_publisher API usually returns JSON with a 'rows' key
            if 'rows' in report_data and isinstance(report_data['rows'], list):
                # Data might be sorted or unsorted. Let's make sure it's sorted by date ascending
                # Assuming 'datetime' contains the date (e.g., '2023-10-01')
                try:
                    rows = report_data['rows']
                    rows.sort(key=lambda x: x.get('datetime', ''))
                    for row in rows:
                        date_str = row.get('datetime', '')
                        # PopAds publisher report uses 'revenue' or 'cost'. 
                        daily_rev = float(row.get('revenue', row.get('cost', 0)))
                        
                        if date_str:
                            result['chart_labels'].append(date_str)
                            result['chart_data'].append(round(daily_rev, 2))
                except Exception as e:
                    logger.error(f"Error parsing PopAds report data: {e}")

        # Cache the result for 15 minutes (900 seconds)
        cache.set(cache_key, result, 900)
        return result

    except requests.RequestException as e:
        logger.error(f"PopAds API Request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching PopAds data: {e}")
        return None
