import os
import matplotlib.pyplot as plt

from stable_baselines3 import DQN, PPO, A2C
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import load_results
import torch
import gymnasium as gym  # para compatibilidad con Gymnasium

class TrainAgent:
    def __init__(self, env, log_dir: str = "logs/"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        # Monitor para guardar estadísticas
        self.env = Monitor(env, filename=os.path.join(self.log_dir, "monitor.csv"))

    def train(self, total_timesteps: int):
        vec_env = DummyVecEnv([lambda: self.env])
        device = "cuda" if torch.cuda.is_available() else "cpu"

        model = DQN(
            "MlpPolicy", vec_env,
            learning_rate=1e-4,
            buffer_size=100_000,
            batch_size=64,
            gamma=0.99,
            train_freq=(4, "step"),        # entrenar cada 4 pasos
            gradient_steps=1,
            learning_starts=10_000,
            target_update_interval=8000,
            exploration_fraction=0.1,
            exploration_initial_eps=1.0,
            exploration_final_eps=0.01,
            policy_kwargs=dict(
                net_arch=[512, 512],
                activation_fn=torch.nn.ReLU,
                # Dueling DQN se activa por defecto en SB3
                # No es necesario pasar `dueling=True` explícitamente aquí
            ),
            tensorboard_log="./rainbow_dqn_tb/",
            verbose=1,
            device=device,
            # prioritized_replay=True,
            # n_steps=3,
            # noisy_std=0.5,
            # double_q=True,  # activar Double DQN
        )

        model.learn(total_timesteps=total_timesteps)

        results = load_results(self.log_dir)
        print(results)

        obs = vec_env.reset()
        for _ in range(1000):
            action, _ = model.predict(obs, deterministic=True)
            obs, rewards, dones, infos = vec_env.step(action)
            self.env.unwrapped.render()

