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
        
        # Initialize state and other variables
        self.state = np.array([0,0,0,0,0])
        self.tot_emissions = 0
        self.occupancy = 0
        self.mean_speed = 0
        self.total_cars = 0
        self.total_trucks = 0


        # SUMO simulation set up
        self.simulation_dir = 'F:/SUMO/OptimalEmission-SUMO-ReinforcementLearning/'

        for f in os.listdir(self.simulation_dir):
            if f.endswith('.sumocfg'):
                self._SUMOCFG = os.path.join(self.simulation_dir, f)
        
        self.sumo_binary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo-gui')
        self.sumo_cmd = [self.sumo_binary, "-c", self._SUMOCFG]

        # Star simulation
        traci.start(self.sumo_cmd)


    def reset(self, seed=None, options=None):
        """Reset the state of the environment to an initial state."""

        self.close()
        traci.start(self.sumo_cmd)
        
  

        self.counter = 0 

        while self.counter < 200:
            traci.simulationStep()
            self.counter += 1 

        self.state = np.array(self.get_state(), dtype='float32') 

        return self.state, {}
    

    def close(self):
        traci.close(False)
   
          

    def step(self, action=None):
        """Execute one time step within the environment."""

        self.set_speed_limit(action)

        traci.simulationStep()

        self.reward = - self.get_emission()
        self.state = np.array(self.get_state(), dtype='float32')

        truncated=False
        self.counter += 1 
        if self.counter > 4500:
            truncated = True
            # self.close()

        done = False
        info = {}
        
        return self.state, self.reward, done, truncated, info


    def get_state(self):
        """Gets the current state space = total small vehicles, total large vehicles, average speed, occupancy, total emission."""
   
        number_of_lanes = traci.lane.getIDCount()
        count_vehc = 0
        lane_length_sum = 0
        mean_speed_sum = 0
        occupancy_sum = 0
        self.mean_speed = 0
        self.occupancy = 0

        lanes = traci.lane.getIDList()

        for lane in lanes:

            count_vehc += traci.lane.getLastStepVehicleNumber(lane) #int
            lane_length_sum += traci.lane.getLength(lane) #m
            mean_speed_sum += traci.lane.getLastStepMeanSpeed(lane) #m/s
            occupancy_sum += traci.lane.getLastStepOccupancy(lane) #%


        self.mean_speed = mean_speed_sum/number_of_lanes
        self.occupancy = (occupancy_sum/number_of_lanes)*100

        vehicles = emissions.get_all_vehicles()
        veh_types = []

        for vehicle in vehicles:
            veh_types.append(vehicle.type)

        self.total_cars = Counter(veh_types)['normal'] + Counter(veh_types)['sporty']
        self.total_trucks = Counter(veh_types)['coach'] + Counter(veh_types)['trailer']

        self.tot_emissions = self.get_emission()

        print([self.total_cars, self.total_trucks, self.mean_speed, self.occupancy, self.tot_emissions])

        return [self.total_cars, self.total_trucks, self.mean_speed, self.occupancy, self.tot_emissions]
    


    def get_emission(self):
        """Gets the total emission on the current state"""

        vehicles = emissions.get_all_vehicles()
        total_emissions = Emission()
    
        for vehicle in vehicles:
            total_emissions += vehicle.emissions

        total = total_emissions.co2 + total_emissions.co + total_emissions.nox + total_emissions.hc + total_emissions.pmx

        return total/1000000
    
    
    def set_speed_limit(self, action):
        """Sets the current speed limit on the network"""

        speeds = [40, 50, 60, 70, 80, 90, 100]
        print(f'current speed limit: {speeds[action]}')

        lanes = traci.lane.getIDList()
        for lane in lanes:
            traci.lane.setMaxSpeed(lane, speeds[action]/3.6)
