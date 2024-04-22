import os

def generate_random_trips(network_file, output_file):
    command = f"python data_rand/randomTrips.py -n {network_file} -o {output_file}"
    os.system(command)

# Use the function
generate_random_trips("data_rand/Random.net.xml", "data_rand/randomTrips.rou.xml")
