import requests
from django.core.cache import cache
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def fetch_adsterra_dashboard_data(api_key):
    """
    Fetches Adsterra Publisher stats (Impressions, Clicks, Revenue).
    Uses caching (15 minutes) to avoid rate limits and improve page speed.
    """
    if not api_key:
        return None

    cache_key = "adsterra_dashboard_data"
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    result = {
        'total_revenue': 0.0,
        'total_impressions': 0,
        'total_clicks': 0,
        'chart_labels': [],
        'chart_data_revenue': [],
        'chart_data_impressions': [],
    }

    try:
        # Fetch Report for last 7 days
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
        
        url = f"https://api3.adsterratools.com/publisher/stats.json?start_date={start_date}&finish_date={end_date}&group_by=date"
        headers = {'X-API-Key': api_key, 'Accept': 'application/json'}
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'items' in data:
                rows = data['items']
                # Adsterra usually returns dates as YYYY-MM-DD
                rows.sort(key=lambda x: x.get('date', ''))
                
                for row in rows:
                    date_str = row.get('date', '')
                    revenue = float(row.get('revenue', 0))
                    impressions = int(row.get('impression', 0))
                    clicks = int(row.get('clicks', 0))
                    
                    if date_str:
                        result['chart_labels'].append(date_str)
                        result['chart_data_revenue'].append(round(revenue, 2))
                        result['chart_data_impressions'].append(impressions)
                        
                        result['total_revenue'] += revenue
                        result['total_impressions'] += impressions
                        result['total_clicks'] += clicks
                        
        result['total_revenue'] = round(result['total_revenue'], 2)
        
        # Cache the result for 15 minutes
        cache.set(cache_key, result, 900)
        return result

    except requests.RequestException as e:
        logger.error(f"Adsterra API Request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching Adsterra data: {e}")
        return None
