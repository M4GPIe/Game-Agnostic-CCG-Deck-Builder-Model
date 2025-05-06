import os
import subprocess
from featureExtractor.classes.card import MTGCard
from collections import Counter
from typing import List
import random
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class Simulator:
    def __init__(self, forge_installation_path: str, forge_jar_path: str, test_decks_path: str, test_decks: List[str]=None, thread_num = 6):
        self.forge_installation_path = forge_installation_path
        self.forge_jar_path = forge_jar_path
        self.test_decks_path = test_decks_path
        self.test_decks = test_decks
        self.thread_num = thread_num 

    def generate_deck(self, parsed_cards: List[MTGCard]):
        """
        Genera el archivo .dck con las cartas proporcionadas y lo guarda en la ruta
        'forge_installation_path\\decks\\constructed'
        """
        
        lands, num_lands = self.calculate_lands(parsed_cards)

        deck_file_path = os.path.join(self.forge_installation_path, 'decks', 'constructed', 'Generated_deck.dck')

        self.write_deck(parsed_cards, lands, deck_file_path)

        print(f"El archivo .dck se ha generado correctamente: {deck_file_path}")
        return deck_file_path, "Generated_deck.dck"

    def calculate_lands(self, parsed_cards: List[MTGCard]):
        """
        Calcula el número ideal de tierras basándose en las cartas del mazo y su coste de mana.
        """
        num_lands = int(len(parsed_cards) * 0.4)

        mana_count = Counter()
        for card in parsed_cards:
            for color, count in card.mana_cost_by_color.items():
                if color != "C":
                    mana_count[color] += count
        
        total_mana_cost = sum(mana_count.values())
        lands = {}
        for color, count in mana_count.items():
            lands[color] = int((count / total_mana_cost) * num_lands)

        return lands, num_lands

    def write_deck(self, parsed_cards: List[MTGCard], lands: dict, output_file: str):
        """
        Escribe el archivo .dck con las cartas y tierras calculadas.
        """
        
        with open(output_file, 'w') as f:
            f.write("[metadata]\n")
            f.write("Name=Generated_deck\n")
            f.write("[main]\n")

            card_counts = Counter([card.name for card in parsed_cards])

            for card_name, count in card_counts.items():
                f.write(f"{count} {card_name}\n")

            for color, land_count in lands.items():
                if land_count == 0:
                    continue
                if color == 'B':
                    f.write(f"{land_count} Swamp\n")
                elif color == 'U':
                    f.write(f"{land_count} Island\n")
                elif color == 'R':
                    f.write(f"{land_count} Mountain\n")
                elif color == 'G':
                    f.write(f"{land_count} Forest\n")
                elif color == 'W':
                    f.write(f"{land_count} Plains\n")
                else:
                    f.write(f"{land_count} Wastes\n")
                    
                    
    def simulate_matches(self, generated_deck_name: str, num_matches: int, games_per_match: int):

        deck_list = []
        
        if not self.test_decks or len(self.test_decks)==0:
            print("no se han pasado mazos")
            text_decks_path = os.path.join(self.forge_installation_path, 'decks', 'constructed')

            deck_list = [f for f in os.listdir(text_decks_path) if f.endswith('.dck') and f is not generated_deck_name]
        else: deck_list=self.test_decks
        
        if len(deck_list) == 0:
            print("No hay archivos .dck en la carpeta especificada.")
            return
        
        match_results = []
        
        lock = threading.Lock()

        def worker(_):
            # Escoge un deck aleatorio
            test_deck_name = random.choice(deck_list)
            with lock:
                print(f"Simulando juego con el deck: {test_deck_name}")

            # Simula la partida
            result = self.run_match(games_per_match, test_deck_name, generated_deck_name)

            with lock:
                match_results.append(result)
                print(f"Partidas ganadas {result['wins_generated_deck']}/{result['total_games']}")

            return result

        # Lanzamos num_matches tareas en paralelo
        with ThreadPoolExecutor(max_workers=self.thread_num) as executor:
            futures = [executor.submit(worker, i) for i in range(num_matches)]

        wins = 0
        matches = 0

        for result in match_results:
            wins+=result["wins_generated_deck"]
            matches += result["total_games"]

        print(f"Total win rate: {wins/matches}")

        return wins/matches
        

    def run_match(self, games_per_match: int, test_deck_name: str, generated_deck_name: str):
        
        command = [
            "java", "-Xmx1024m", "-jar", os.path.join(self.forge_jar_path, "forge-gui-desktop-2.0.03-SNAPSHOT-jar-with-dependencies.jar"),
            "sim", "-d", generated_deck_name, test_deck_name, "-q", "-n", str(games_per_match)
        ]

        result = subprocess.run(command, check=True, capture_output=True, text=True, cwd=self.forge_jar_path)

        output = result.stdout

        total_games = 0
        wins_test_deck = 0
        wins_generated_deck = 0
        total_turns_test_deck = 0
        total_turns_generated_deck = 0

        match_result_pattern = r"Game (\d+) ended in (\d+) ms\. Ai\(\d\)-(\S.*) has (won|lost)"
        turn_pattern = r"Game outcome: Turn (\d+)"

        for line in output.splitlines():
            
            game_turns = 0
            
            match_result = re.search(match_result_pattern, line)
            if match_result:
                #print(match_result)
                total_games += 1
                winner = match_result.group(3)
                #print(winner)
                if winner == generated_deck_name[:-4]:
                    wins_generated_deck += 1 
                
                elif winner == test_deck_name:
                    wins_test_deck += 1 
                    
            turn_match = re.search(turn_pattern, line)
            if turn_match:
                turn_number = int(turn_match.group(1))
                game_turns += turn_number

        avg_turns_test_deck = total_turns_test_deck / wins_test_deck if wins_test_deck > 0 else 0
        avg_turns_generated_deck = total_turns_generated_deck / wins_generated_deck if wins_generated_deck > 0 else 0


        return {
            "total_games": total_games,
            "wins_test_deck": wins_test_deck,
            "wins_generated_deck": wins_generated_deck,
            "avg_turns_test_deck": avg_turns_test_deck,
            "avg_turns_generated_deck": avg_turns_generated_deck
        }
