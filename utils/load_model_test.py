from stable_baselines3 import PPO

def evaluate_model(model_path: str, num_partidas: int, env) -> float:
    """
    Carga un modelo PPO entrenado y calcula su porcentaje de victoria
    promediado sobre `num_partidas` episodios (cada episodio tiene n=30 pasos).

    :param model_path: Ruta al archivo .zip del modelo guardado.
    :param num_partidas: Número de episodios a evaluar.
    :param env:          Instancia de DeckBuilderEnv (con n=30).
    :return:             Porcentaje de victoria medio (0–100).
    """
    # 1) Carga el modelo
    model = PPO.load(model_path)

    # 2) Reset inicial
    obs, _ = env.reset()

    total_win_rate = 0.0
    step_count = 0
    target_steps = 30 * num_partidas  # 30 pasos/episodio * num_partidas

    # 3) Rollout hasta completar los pasos objetivo
    while step_count < target_steps:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        step_count += 1

        if terminated:
            # reward final está en [-1,1] = 2*pct_victoria - 1
            win_rate = (reward + 1.0) / 2.0
            total_win_rate += win_rate
            obs, _ = env.reset()

    # 4) Porcentaje medio de victoria
    avg_win_rate = total_win_rate / num_partidas
    return avg_win_rate * 100.0
