import os
from pathlib import Path
import subprocess
from simulator.AbstractSimulator import AbstractSimulator, MatchResults
from featureExtractor.classes.HSCard import HSCard
from typing import List, Set
import random
import json

# export JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64"

class HearthstoneSimulator(AbstractSimulator):
  def __init__(self, test_decks_directory : str, run_simulator_path: str , game_config_path: str,supported_cards_names : Set[str]=None, supported_test_decks : List[str] = None):
    self.game_config_path = game_config_path
    self.supported_cards_names = supported_cards_names
    self.supported_test_decks = supported_test_decks
    self.generated_deck_name = 'Generated_deck.hsdeck'
    self.run_simulator_path = run_simulator_path
    super().__init__(test_decks_directory)

  def generate_deck(self, deck_cards: List[HSCard]) -> str:
    deck_file_path = os.path.join(self.test_decks_directory, self.generated_deck_name)
    with open(deck_file_path, "w", encoding="utf-8") as f:
        f.write("None,\n")  # Arena mode has no class
        names = [getattr(obj, "name", None) for obj in deck_cards if getattr(obj, "name", None) is not None]
        for i, name in enumerate(names):
            if i == len(names) - 1:
                f.write(f"{name}\n")  
            else:
                f.write(f"{name},\n")
                
    return deck_file_path


  def simulate_matches(self, num_matches:int, games_per_match : int) -> MatchResults:

    deck_list = []

    if not self.supported_test_decks or len(self.supported_test_decks)==0:
        deck_list = [f for f in os.listdir(self.test_decks_directory) if f.endswith('.hsdeck') and f is not self.generated_deck_name]
    else: deck_list=self.supported_test_decks

    if len(deck_list) == 0:
        print("No test decks found in the given directory")
        return
    
    result = {
                "winRate": 0,
                "avg_turns": 0,
            }

    for i in range(num_matches):
      test_deck_name = random.choice(deck_list)

      test_deck_path = os.path.join(self.test_decks_directory, test_deck_name)
      generated_deck_path = os.path.join(self.test_decks_directory, self.generated_deck_name)

      res = self.simulate_match(games_per_match, test_deck_name, self.generated_deck_name)

      result["avg_turns"] = res["avg_turns"] + result["avg_turns"]
      result["winRate"] = res["winRate"] + result["winRate"]

    result["avg_turns"] = result["avg_turns"]/num_matches
    result["winRate"] = result["winRate"]/num_matches

    return result

  def write_game_config(self, games_per_match : int, deck_a_name : str, deck_b_name : str, output_file_name: str):

    config_file = os.path.join(self.game_config_path, 'masterParams.hsparam')

    with open(config_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if "num_simulations" in line:
            new_line = f"num_simulations           =   {games_per_match}\n"
        elif "output_file" in line:
            new_line = f"output_file               =   {output_file_name}\n"
        elif "deckListFilePath0" in line:
            new_line = f"deckListFilePath0         =       {deck_a_name}\n"
        elif "deckListFilePath1" in line:
            new_line = f"deckListFilePath1         =       {deck_b_name}\n"
        else:
            new_line = line
        new_lines.append(new_line)

    with open(config_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

  def simulate_match(self, games_per_match: int ,deck_a_name : str, deck_b_name : str):

    output_file_name = f"{deck_a_name.replace('.hsdeck','')}_vs_{deck_b_name.replace('.hsdeck','')}.hsres"

    self.write_game_config(games_per_match, deck_a_name, deck_b_name, output_file_name)

    result = subprocess.run(['gradlew','runSim'], cwd=r"C:\Users\Admin\OneDrive\Escritorio\TFG\HearthSim",shell=True)

    if result.returncode != 0:
        print("Error executing match")
        print(result.stderr)
        return None

    output_file_path = os.path.join(self.game_config_path, output_file_name)

    print(output_file_path)

    if os.path.exists(output_file_path):
        with open(output_file_path, "r", encoding="utf-8") as f:
            contenido = f.read()

        matches_data = []
        total_wins = 0
        total_turns = 0
        total_matches = 0

        # Parse the match data to calculate the win rate and average turns
        for line in contenido.splitlines():
            try:
                match_result = json.loads(line)
                winner = match_result.get("winner", None)
                duration = match_result.get("duration", 0)

                # Filter out matches where player 1 won
                if winner == 1:
                    total_wins += 1
                total_turns += duration
                total_matches += 1
            except json.JSONDecodeError:
                print("Error parsing match result line:", line)
                continue

        # If player 1 never won, set the average duration to -1
        if total_wins > 0:
            avg_turns = total_turns / total_wins
        else:
            avg_turns = -1

        print(total_wins, total_matches)

        # Return the win rate and average turns for player 1
        win_rate = total_wins / total_matches if total_matches > 0 else 0
        print(win_rate)
        return {
            "winRate": win_rate,
            "avg_turns": avg_turns
        }
    else:
        print("Output file not found: ", self.game_config_path)
        return None

