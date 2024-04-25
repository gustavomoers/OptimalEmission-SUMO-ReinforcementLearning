import gymnasium as gym
from gymnasium import spaces
import numpy as np
import traci
from utils import emissions
from utils.model import Emission
from collections import Counter
import os
import random


class SpeedLimitEnv(gym.Env):
    """A simple traffic simulation environment for adjusting speed limits to minimize emissions."""
    def __init__(self):
        super().__init__()
        
        # action space (discrete speed limits between 40 km/h and 100 km/h, in 10 km/h increments)
        self.action_space = spaces.Discrete(7)  # 7 options: 40, 50, ..., 100

        # self.action_space = spaces.Box(low=40, high=100,shape=(1,),dtype="float32")

        
        # observation space (total small vehicles, total large vehicles, average speed, occupancy (length of cars/lenght of roads), total emission)
        self.observation_space = spaces.Box(low=np.array([-np.inf, -np.inf, -np.inf, -np.inf]), high=np.array([np.inf, np.inf, np.inf, np.inf]), dtype=np.float32)
        
        # Initialize state and other variables
        self.state = np.array([0,0,0,0])
        self.tot_emissions = 0
        self.occupancy = 0
        self.mean_speed = 0
        self.total_cars = 0
        self.total_trucks = 0



        # SUMO simulation set up
        self.simulation_dir = 'F:/SUMO/OptimalEmission-SUMO-ReinforcementLearning/scenarios'

        self.dirs = [x[0] for x in os.walk(self.simulation_dir)]

        self.select_network()


    def reset(self, seed=None, options=None):
        """Reset the state of the environment to an initial state."""

        self.close()

        self.select_network()

        # lanes = traci.lane.getIDList()
        # for lane in lanes:
        #     traci.lane.setMaxSpeed(lane, 40)


        self.counter = 0 


        traci.simulationStep()
       

        self.state = np.array(self.get_state(), dtype='float32') 

        return self.state, {}
    

    def close(self):
        traci.close(False)
   
          

    def step(self, action=None):
        """Execute one time step within the environment."""

        self.set_speed_limit(action)

        traci.simulationStep()

       
        self.state = np.array(self.get_state(), dtype='float32')
        self.reward = - self.state[3]

        truncated=False
        self.counter += 1 
        if self.counter > 60000:
            truncated = True
            # self.close()

        done = False
        info = {}
        
        return self.state, self.reward, done, truncated, info


    def get_state(self):
        """Gets the current state space = total small vehicles, total large vehicles, average speed, occupancy, total emission."""
   
        veh_types =[]
        veh_speeds= []
        total_emissions = Emission()
        self.mean_speed = 0

        vehicles = emissions.get_all_vehicles()
        for vehicle in vehicles:
            veh_types.append(vehicle.type)
            veh_speeds.append(vehicle.speed)
            total_emissions += vehicle.emissions

        # print(veh_types)
        # self.total_cars = Counter(veh_types)['motorcycle_motorcycle'] + Counter(veh_types)['veh_passenger']
        # self.total_trucks = Counter(veh_types)['bus_bus'] + Counter(veh_types)['truck_truck']
        self.total_cars = sum(1 for row in veh_types if row[0][0] == 'v' or row[0][0] == 'm')
        self.total_trucks = sum(1 for row in veh_types if row[0][0] == 't' or row[0][0] == 'b')
        print(self.total_cars+self.total_trucks)

        self.mean_speed = sum(veh_speeds) / (len(veh_speeds)+0.00001)
        print(self.mean_speed)

        total = total_emissions.co2 + total_emissions.co + total_emissions.nox + total_emissions.hc + total_emissions.pmx
        self.tot_emissions = total/1000000

        # print([self.total_cars, self.total_trucks, self.mean_speed, self.tot_emissions])

        return [self.total_cars, self.total_trucks, self.mean_speed, self.tot_emissions]
    


    # def get_emission(self):
    #     """Gets the total emission on the current state"""

    #     vehicles = emissions.get_all_vehicles()
    #     total_emissions = Emission()
    
    #     for vehicle in vehicles:
    #         total_emissions += vehicle.emissions

    #     total = total_emissions.co2 + total_emissions.co + total_emissions.nox + total_emissions.hc + total_emissions.pmx

    #     return total/1000000
    
    
    def set_speed_limit(self, action):
        """Sets the current speed limit on the network"""

        speeds = [40, 50, 60, 70, 80, 90, 100]
        print(f'current speed limit: {speeds[action]}')

        lanes = traci.edge.getIDList()
        for lane in lanes:
            traci.edge.setMaxSpeed(lane, speeds[action]/3.6)

        # VID = traci.vehicle.getIDList()

        # for v in VID:
        #     traci.vehicle.setMaxSpeed(v, speeds[action]/3.6)


    def select_network(self):

        # SUMO simulation set up
        # scenario = random.choice(self.dirs)
        scenario = self.dirs[3]
        print(f'selected network: {scenario}')

        for f in os.listdir(scenario):
            if f.endswith('.sumocfg'):
                self._SUMOCFG = os.path.join(scenario, f)
        
        self.sumo_binary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo')
        self.sumo_cmd = [self.sumo_binary, "-c", self._SUMOCFG]

        # Star simulation
        traci.start(self.sumo_cmd)

        
