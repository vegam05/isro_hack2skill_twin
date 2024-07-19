import os
import sys
import traci
import requests
import time
import random
from sumolib import checkBinary

# Importing the SUMO libraries
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

def get_traffic_data(api_key, bbox):
    url = "https://data.traffic.hereapi.com/v7/flow"
    params = {
        'apiKey': api_key,
        'in': bbox,
        'units': 'metric',
        'locationReferencing': 'shape'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def create_vehicle_from_traffic_data(traffic_data):
    if not traffic_data or 'results' not in traffic_data:
        return

    edge_ids = traci.edge.getIDList()
    for result in traffic_data['results']:
        road_id = result.get('location', {}).get('id')
        speed = result.get('currentSpeed', {}).get('value', 0)
        jam_factor = result.get('jamFactor', 0)

        if road_id in edge_ids:
            vehicle_count = int((10 - jam_factor) * 2)  
            for _ in range(vehicle_count):
                vehicle_id = f"veh_{road_id}_{int(time.time())}_{random.randint(0, 1000)}"
                try:
                    traci.vehicle.add(vehicle_id, road_id, departSpeed=str(speed))
                    traci.vehicle.setSpeed(vehicle_id, speed)
                    
                    possible_routes = traci.route.getIDList()
                    if possible_routes:
                        traci.vehicle.setRoute(vehicle_id, random.choice(possible_routes))
                except traci.TraCIException as e:
                    print(f"Error adding vehicle on road {road_id}: {e}")

def run_simulation():
    api_key = 'HUXG-svKWXMvRQjtzZMZ1KM4bx5-VBnecbkZjxEJOZk'
    bbox = 'bbox:80.905552,26.832788,80.946610,26.856222'
    
    step = 0
    try:
        while step < 3600:  
            traci.simulationStep()
            
            # Fetch and apply traffic data every 300 steps
            if step % 300 == 0:
                traffic_data = get_traffic_data(api_key, bbox)
                if traffic_data:
                    create_vehicle_from_traffic_data(traffic_data)
                else:
                    print("Failed to fetch traffic data.")
            
            # code to simulate accidents or traffic signal failures or other failures can be added here
            
            step += 1
    except traci.TraCIException as e:
        print(f"SUMO TraCI exception: {e}")
    finally:
        traci.close()

if __name__ == "__main__":
    sumoBinary = checkBinary('sumo-gui')
    try:
        traci.start([sumoBinary, "-c", "simulation_data/lucknow.sumo.cfg",
                     "--start", "--quit-on-end"])
        run_simulation()
    except traci.TraCIException as e:
        print(f"Error starting SUMO: {e}")