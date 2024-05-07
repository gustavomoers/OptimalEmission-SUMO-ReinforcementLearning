from stable_baselines3 import PPO #PPO
from TrafficEnv import SpeedLimitEnv
import time
import os
from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.evaluation import evaluate_policy

run = '1714040559-autobahn'
logdir = f"logs/{run}/evaluation/"


if not os.path.exists(logdir):
	os.makedirs(logdir)



def simulation_loop(): 



    env= SpeedLimitEnv(visuals=True)
    env = Monitor(env, logdir)
    env = DummyVecEnv([lambda: env])
    env = VecNormalize(env)
    env.training = False
    env.norm_reward = False

    model = PPO.load(f"F:/SUMO/OptimalEmission-SUMO-ReinforcementLearning/logs/{run}/rl_model_42500_steps.zip", env=env, print_system_info=True)

    mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=30)

# ==============================================================================
# -- main() --------------------------------------------------------------------
# ==============================================================================


def main():
  
    try:

        simulation_loop()

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')


if __name__ == '__main__':

    main()
