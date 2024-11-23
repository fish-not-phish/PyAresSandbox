import os
import pygame

def load_ship_assets(base_path, race, ship_type):
    """
    Load the sprite sheet and frame data for a specific race and ship type.
    """
    race_path = os.path.join(base_path, race)
    sprite_path = os.path.join(race_path, f"{ship_type}.png")
    frame_path = os.path.join(race_path, f"{ship_type}.pn")
    
    # Load sprite sheet and frames
    sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
    frames = parse_pn_file(frame_path)
    
    return sprite_sheet, frames

def load_weapon_assets(base_path, race, weapon_type):
    """
    Load the sprite sheet and frame data for a weapon.
    """
    sprite_path = os.path.join(base_path, race, "weapons", f"{weapon_type}.png")
    frame_path = os.path.join(base_path, race, "weapons", f"{weapon_type}.pn")
    
    # Load sprite sheet and frames
    sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
    frames = parse_pn_file(frame_path)
    
    return sprite_sheet, frames

def parse_pn_file(filename):
    frames = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("*"):  # Check if the line starts with an asterisk
                line = line[1:].strip()  # Remove the asterisk and any leading whitespace
                # Parse the frame data from the line
                frame_data = {}
                line = line.replace("{", "").replace("}", "").strip()
                for part in line.split(","):
                    key, value = part.split(":")
                    frame_data[key.strip()] = int(value.strip())
                frames.append(frame_data)
    return frames

def load_explosion_assets(base_path, explosion_type):
    """
    Load explosion sprite sheet and frame data based on the explosion type.
    """
    sprite_path = os.path.join(base_path, 'explosions', f'{explosion_type}.png')
    frame_path = os.path.join(base_path, 'explosions', f'{explosion_type}.pn')

    # Load sprite sheet and frames
    sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
    frames = parse_pn_file(frame_path)

    return sprite_sheet, frames