import os
import subprocess
from featureExtractor.classes.card import MTGCard
from collections import Counter
from typing import List

class Simulator:
    def __init__(self, forge_installation_path: str, forge_jar_path: str):
        self.forge_installation_path = forge_installation_path
        self.forge_jar_path = forge_jar_path

    def generate_deck(self, parsed_cards: List[MTGCard]):
        """
        Genera el archivo .dck con las cartas proporcionadas y lo guarda en la ruta
        'forge_installation_path\\decks\\constructed'
        """
        # Calcular tierras y cantidad total de tierras
        lands, num_lands = self.calculate_lands(parsed_cards, len(parsed_cards))

        # Establecer la ruta de guardado para el archivo .dck
        deck_file_path = os.path.join(self.forge_installation_path, 'decks', 'constructed', 'generated_deck.dck')

        # Generar y guardar el archivo .dck
        self.write_deck(parsed_cards, lands, deck_file_path)

        print(f"El archivo .dck se ha generado correctamente: {deck_file_path}")
        return deck_file_path

    def calculate_lands(self, parsed_cards: List[MTGCard], total_cards: int):
        """
        Calcula el número ideal de tierras basándose en las cartas del mazo y su coste de mana.
        """
        num_lands = int(total_cards * 0.4)

        mana_count = Counter()
        for card in parsed_cards:
            for color, count in card.mana_cost_by_color.items():
                mana_count[color] += 1

        # Calcular la proporción de tierras por color
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

    def run_matches(self, num_matches: int, deck_file_path: str):
        """
        Ejecuta el comando para simular partidas usando Forge. Este método toma el número de partidas
        a simular y el path al archivo .dck generado para usarlo en el simulador de Forge.
        """
        # Establecer el comando para ejecutar el simulador de Forge
        command = [
            "java", "-Xmx1024m", "-jar", os.path.join(self.forge_jar_path, "forge-gui-desktop-2.0.03-SNAPSHOT-jar-with-dependencies.jar"),
            "sim", "-d", deck_file_path, "deck2.dck", "-q", "-n", str(num_matches)
        ]

        # Ejecutar el comando y obtener el resultado
        print(f"Ejecutando el simulador de partidas con el comando: {' '.join(command)}")
        subprocess.run(command, check=True)
        print(f"Simulación de {num_matches} partidas completada.")