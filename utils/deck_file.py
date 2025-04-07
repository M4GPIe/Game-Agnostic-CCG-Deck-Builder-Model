import json
from collections import Counter
from typing import List
from featureExtractor.classes.card import MTGCard

# Calculate ideal number of lands for a deck given the cards
def calculate_lands(parsed_cards: List[MTGCard], total_cards):
    
    num_lands = int(total_cards * 0.4)

    mana_count = Counter()
    for card in parsed_cards:
        for color, count in card.mana_cost_by_color.items():
            mana_count[color] += 1

    # Calcular la proporción de tierras de cada color
    total_mana_cost = sum(mana_count.values())
    lands = {}
    for color, count in mana_count.items():
        lands[color] = int((count / total_mana_cost) * num_lands)

    #print(lands, num_lands)

    return lands, num_lands

# generates the deck, including lands, and writes the file
def write_deck(parsed_cards: List[MTGCard], lands, output_file):

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
            if color=='B':
              f.write(f"{land_count} Swamp\n")
            elif color=='U':
              f.write(f"{land_count} Island\n")
            elif color=='R':
              f.write(f"{land_count} Mountain\n")
            elif color=='G':
              f.write(f"{land_count} Forest\n")
            elif color=='W':
              f.write(f"{land_count} Plains\n")
            else:
              f.write(f"{land_count} Wastes\n")

def generate_deck(parsed_cards: List[MTGCard]):
        
    # calculate lands
    lands, num_lands = calculate_lands(parsed_cards, len(parsed_cards))

    # Generar el archivo .dck
    output_file = 'output_deck.dck'
    write_deck(parsed_cards, lands, output_file)

    print(f"El archivo .dck se ha generado correctamente: {output_file}")