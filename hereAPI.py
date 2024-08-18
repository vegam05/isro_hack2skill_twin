import os
import sys
import traci
import requests
import time
import random
from sumolib import checkBinary
import pandas as pd


scenario_data = pd.DataFrame()

# Importing the SUMO libraries
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

def generate_scenario_data(step, edges, scenario_type):
    global scenario_data
    new_data = []
    for edge in edges:
        # Collect features
        mean_speed = traci.edge.getLastStepMeanSpeed(edge)
        vehicle_count = traci.edge.getLastStepVehicleNumber(edge)
        jam_length = traci.edge.getLastStepLength(edge)
        
        # Create a dictionary of the features
        data = {
            'step': step,
            'edge': edge,
            'mean_speed': mean_speed,
            'vehicle_count': vehicle_count,
            'jam_length': jam_length,
            'scenario_type': scenario_type
        }
        new_data.append(data)
    
    # Create a new DataFrame with the new data and concatenate it with the existing data
    new_df = pd.DataFrame(new_data)
    global scenario_data
    scenario_data = pd.concat([scenario_data, new_df], ignore_index=True)

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

def create_vehicle_from_traffic_data(traffic_data, step):
    if not traffic_data or 'results' not in traffic_data:
        print('HELLO')
        return

    edge_ids = traci.edge.getIDList()
    for result in traffic_data['results']:
        road_id = result.get('location', {}).get('id')
        speed = result.get('currentSpeed', {}).get('value', 0)
        jam_factor = result.get('jamFactor', 0)

        if road_id in edge_ids:
            # Generate vehicles based on jam factor and speed
            vehicle_count = int((10 - jam_factor) * 2)  # More vehicles when less jammed
            print(vehicle_count)
            for _ in range(vehicle_count):
                vehicle_id = f"veh_{road_id}_{step}_{random.randint(0, 1000)}"
                try:
                    traci.vehicle.add(vehicle_id, road_id, departSpeed=str(speed))
                    traci.vehicle.setSpeed(vehicle_id, speed)
                    
                    # Set a random route for the vehicle
                    possible_routes = traci.route.getIDList()
                    if possible_routes:
                        traci.vehicle.setRoute(vehicle_id, random.choice(possible_routes))
                        print()
                except traci.TraCIException as e:
                    print(f"Error adding vehicle on road {road_id}: {e}")

def simulate_traffic_jam(edge_ids, intensity=2):
    for edge in edge_ids:
        try:
            traci.edge.setMaxSpeed(edge, traci.edge.getLastStepMeanSpeed(edge) / intensity)
        except traci.TraCIException as e:
            print(f"Error simulating traffic jam on edge {edge}: {e}")

# def simulate_traffic_signal_failure(tls_id):
#     try:
#         logic = traci.trafficlight.getAllProgramLogics(tls_id)[0]
#         phases = logic.getPhases()
#         for phase in phases:
#             phase.duration = 0
#         traci.trafficlight.setProgramLogic(tls_id, logic)
#     except traci.TraCIException as e:
#         print(f"Error simulating traffic signal failure for {tls_id}: {e}")

def get_edges_for_traffic_light(tls_id):
    try:
        controlled_links = traci.trafficlight.getControlledLinks(tls_id)
        affected_edges = set()
        for links in controlled_links:
            for link in links:
                affected_edges.add(link[0][0])  # The incoming edge of the link
        return list(affected_edges)
    except traci.TraCIException as e:
        print(f"Error getting edges for traffic light {tls_id}: {e}")
        return []

def simulate_flooded_roads(edge_ids, intensity=0.5):
    for edge in edge_ids:
        try:
            traci.edge.setMaxSpeed(edge, traci.edge.getLastStepMeanSpeed(edge) * intensity)
        except traci.TraCIException as e:
            print(f"Error simulating flood on edge {edge}: {e}")

def run_simulation():
    api_key = 'API_KEY'
    bbox = 'bbox:80.905552,26.832788,80.946610,26.856222'
    #print("Available edges:", traci.edge.getIDList())
    step = 0
    try:
        while step < 3600:  # Run for 3600 steps (1 hour if each step is 1 second)
            traci.simulationStep()
            
            # Fetch and apply traffic data every 200 steps 
            if step % 200 == 0:
                traffic_data = get_traffic_data(api_key, bbox)
                if traffic_data:
                    create_vehicle_from_traffic_data(traffic_data,step)
                else:
                    print("Failed to fetch traffic data.")
            
            # Simulate random events every 600 steps (10 minutes)
            if step % 600 == 0:
                simulate_traffic_jam(['994848277', '995140950'])
                #generate_scenario_data(step, ['994848277', '995140950'], 'traffic_jam')


                tls_id = '2196599314'
                #simulate_traffic_signal_failure(tls_id)
                # affected_edges = get_edges_for_traffic_light(tls_id)
                # generate_scenario_data(step, affected_edges, 'signal_failure')

                simulate_flooded_roads(['210670076#1', '-213249546#2'])
                #generate_scenario_data(step, ['210670076#1', '-213249546#2'], 'flood')
            
            step += 1
    except traci.TraCIException as e:
        print(f"SUMO TraCI exception: {e}")
    finally:
        traci.close()
        scenario_data.to_csv('scenario_data.csv', index=False)

if __name__ == "__main__":
    sumoBinary = checkBinary('sumo-gui')
    try:
        traci.start([sumoBinary, "-c", "simulation_data/lucknow.sumo.cfg",
                     "--start", "--quit-on-end"])
        run_simulation()
    except traci.TraCIException as e:
        print(f"Error starting SUMO: {e}")
