from .utils.supportedModels import SupportedModels
from .utils.helper_functions import is_numeric
from .classes.nlp_analyzer import NLP
from .classes.keyword_analyzer import KeywordProcessor
from .classes.card import MTGCard
from typing import List, Dict
import zipfile
import json
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys

class FeatureExtractor:
    def __init__(self, supported_cards_file: str, keywords_list: List[str], effect_references: Dict[str, List[str]], nlp_model: SupportedModels = "sentence-transformers/all-MiniLM-L6-v2", nlp_threshold: float = 0.6, verbose: bool = False, chunkSize: int = 500, excluded_card_types: List[str] = ["Land"]):
        self.verbose = verbose
        self.chunkSize = chunkSize
        # Usar `self` para llamar a los métodos
        self.nlp = self.initialize_nlp(nlp_model, nlp_threshold)
        self.keyword_processor = self.initialize_keywords_processor(keywords_list)
        self.excluded_card_types = excluded_card_types
        self.supported_cards = self.get_supported_cards(supported_cards_file)
        self.effect_references = effect_references


    # Métodos de la clase, asegúrate de usar `self`
    def initialize_nlp(self, nlp_model: SupportedModels, nlp_threshold: float):
        return NLP(model=nlp_model, threshold=nlp_threshold)

    def initialize_keywords_processor(self, keywords_list):
        return KeywordProcessor(keywords_list=keywords_list)

    def process_cards_chunk(self, cards_chunk: List[Dict], thread_num: int) -> List[MTGCard]:
        print(f"Hilo {thread_num} empezando",flush=True)
        sys.stdout.flush()
        parsed_cards = []
        for card_list in cards_chunk:
            card = card_list[0]
            print(f"Hilo {thread_num} procesando {len(parsed_cards)} de {len(cards_chunk)}",flush=True)
            sys.stdout.flush()  
            if card.get("type") in self.excluded_card_types:
                continue
            parsed_card = self.parse_card_data(card)
            if parsed_card:
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

                    cards = list(data['data'].values())[:1500]
                    card_chunks = [cards[i:i + self.chunkSize] for i in range(0, len(cards), self.chunkSize)]

                    print(len(card_chunks))
                    print(len(card_chunks[0]))

                    # Procesar los chunks en paralelo utilizando multiprocessing
                    parsed_cards = set()
                    with ProcessPoolExecutor() as executor:
                        futures = {
                            executor.submit(self.process_cards_chunk, chunk, thread_num): (chunk, thread_num)
                            for thread_num, chunk in enumerate(card_chunks, start=1)
                        }
                        for future in as_completed(futures):
                            result = future.result()
                            print(f"Result first {result[0]}")
                            parsed_cards.update(result)

                    print(len(parsed_cards))
                    # Aquí, aseguramos que solo un proceso escriba en el archivo final
                    with open(output_file, 'w') as json_out:
                        json.dump([card.__dict__ for card in parsed_cards], json_out, indent=4)

        print(f"Cartas guardadas en {output_file}")

    def get_supported_cards(self, supported_cards_file: str)-> set[str]:

        names_set = set()

        with open(supported_cards_file, 'r', encoding='utf-8') as file:
            names_set = {line.strip() for line in file}

        return names_set

    def parse_card_data(self, card: Dict) -> MTGCard:
        """
            Parse a JSON object into card
        """

        power = card.get("power", "0")
        toughness = card.get("toughness", "0")

        if not is_numeric(power) or not is_numeric(toughness):
            return None  

        name = card.get("name", "")
        card_type = card.get("type", "")
        mana_cost = card.get("manaCost", "")
        convertedManaCost = card.get("convertedManaCost", 0)
        power = int(card.get("power", 0)) if card.get("power") else 0
        toughness = int(card.get("toughness", 0)) if card.get("toughness") else 0
        text = card.get("text", "")
        card_keywords = card.get("keywords", [])

        print(name)
        if name not in self.supported_cards:
            print("NOT FOUND")
            return None

        print("FOUND")
        
        # get keywords
        parsed_keywords = self.keyword_processor.extract_keywords(card_keywords=card_keywords, card_text = text)

        # get nlp features
        effects_object  = {}
        for effect in self.effect_references.keys():
            effects_object[effect]= False

        for effect, references in self.effect_references.items():
            
            for ref in references:
                found = self.nlp.text_query(base_text=text, query_text=ref)
                
                if found == True:
                    effects_object[effect]= True
                    break

        # parse mana colors
        # black, blue, red, green, white and colorless
        mana_cost_by_color = {'B': 0, 'U': 0, 'R': 0, 'G': 0, 'W': 0, 'C': 0}  

        # mana is expresed in string form like "{2}{B}{G}" meaning 2 colorless, one black and one green
        mana_pattern = r'\{(\d+)\}|\{(B|U|R|G|W|C)\}'  

        matches = re.findall(mana_pattern, mana_cost)

        for match in matches:
            if match[0]:  # if matches the first part is a number represeting colorless
                mana_cost_by_color['C'] += int(match[0]) 
            elif match[1]:  #if matches a letter
                mana_cost_by_color[match[1]] += 1 

        print(effects_object)

        # create card instance
        mtg_card = MTGCard(
            name=name,
            card_type=card_type,
            mana_cost_by_color=mana_cost_by_color,
            convertedManaCost=convertedManaCost,
            power=power,
            toughness=toughness,
            card_keywords=parsed_keywords,
            card_effects = effects_object
        )

        print(mtg_card)

        return mtg_card