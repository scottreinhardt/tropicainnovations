import requests
import time  # optional: to pause between requests

def fetch_all_cities(batch_size=1000):
    base_url = "https://public.opendatasoft.com/api/v2/catalog/datasets/geonames-all-cities-with-a-population-1000/records"
    offset = 0
    all_data = []

    while True:
        params = {
            "limit": batch_size,
            "offset": offset
        }

        try:
            r = requests.get(base_url, params=params)
            r.raise_for_status()
            json_data = r.json()

            records = json_data.get("records", [])
            if not records:
                break  # No more data

            all_data.extend(records)
            print(f"Fetched {len(records)} records (Total so far: {len(all_data)})")
            offset += batch_size

            time.sleep(0.5)  # Optional: avoid rate limits

        except Exception as e:
            print(f"Error at")