import os
from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime

pytrends = TrendReq(hl='en-US', tz=360)

def fetch_trending(regions):
    all_trending_data = pd.DataFrame()
    
    for region in regions:
        try:
            trending_searches_df = pytrends.trending_searches(pn=region)
            trending_searches_df['region'] = region  
            all_trending_data = pd.concat([all_trending_data, trending_searches_df], ignore_index=True)
        except Exception as e:
            print(f"get {region} error: {e}")
            continue  # 

    all_trending_data['date'] = datetime.now().strftime('%Y-%m-%d')  

    file_path = 'trending_searches.csv'


    file_exists = os.path.isfile(file_path)

    all_trending_data.to_csv(file_path, mode='a', header=not file_exists, index=False)
    print(f"get data for {datetime.now().strftime('%Y-%m-%d')} ")

def get_region_code(country_name):
    country_name = country_name.lower()
    region_mapping = {
        'united states': 'united_states',
        'us': 'united_states',
        'usa': 'united_states',
        '美国': 'united_states',
        'canada': 'canada',
        '加拿大': 'canada',
        'united kingdom': 'united_kingdom',
        'uk': 'united_kingdom',
        '英国': 'united_kingdom',
        'australia': 'australia',
        '澳大利亚': 'australia',
    }
    return region_mapping.get(country_name)

