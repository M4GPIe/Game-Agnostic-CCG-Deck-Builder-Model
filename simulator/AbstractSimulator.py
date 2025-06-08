from abc import ABC, abstractmethod
from typing import Dict, List, Set

from featureExtractor.classes.AbstractCard import AbstractCard

from typing import TypedDict

# Typed class of a game result
class MatchResults(TypedDict):
    winRate: float
    avg_turns: float | None
    avg_lifes_left: float | None

#Abstract class containing all methods needed to fulfill with any new simulator
class AbstractSimulator(ABC):

  """"
    Constructor:
      - test_decks_directory : Directory containing all test decks
  """
  def __init__(self, test_decks_directory : str):
    self.test_decks_directory = test_decks_directory

  """
    Deck build: builds the deck file and returns the generated deck name
      - deck_cards : List of card names
  """
  @abstractmethod
  def generate_deck(self, deck_cards : List[AbstractCard]) -> str:
    pass

  """
    Simulate matches: runs a number of matches between two decks and returns a result with a list of game results for each match
      - num_matches: number of matches to be played each with a different test deck
      - games_per_match : number of games played on each match
      - deck_a_name : Name of the first deck
      - deck_b_name : Name of the second deck
  """
  @abstractmethod
  def simulate_matches(self, num_matches:int, games_per_match : int) -> MatchResults:
    pass

  """
    Simulate game: runs a single game between two decks and returns the result of the game
      - games_per_match : number of games played on the match
      - deck_a_name : Name of the first deck
      - deck_b_name : Name of the second deck
  """
  @abstractmethod
  def simulate_match(self, games_per_match: int ,deck_a_name : str, deck_b_name : str):
    pass
