import json
import random

# File containing MTGCard objects in json
input_file = '/content/parsedCards.json'

def get_random_cards(num_random_cards=2): 

    with open(input_file, 'r') as json_in:
        parsed_cards = json.load(json_in)

    random_cards = random.sample(parsed_cards, num_random_cards)

    # for card in random_cards:
    #     print(json.dumps(card, indent=4))

    return random_cards