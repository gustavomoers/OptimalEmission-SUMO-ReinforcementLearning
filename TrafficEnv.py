import gymnasium as gym
from gymnasium import spaces
import numpy as np
import traci
from utils import emissions
from utils.model import Emission
from collections import Counter
import os


class SpeedLimitEnv(gym.Env):
    """A simple traffic simulation environment for adjusting speed limits to minimize emissions."""
    def __init__(self):
        super().__init__()
        
        # action space (discrete speed limits between 40 km/h and 100 km/h, in 10 km/h increments)
        self.action_space = spaces.Discrete(7)  # 7 options: 40, 50, ..., 100

        # self.action_space = spaces.Box(low=-1, high=1,shape=(1,),dtype="float32")

        
        # observation space (total small vehicles, total large vehicles, average speed, occupancy (length of cars/lenght of roads), total emission)
        self.observation_space = spaces.Box(low=np.array([0, 0, 0, 0, 0]), high=np.array([400, 400, 28, 100, 100]), dtype=np.float32)
        
        # Initialize state and other necessary variables
        self.state = np.array([0,0,0,0,0])

        self.simulation_dir = 'F:/SUMO/sumo-grid/'

        for f in os.listdir(self.simulation_dir):
            if f.endswith('.sumocfg'):
                self._SUMOCFG = os.path.join(self.simulation_dir, f)
        
        self.sumo_binary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo')
        self.sumo_cmd = [self.sumo_binary, "-c", self._SUMOCFG]


        emissions = 0
        occupancy = 0
        mean_speed = 0
        total_cars = 0
        total_trucks = 0
        traci.start(self.sumo_cmd)


    def reset(self, seed=None, options=None):
        """Reset the state of the environment to an initial state."""

        self.close()
        traci.start(self.sumo_cmd)
        self.state = np.array(self.get_state(), dtype='float32')
  

        self.counter = 0  

        return self.state, {}
    

    def close(self):
        traci.close(False)
   
          

    def step(self, action=None):
        """Execute one time step within the environment."""

        act = action
        print(f'action: {act}')

        self.set_speed_limit(act)
        traci.simulationStep()
        self.reward = - self.get_emission()
        self.state = np.array(self.get_state(), dtype='float32')

        truncated=False
        self.counter += 1 
        if self.counter > 200:
            truncated = True
            # self.close()

        done = False
        info = {}
        
        return self.state, self.reward, done, truncated, info


    
    def get_state(self):

   
        number_of_lanes = traci.lane.getIDCount()
        count_vehc = 0
        lane_length_sum = 0
        mean_speed_sum = 0
        occupancy_sum = 0
        mean_speed = 0
        occupancy = 0

        lanes = traci.lane.getIDList()

        for lane in lanes:

            count_vehc += traci.lane.getLastStepVehicleNumber(lane) #int
            lane_length_sum += traci.lane.getLength(lane) #m
            mean_speed_sum += traci.lane.getLastStepMeanSpeed(lane) #m/s
            occupancy_sum += traci.lane.getLastStepOccupancy(lane) #%


        mean_speed = mean_speed_sum/number_of_lanes
        occupancy = (occupancy_sum/number_of_lanes)*100

        vehicles = emissions.get_all_vehicles()
        veh_types = []

        for vehicle in vehicles:
            veh_types.append(vehicle.type)

        total_cars = Counter(veh_types)['normal'] + Counter(veh_types)['sporty']
        total_trucks = Counter(veh_types)['coach'] + Counter(veh_types)['trailer']

        tot_emissions = self.get_emission()

        print([total_cars, total_trucks, mean_speed, occupancy, tot_emissions])

        return [total_cars, total_trucks, mean_speed, occupancy, tot_emissions]
    


    def get_emission(self):

        vehicles = emissions.get_all_vehicles()
        total_emissions = Emission()
    
        for vehicle in vehicles:
            total_emissions += vehicle.emissions

        total = total_emissions.co2 + total_emissions.co + total_emissions.nox + total_emissions.hc + total_emissions.pmx

        return total/100000000
    
    
    def set_speed_limit(self, act):

        speeds = [40, 50, 60, 70, 80, 90, 100]
        # print('here')

        # speed_value = (max(speeds)-min(speeds))*((act[0]+1)/2)+min(speeds)
        print(speeds[act])

        lanes = traci.lane.getIDList()
        for lane in lanes:
            traci.lane.setMaxSpeed(lane, speeds[act]/3.6)
