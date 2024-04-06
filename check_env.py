from TrafficEnv import SpeedLimitEnv
from stable_baselines3.common.env_checker import check_env
import traci


try:
    
    env = SpeedLimitEnv()
    check_env(env)


finally:
   traci.close(False)