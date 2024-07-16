#For analyzing traffic data
import xml.etree.ElementTree as ET

tree = ET.parse('lucknow.sumo.xml')
root = tree.getroot()

for timestep in root.findall('timestep'):
    for vehicle in timestep.findall('vehicle'):
        print(vehicle.attrib)

