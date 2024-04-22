import os

def generate_random_network(output_file, iterations):
    command = f"netgenerate --rand -o {output_file} --rand.iterations={iterations}"
    os.system(command)

# Use the function
generate_random_network("data_rand/Random.net.xml", 70)



# os.system(f'cmd /c "netgenerate --rand -o network.net.xml --rand.grid \
#     --turn-lanes {turn_lanes} --turn-lanes.length {turn_lanes_length} \
#     -j traffic_light --rand.iterations=70"')
