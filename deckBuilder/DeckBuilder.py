import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
import json
from deckBuilder.utils.mana_curve_similarity import mana_curve_similarity
from featureExtractor.classes.card import MTGCard
from simulator.Simulator import Simulator

class DeckBuilderEnv(gym.Env):
    def __init__(self, n: int, k: int, history: bool, parsed_cards_file: str, simulator: Simulator):
        """
        Parámetros:
            - n: Tamaño máximo del deck (número de cartas que se seleccionarán).
            - k: Número de cartas disponibles en cada paso.
            - history: Si es True, el estado incluye el deck seleccionado hasta el momento.
            - parsed_cards_file: Archivo JSON con las cartas.
            - simulator: Objeto Simulator para generar decks y simular partidas.
        """
        super().__init__()

        self.n = n  # deck size (cantidad máxima de cartas seleccionadas)
        self.k = k  # cantidad de cartas disponibles en cada paso
        self.history = history  # indica si se debe incluir la historia del deck en el estado
        self.parsed_cards_file = parsed_cards_file
        self.simulator = simulator

        self.deck = [] 
        self.current_step = 0  

        # Generar cartas disponibles iniciales
        self.available_cards = self.generate_random_cards()
        
        # Calcular la dimensión d del vector de cada carta (suponiendo que siempre es consistente)
        # Se toma la primera carta de las disponibles.
        if len(self.available_cards) > 0:
            self.d = len(self.available_cards[0].to_vector())
        else:
            raise ValueError("El archivo de cartas no tiene cartas o la generación falló.")

        # Definir el espacio de acciones
        self.action_space = spaces.Discrete(self.k)

        # Definir el espacio de observación en función de la configuración:
        # - Si history es False, el estado es un vector aplanado de k cartas: (k * d,)
        # - Si history es True, el estado es un vector aplanado de (n + k) cartas: ( (n+k) * d, )
        if self.history:
            obs_shape = ((self.n + self.k) * self.d, )
        else:
            obs_shape = (self.k * self.d, )
        self.observation_space = spaces.Box(low=0, high=1, shape=obs_shape, dtype=np.float32)

    def generate_random_cards(self):
        """
        Selecciona aleatoriamente k cartas a partir del archivo JSON y retorna sus representaciones MTGCard.
        """
        with open(self.parsed_cards_file, 'r') as json_in:
            parsed_cards = json.load(json_in)

        random_cards = random.sample(parsed_cards, self.k)
        mtg_cards = []
        for card in random_cards:
            card_obj = MTGCard(
                name=card.get("name", ""),
                card_type=card.get("card_type", ""),
                mana_cost_by_color=card.get("mana_cost_by_color", {}),
                convertedManaCost=card.get("convertedManaCost", 0),
                power=card.get("power", 0),
                toughness=card.get("toughness", 0),
                card_effects=card.get("card_effects", {}),
                card_keywords=card.get("card_keywords", {})
            )
            mtg_cards.append(card_obj)
        return mtg_cards

    def step(self, action):
        """
        Ejecuta una acción (selección de una carta, según el índice),
        añade esa carta al deck y actualiza el entorno.
        """
        selected_card = self.available_cards[action]
        self.deck.append(selected_card)
        self.current_step += 1

        terminated = False
        truncated = False

        if self.current_step >= self.n:
            deck_path, deck_name = self.simulator.generate_deck(self.deck)
            victory_rate = self.simulator.simulate_matches(
                generated_deck_name=deck_name,
                num_matches=4,
                games_per_match=2
            )
            reward = self.normalize_reward(victory_rate)
            print(f"Reward: {reward}")
            terminated = True  
        else:
            self.available_cards = self.generate_random_cards()
            reward = mana_curve_similarity(self.deck, self.n)  

        state = self.get_state()
        return state, reward, terminated, truncated, {}

    def get_state(self):
        """
        Construye el estado actual como vector fijo:
        
        - Si history es False: 
            Se obtiene el vector aplanado de las k cartas disponibles.
        
        - Si history es True:
            Se concatena el vector de las cartas seleccionadas (deck) con el vector de las cartas disponibles.
            El deck se rellena (padding con ceros) hasta tener n cartas para garantizar una forma fija.
        """
        if not self.history:
            # Estado: k cartas disponibles
            available_vectors = [card.to_vector() for card in self.available_cards]
            state = np.array(available_vectors, dtype=np.float32)  # Forma: (k, d)
            return state.flatten()  # Forma final: (k*d, )
        else:
            # Estado: deck (hasta n cartas) + k cartas disponibles

            # Obtener vectores para las cartas del deck
            deck_vectors = [card.to_vector() for card in self.deck]
            if len(deck_vectors) == 0:
                # Si aún no hay cartas seleccionadas, se rellena con ceros para n cartas
                deck_array = np.zeros((self.n, self.d), dtype=np.float32)
            else:
                deck_array = np.array(deck_vectors, dtype=np.float32)
                # Asegurarse de que deck_array tenga dos dimensiones:
                if deck_array.ndim == 1:
                    deck_array = deck_array.reshape(-1, self.d)
                num_deck_cards = deck_array.shape[0]
                if num_deck_cards < self.n:
                    pad_size = self.n - num_deck_cards
                    padding = np.zeros((pad_size, self.d), dtype=np.float32)
                    deck_array = np.vstack([deck_array, padding])
                else:
                    deck_array = deck_array[:self.n, :]

            # Obtener vectores para las cartas disponibles (siempre k cartas)
            available_vectors = [card.to_vector() for card in self.available_cards]
            available_array = np.array(available_vectors, dtype=np.float32)
            # Asegurar que available_array tenga la forma (k, d)
            if available_array.ndim == 1:
                available_array = available_array.reshape(-1, self.d)

            # Concatenar deck y cartas disponibles: forma final ((n + k), d)
            full_state = np.vstack([deck_array, available_array])
            return full_state.flatten()  # Aplanado a ( (n+k)*d, )

    def normalize_reward(self, victory_rate):
        """
        Normaliza la tasa de victorias (de 0 a 1) a un rango de -1 a 1.
        """
        return 2 * victory_rate - 1

    def reset(self, seed=None, options=None):
        """
        Reinicia el entorno. Esta versión acepta los parámetros seed y options,
        y retorna una tupla (observación, info).
        """
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

        self.deck = []
        self.current_step = 0
        self.available_cards = self.generate_random_cards()
        return self.get_state(), {}

    def render(self):
        """
        Muestra por consola el estado actual para depuración.
        """
        print(f"Deck ({len(self.deck)}/{self.n}): {self.deck}")
        print(f"Available Cards (k={self.k}): {self.available_cards}")
        print(f"Step: {self.current_step}/{self.n}")
