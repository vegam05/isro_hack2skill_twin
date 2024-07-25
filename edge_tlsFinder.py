from sumolib import net

# Load the network
netfile = "simulation_data/xml/lucknow.net.xml"
network = net.readNet(netfile)

# Print all edges
edges = network.getEdges()
print("Edges:")
for edge in edges:
    print(f"Edge ID: {edge.getID()}")

# Print all traffic lights
traffic_lights = network.getTrafficLights()
print("Traffic Lights:")
for tls in traffic_lights:
    print(f"TLS ID: {tls.getID()}")

