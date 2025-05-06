import os
import matplotlib.pyplot as plt

from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import load_results, ts2xy, plot_results
import torch

class TrainAgent:
    def __init__(self, env, log_dir: str = "logs/"):
        # directorio de logs
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        self.env = Monitor(env, filename=os.path.join(self.log_dir, "monitor.csv"))
        
    def train(self, total_timesteps: int):
        vec_env = DummyVecEnv([lambda: self.env])

        device = "cuda" if torch.cuda.is_available() else "cpu"

        model = DQN(
            "MlpPolicy", vec_env,
            learning_rate=3e-4,
            buffer_size=500_000,
            learning_starts=10000,
            batch_size=128,
            gamma=0.99,
            train_freq=1,
            gradient_steps=1,
            target_update_interval=2000,
            exploration_fraction=0.1,
            exploration_initial_eps=1.0,
            exploration_final_eps=0.01,
            policy_kwargs=dict(net_arch=[512, 512], activation_fn=torch.nn.ReLU),
            tensorboard_log="./dqn_vectorial_tb/",
            prioritized_replay=True,
            prioritized_replay_alpha=0.6,
            prioritized_replay_beta0=0.4,
            prioritized_replay_beta_iters=1_000_000,
            verbose=1,
            device=device
                )

        # entrenamos
        model.learn(total_timesteps=total_timesteps)

        results = load_results(self.log_dir)

        print(results)

        # # 3a) Dibujamos curva recompensas vs timesteps
        # plot_results([self.log_dir],   # 1) carpeta de logs
        #       total_timesteps,  # 2) hasta este timestep
        #       "timesteps",      # 3) eje x: pasos de tiempo
        #       "Recompensa v Timesteps")  # 4) título
        # plt.show()

        # # 3b) Dibujamos recompensa media móvil (ventana=100 ep.)
        # # ts2xy permite extraer arrays de timesteps o episodios
        # x_epi, y_rew = ts2xy(results, "episodes")
        # window = 100
        # # media móvil
        # import numpy as np
        # mov_avg = np.convolve(y_rew, np.ones(window)/window, mode='valid')
        # plt.figure()
        # plt.plot(x_epi[window-1:], mov_avg)
        # plt.xlabel("Episodio")
        # plt.ylabel(f"Recompensa media (ventana={window})")
        # plt.title("Media móvil de recompensa por episodio")
        # plt.show()

        # # 3c) Dibujamos longitud de episodio vs episodios
        # # del mismo array results[:,2] sale length
        # # pero ts2xy no la extrae directamente: usamos pandas:
        # import pandas as pd
        # df = pd.read_csv(os.path.join(self.log_dir, "monitor.csv"), comment='#',
        #                  names=['t','r','l','time'], header=None)
        # plt.figure()
        # plt.plot(df.index, df['l'])
        # plt.xlabel("Índice de episodio")
        # plt.ylabel("Longitud de episodio")
        # plt.title("Longitud de episodio por iteración")
        # plt.show()

        # 4) (Opcional) Prueba del modelo
        obs = vec_env.reset()
        for _ in range(1000):
            action, _ = model.predict(obs, deterministic=True)
            obs, rewards, dones, infos = vec_env.step(action)
            self.env.unwrapped.render()
