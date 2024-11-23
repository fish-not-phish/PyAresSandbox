import os
import json

class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.ships = []  # List of ships with their configurations
        self.load_level_data()

    def load_ship_config(self, race, ship_type):
        """
        Load ship configuration from an external JSON file.
        """
        file_path = f"configs/ships/{race}/{ship_type}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                return json.load(file)
        else:
            raise FileNotFoundError(f"Configuration file for {race} {ship_type} not found: {file_path}")

    def load_level_data(self):
        LEVEL_DATA = {
            1: {
                "aud": [
                    {"type": "carrier", "x": 200, "y": 150}, 
                    {"type": "cruiser", "x": 500, "y": 150},
                    {"type": "carrier", "x": 100, "y": 150},
                    {"type": "gunship", "x": 250, "y": 150},
                    {"type": "fighter", "x": 250, "y": 200},
                ],
                "ish": [
                    {"type": "carrier", "x": 400, "y": 300},
                ],
            },
            2: {
                "uns": [
                    {"type": "hvc", "x": 100, "y": 200},
                    {"type": "carrier", "x": 500, "y": 400},
                ],
                "aud": [
                    {"type": "cruiser", "x": 300, "y": 350},
                    {"type": "fighter", "x": 600, "y": 450},
                ],
            },
        }

        # Load the level configuration
        level_config = LEVEL_DATA.get(self.level_number, {})
        for race, ships in level_config.items():
            for ship_entry in ships:
                # Load ship constants from external file
                ship_constants = self.load_ship_config(race, ship_entry["type"])
                # Merge constants with level-specific attributes
                ship_config = {**ship_constants, "x": ship_entry["x"], "y": ship_entry["y"], "race": race}
                self.ships.append(ship_config)
