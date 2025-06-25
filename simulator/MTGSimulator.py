import os
import subprocess
from collections import Counter
from typing import List, Set
import random
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from simulator.AbstractSimulator import AbstractSimulator, MatchResults
from featureExtractor.classes.MTGCard import MTGCard

class MTGSimulator(AbstractSimulator):
  def __init__(self, forge_jar_path: str, test_decks_directory : str,thread_num: int,supported_cards_names : Set[str]=None, supported_test_decks : List[str] = None):
    self.supported_cards_names = supported_cards_names
    self.supported_test_decks = supported_test_decks
    self.forge_jar_path = forge_jar_path
    self.thread_num = thread_num
    self.generated_deck_name = 'Generated_deck.dck'
    super().__init__(test_decks_directory)

  def generate_deck(self, parsed_cards: List[MTGCard]):

        lands, num_lands = self.calculate_lands(parsed_cards)

        deck_file_path = os.path.join(self.test_decks_directory, self.generated_deck_name)

        self.write_deck(parsed_cards, lands, deck_file_path)

        print(f"Deck file generated correctly: {deck_file_path}")
        return deck_file_path

  def calculate_lands(self, parsed_cards: List[MTGCard]):
      """
        Calculate ideal number of lands according to the number of cards for each color
      """
      num_lands = int(len(parsed_cards) * 0.5)

      mana_count = Counter()
      for card in parsed_cards:
          for color, count in card.cost_by_color.items():
              if color != "C":
                  mana_count[color] += count

      total_mana_cost = sum(mana_count.values())
      lands = {}
      for color, count in mana_count.items():
          lands[color] = int((count / total_mana_cost) * num_lands)

      return lands, num_lands

  def write_deck(self, parsed_cards: List[MTGCard], lands: dict, output_file: str):
      """
      Writes the .dck file with the given cards
      """

      with open(output_file, 'w') as f:
          f.write("[metadata]\n")
          f.write("Name=Generated_deck\n")
          f.write("[Main]\n")

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

  def simulate_matches(self, num_matches:int, games_per_match : int) -> MatchResults:

      deck_list = []

      if not self.supported_test_decks or len(self.supported_test_decks)==0:
          text_decks_path = os.path.join(self.test_decks_directory)

          deck_list = [f for f in os.listdir(text_decks_path) if f.endswith('.dck') and f is not self.generated_deck_name]
      else: deck_list=self.supported_test_decks

      if len(deck_list) == 0:
          print("No test decks found in the given directory")
          return

      match_results = []

      lock = threading.Lock()

      def worker(_):
          test_deck_name = random.choice(deck_list)
          with lock:
              print(f"Simulating deck with: {test_deck_name}")

        #   test_deck_path = os.path.join(self.test_decks_directory, test_deck_name)
        #   generated_deck_path = os.path.join(self.test_decks_directory, self.generated_deck_name)

          result = self.simulate_match(games_per_match, test_deck_name,  self.generated_deck_name)

          with lock:
              match_results.append(result)
              print(f"Winned games {result['wins_generated_deck']}/{result['total_games']}")

          return result

      with ThreadPoolExecutor(max_workers=self.thread_num) as executor:
          futures = [executor.submit(worker, i) for i in range(num_matches)]

      wins = 0
      turns = 0
      matches = 0

      for result in match_results:
          wins+=result["wins_generated_deck"]
          matches += result["total_games"]
          turns+=result["avg_turns_generated_deck"]

      print(f"Total win rate: {wins/matches}")

      return {"winRate": wins/matches,"avg_turns": turns/matches}


  def simulate_match(self, games_per_match: int, test_deck_name: str, generated_deck_name: str):
      
      command = [
          "java", "-Xmx1024m", "-jar", os.path.join(self.forge_jar_path, "forge-gui-desktop-2.0.03-SNAPSHOT-jar-with-dependencies.jar"),
          "sim", "-D", self.test_decks_directory , "-d",generated_deck_name, test_deck_name, "-q", "-n", str(games_per_match)
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