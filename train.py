from stable_baselines3 import PPO #PPO
from TrafficEnv import SpeedLimitEnv
import time
import os
from stable_baselines3.common.callbacks import CallbackList
from callbacks import *
from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback


logdir = f"logs/{int(time.time())}/"


if not os.path.exists(logdir):
	os.makedirs(logdir)



def simulation_loop(): 


    # Create Callback
    save_callback = SaveOnBestTrainingRewardCallback(check_freq=100, log_dir=logdir, verbose=1) 
    tensor = TensorboardCallback()                                                                  # 
    checkpoint = CheckpointCallback(save_freq=500, save_path=logdir, verbose=1 )  


    env= SpeedLimitEnv()
    env = Monitor(env, logdir)
    env = DummyVecEnv([lambda: env])
    env = VecNormalize(env)

    model = PPO('MlpPolicy', env, verbose=2, tensorboard_log=logdir)  # pass the env to model

    TIMESTEPS = 500000 
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"PPO", progress_bar=False, 
                    callback = CallbackList([tensor, save_callback, checkpoint])) 
                



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
