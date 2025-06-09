import os
import matplotlib.pyplot as plt

from stable_baselines3 import DQN, PPO, A2C
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import load_results
import torch
from typing import Literal

class TrainAgent:
    def __init__(self, env, log_dir: str = "logs/"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        # Monitor para guardar estadísticas
        self.env = Monitor(env, filename=os.path.join(self.log_dir, "monitor.csv"))

    def train(self, total_timesteps: int, algorithm = Literal["A2C","PPO","DQN"]):
        vec_env = DummyVecEnv([lambda: self.env])
        device = "cuda" if torch.cuda.is_available() else "cpu"

        model = None

        if algorithm == "A2C":
            model = A2C(
                 "MlpPolicy",
                 vec_env,
                 learning_rate=7e-4,
                 n_steps=20,
                 gamma=0.99,
                 gae_lambda=0.95,
                 ent_coef=0.01,
                 vf_coef=0.25,
                 max_grad_norm=0.5,
                 use_rms_prop=True,
                 rms_prop_eps=1e-5,
                 normalize_advantage=True,
                 policy_kwargs=dict(
                     net_arch=dict(pi=[128, 128], vf=[128, 128]),
                     activation_fn=torch.nn.ReLU
                 ),
                 tensorboard_log="./a2c_tb/",
                 verbose=1,
                 device="cpu"
             )
        elif algorithm == "DQN":
            model = DQN(
                "MlpPolicy", vec_env,
                learning_rate=1e-4,
                buffer_size=100_000,
                batch_size=32,
                gamma=0.99,
                train_freq=(4, "step"),         #entrenar cada 4 pasos
                gradient_steps=1,
                target_update_interval=512,
                exploration_fraction=0.1,
                exploration_initial_eps=1.0,
                exploration_final_eps=0.01,
                policy_kwargs=dict(
                    net_arch=[512, 512],
                    activation_fn=torch.nn.ReLU,
                ),
                tensorboard_log="./dqn_vectorial_tb/",
                verbose=1,
                device=device,
            )
        else:
            model = PPO(
                "MlpPolicy",
                vec_env,
                learning_rate=3e-4,
                n_steps=512,             #ahora cada rollout son 512 pasos → ~78 rollouts
                batch_size=32,           #minibatches pequeños para mayor número de updates
                n_epochs=10,             #pasadas por rollout
                gamma=0.99,
                gae_lambda=0.95,
                ent_coef=0.01,
                vf_coef=0.5,
                max_grad_norm=0.5,
                clip_range=0.2,
                policy_kwargs=dict(
                    net_arch=[256, 256],
                    activation_fn=torch.nn.ReLU
                ),
                tensorboard_log="./ppo_tb/",
                verbose=1,
                device="cpu",
            )

        model.learn(total_timesteps=total_timesteps)

        results = load_results(self.log_dir)
        print(results)

        obs = vec_env.reset()
        for _ in range(1000):
            action, _ = model.predict(obs, deterministic=True)
            obs, rewards, dones, infos = vec_env.step(action)
            self.env.unwrapped.render()

