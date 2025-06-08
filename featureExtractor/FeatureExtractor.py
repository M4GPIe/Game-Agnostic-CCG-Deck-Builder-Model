from enum import Enum
import os
from typing import List, Dict, Literal
import zipfile
import json
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import sys
from featureExtractor.classes.MTGCard import MTGCard
from featureExtractor.classes.HSCard import HSCard
from featureExtractor.classes.AbstractCard import AbstractCard
from featureExtractor.classes.KeywordProcessor import KeywordProcessor
from featureExtractor.classes.NLPProcessor import NLPProcessor
from featureExtractor.classes.SupportedModels import SupportedModels
from featureExtractor.utils.helper_functions import parse_HS_card_name

class FeatureExtractor:
    def __init__(self, ccg : Literal["MTG","HS"], keywords_list: List[str], effect_references: Dict[str, List[str]], nlp_model: SupportedModels = "sentence-transformers/all-MiniLM-L6-v2", nlp_threshold: float = 0.6, verbose: bool = False, chunkSize: int = 500, excluded_card_types: List[str] = ["Land"], supported_cards_file: str = None):
        self.verbose = verbose
        self.ccg = ccg
        self.chunkSize = chunkSize
        self.nlp = self.initialize_nlp(nlp_model, nlp_threshold)
        self.keyword_processor = self.initialize_keywords_processor(keywords_list)
        self.excluded_card_types = excluded_card_types
        self.supported_cards = self.get_supported_cards(supported_cards_file) if supported_cards_file != None else None
        self.effect_references = effect_references

    def initialize_nlp(self, nlp_model: SupportedModels, nlp_threshold: float):
        return NLPProcessor(model=nlp_model, threshold=nlp_threshold)

    def initialize_keywords_processor(self, keywords_list):
        return KeywordProcessor(keywords_list=keywords_list)

    def process_cards_chunk(self, cards_chunk: List[Dict], thread_num: int) -> List[AbstractCard]:
        print(f"Hilo {thread_num} empezando",flush=True)
        sys.stdout.flush()
        parsed_cards = []
        for index, card_list in enumerate(cards_chunk):
            card = card_list[0] if isinstance(card_list, List) else card_list
            print(f"Hilo {thread_num} procesando {index} de {len(cards_chunk)}",flush=True)
            sys.stdout.flush()
            if card.get("type") in self.excluded_card_types or (self.supported_cards and ((self.ccg == "MTG" and card.get("name") not in self.supported_cards) or (self.ccg=="HS" and parse_HS_card_name(card.get("name")) not in self.supported_cards))):
                continue
            parsed_card = self.parse_card_data(card)
            print(parsed_card)
            if parsed_card is not None or parsed_card is not {}:
                parsed_cards.append(parsed_card)
        print(f"Hilo {thread_num} terminado",flush=True)
        sys.stdout.flush()
        return parsed_cards

    def parse_cards(self, input_zip_file: str, output_file: str = '../outputFiles/newParsedCards.json'):
        with zipfile.ZipFile(input_zip_file, 'r') as zip_ref:
            json_files = [f for f in zip_ref.namelist() if f.endswith('.json')]
            if not json_files:
                print("No se encontró ningún archivo JSON en el zip.")
            else:
                json_file = json_files[0]
                with zip_ref.open(json_file) as f:
                    data = json.load(f)
                    print(len(data))

                    cards = []

                    if self.ccg == "MTG":
                        cards = list(data['data'].values())[:2000]
                    else:
                        cards = list(data)

                    card_chunks = [cards[i:i + self.chunkSize] for i in range(0, len(cards), self.chunkSize)]

                    # Multithread processing
                    parsed_cards = list()
                    with ThreadPoolExecutor() as executor:
                        futures = {
                            executor.submit(self.process_cards_chunk, chunk, thread_num): (chunk, thread_num)
                            for thread_num, chunk in enumerate(card_chunks, start=1)
                        }
                        for future in as_completed(futures):
                            result = future.result()
                            parsed_cards.extend(result)

                    print(len(parsed_cards))

                     # Create file if it doesnt exist
                    output_dir = os.path.dirname(output_file)
                    if output_dir and not os.path.exists(output_dir):
                        os.makedirs(output_dir)

                    with open(output_file, 'w') as json_out:
                        json.dump([card.__dict__ for card in parsed_cards], json_out, indent=4)

        print(f"Cartas guardadas en {output_file}")

    def get_supported_cards(self, supported_cards_file: str)-> set[str]:

        names_set = set()

        with open(supported_cards_file, 'r', encoding='utf-8') as file:
            names_set = {line.strip() for line in file}

        print(names_set)
        return names_set

    def parse_card_data(self, card: Dict) -> AbstractCard:
        """
            Parse a JSON object into card
        """

        if(self.ccg == "MTG"):
            mtg_card = MTGCard(card, self.keyword_processor, self.nlp)
        else:
            mtg_card = HSCard(card, self.keyword_processor, self.nlp)

        return mtg_card