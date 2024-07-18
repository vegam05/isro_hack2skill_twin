import requests

def get_traffic_data(api_key, bbox):
    url = "https://data.traffic.hereapi.com/v7/flow"
    params = {
        'apiKey': api_key,
        'in': bbox,
        'units': 'metric',  # Use metric units (km/h)
        'locationReferencing': 'shape'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

api_key = 'HUXG-svKWXMvRQjtzZMZ1KM4bx5-VBnecbkZjxEJOZk'
bbox = 'bbox:80.8746,26.7866,81.0103,26.9194' # Define the bounding box for Lucknow region (latitude,longitude)
traffic_data = get_traffic_data(api_key, bbox)

if traffic_data:
    print(traffic_data)
else:
    print("Failed to fetch traffic data.")
