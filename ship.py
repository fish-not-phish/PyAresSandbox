import pygame
import math
from weapon import *
from utils import load_weapon_assets

# Base assets path
BASE_ASSETS_PATH = "assets"

class Ship(pygame.sprite.Sprite):
    def __init__(self, race, x, y, frames, ship_sheet, screen_width, screen_height, config, particles_group, relationship):
        super().__init__()
        self.race = race
        self.relationship = relationship
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.zoom_level = 0.5
        self.frames = frames
        self.ship_sheet = ship_sheet
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.image_idx = 0
        self.size_scale = config.get("size", 1.0)
        self.mass = config.get("mass", 1.0)
        self.particles_group = particles_group

        # Load ship-specific settings
        self.health = config.get("health", 100)
        self.top_speed = config.get("top_speed", 5)
        self.acceleration = config.get("acceleration", 0.1)
        self.rotation_speed = config.get("rotation_speed", 3)
        self.friction = config.get("friction", 0.05)  # Initialize friction

        sound_manager = config.get("sound_manager")
        # Load weapons
        weapon_data = config.get("weapons", {})
        self.primary_weapon = self.load_weapon(weapon_data.get("primary"), sound_manager)
        self.secondary_weapon = self.load_weapon(weapon_data.get("secondary"), sound_manager)
        self.special_weapon = self.load_weapon(weapon_data.get("special"), sound_manager)

        # Store the ship's relationship (friend or foe)
        self.relationship = config.get("relationship", "foe")

        self.update_image()

    def update_image(self):
        # Map the angle to the nearest 15-degree increment for sprite alignment
        normalized_angle = round(self.angle / 15) * 15
        self.image_idx = (normalized_angle // 15) % len(self.frames)

        # Get the current frame data
        frame = self.frames[self.image_idx]
        sprite_rect = pygame.Rect(frame['left'], frame['top'], frame['right'] - frame['left'], frame['bottom'] - frame['top'])
        original_image = self.ship_sheet.subsurface(sprite_rect).copy()  # Copy to prevent repeated transformations

        # Ensure scaling maintains the original aspect ratio
        original_width = sprite_rect.width
        original_height = sprite_rect.height
        scaled_width = int(original_width * self.size_scale)
        scaled_height = int(original_height * self.size_scale)

        # Scale the sprite
        self.image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))

        # Update the rect for positioning
        self.rect = self.image.get_rect(center=(self.position.x, self.position.y))

        self.mask = pygame.mask.from_surface(self.image)


    def rotate_left(self):
        self.angle = (self.angle - self.rotation_speed) % 360
        self.update_image()

    def rotate_right(self):
        self.angle = (self.angle + self.rotation_speed) % 360
        self.update_image()

    def accelerate(self):
        # Calculate the forward direction vector based on the current angle
        direction = pygame.math.Vector2(0, -1).rotate(self.angle)
        self.velocity += direction * self.acceleration

        # Limit the velocity to the top speed
        if self.velocity.length() > self.top_speed:
            self.velocity.scale_to_length(self.top_speed)

    def decelerate(self):
        """Apply friction to reduce velocity."""
        if self.velocity.length() > 0:
            self.velocity -= self.velocity * self.friction
            # Prevent jittering when velocity is very small
            if self.velocity.length() < self.friction:
                self.velocity = pygame.math.Vector2(0, 0)

    def update_position(self, delta_time):
        # Update position based on velocity
        self.position += self.velocity * delta_time
        self.rect.center = self.position

    def zoom_in(self):
        self.zoom_level += 0.1
        self.update_image()

    def zoom_out(self):
        self.zoom_level = max(0.1, self.zoom_level - 0.1)
        self.update_image()

    def draw(self, surface, camera):
        # Draw weapons (attached lasers)
        if self.primary_weapon:
            self.primary_weapon.draw(surface, camera, self)
        if self.secondary_weapon:
            self.secondary_weapon.draw(surface, camera, self)
        if self.special_weapon:
            self.special_weapon.draw(surface, camera, self)
        # Convert world position to screen position
        screen_position = camera.world_to_screen(self.position)

        if camera.zoom_level < 0.3:  # Render as a shape when zoomed out far enough
            size = int(20 * camera.zoom_level * self.size_scale)  # Base size of the triangle
            height = (size * (3 ** 0.5)) / 2  # Height of the equilateral triangle

            # Calculate vertices of the triangle
            top_vertex = (int(screen_position.x), int(screen_position.y - height))
            bottom_left = (int(screen_position.x - size / 2), int(screen_position.y + height / 2))
            bottom_right = (int(screen_position.x + size / 2), int(screen_position.y + height / 2))

            # Draw the triangle
            pygame.draw.polygon(surface, (0, 255, 0), [top_vertex, bottom_left, bottom_right])
        else:
            # Scale the sprite based on the camera's zoom level
            scaled_image = pygame.transform.smoothscale(
                self.image,
                (
                    int(self.rect.width * camera.zoom_level),
                    int(self.rect.height * camera.zoom_level),
                )
            )

            # Create a new rect for the scaled image
            scaled_rect = scaled_image.get_rect(center=(int(screen_position.x), int(screen_position.y)))

            # Blit the scaled image to the surface
            surface.blit(scaled_image, scaled_rect.topleft)


    def load_weapon(self, weapon_config, sound_manager):
        if not weapon_config:
            return None

        weapon_type = weapon_config.get("type")
        alternate_fire = weapon_config.get("alternate_fire", False)

        turret = weapon_config.get("turret", False)  # Retrieve turret flag
        turret_projectiles = weapon_config.get("turret_projectiles", 1)  # Optional: number of projectiles
        turret_spread = weapon_config.get("turret_spread", 15)

        if alternate_fire:
            try:
                sprite_sheet, frames = load_weapon_assets(BASE_ASSETS_PATH, self.race, weapon_type)
                print(f"Loaded weapon '{weapon_type}' with {len(frames)} frames.")
            except FileNotFoundError as e:
                print(f"Error loading weapon assets: {e}")
                return None

            # Define alternate offsets (left and right relative to the ship)
            alternate_offsets = [
                pygame.math.Vector2(-weapon_config.get("alternate_offset", 10), 0),
                pygame.math.Vector2(weapon_config.get("alternate_offset", 10), 0)
            ]

            return Weapon(
                damage=weapon_config.get("damage", 10),
                fire_rate=weapon_config.get("fire_rate", 0.5),
                projectile_type=weapon_type,
                sprite_sheet=sprite_sheet,
                pn_file=frames,
                speed=weapon_config.get("speed", 10),
                lifetime=weapon_config.get("lifetime", 2),
                size=weapon_config.get("size", 1.0),
                mass=weapon_config.get("mass", 0.0),
                sound_manager=sound_manager,
                fire_sound=weapon_config.get("fire_sound"),
                hit_sound=weapon_config.get("hit_sound"),
                explosion_type=weapon_config.get("explosion_type", "weapon_hit"),
                laser_color=tuple(weapon_config.get("laser_color", (255, 0, 0))),
                laser_length=weapon_config.get("laser_length", 100),
                laser_width=weapon_config.get("laser_width", 5),
                alternate_fire=True,                  # Enable alternation
                alternate_offsets=alternate_offsets,    # Provide offset vectors
                turret=turret,                         # Pass turret flag
                turret_projectiles=turret_projectiles, # Pass turret projectile count
                turret_spread=turret_spread
            )

        elif weapon_type == "laser":
            return Weapon(
                damage=weapon_config.get("damage", 10),
                fire_rate=weapon_config.get("fire_rate", 0.5),
                projectile_type=weapon_type,
                speed=weapon_config.get("speed", 10),
                lifetime=weapon_config.get("lifetime", 2),
                size=weapon_config.get("size", 1.0),
                sound_manager=sound_manager,
                fire_sound=weapon_config.get("fire_sound"),
                hit_sound=weapon_config.get("hit_sound"),
                explosion_type=weapon_config.get("explosion_type", "weapon_hit"),
                laser_color=weapon_config.get("laser_color", (255, 0, 0)),
                laser_length=weapon_config.get("laser_length", 100),
                laser_width=weapon_config.get("laser_width", 5),
                alternate_fire=False,                   # Disable alternation
                turret=turret,                         # Pass turret flag
                turret_projectiles=turret_projectiles, # Pass turret projectile count
                turret_spread=turret_spread
            )
        
        elif weapon_type == "tspace":
            return TSpaceWeapon(
                particles_group=self.particles_group,
                damage=weapon_config.get("damage", 30),
                fire_rate=weapon_config.get("fire_rate", 0.1),
                projectile_type=weapon_type,
                speed=weapon_config.get("speed", 10),
                lifetime=weapon_config.get("lifetime", 2),
                size=weapon_config.get("size", 1.0),
                mass=weapon_config.get("mass", 0.0),
                sound_manager=sound_manager,
                fire_sound=weapon_config.get("fire_sound"),
                hit_sound=weapon_config.get("hit_sound"),
                explosion_type=weapon_config.get("explosion_type", "weapon_hit"),
                laser_color=tuple(weapon_config.get("laser_color", (165, 78, 186))),
                laser_length=weapon_config.get("laser_length", 100),
                laser_width=weapon_config.get("laser_width", 3),
                alternate_fire=False,                   # Disable alternation
                turret=turret,                         # Enable turret
                turret_projectiles=turret_projectiles, # Pass turret projectile count
                turret_spread=turret_spread
            )
        
        elif weapon_type == "trazer":
            return TrazerWeapon(
                particles_group=self.particles_group,
                damage=weapon_config.get("damage", 10),
                fire_rate=weapon_config.get("fire_rate", 0.5),
                projectile_type=weapon_type,
                speed=weapon_config.get("speed", 10),
                lifetime=weapon_config.get("lifetime", 2),
                size=weapon_config.get("size", 1.0),
                mass=weapon_config.get("mass", 0.0),
                sound_manager=sound_manager,
                fire_sound=weapon_config.get("fire_sound"),
                hit_sound=weapon_config.get("hit_sound"),
                explosion_type=weapon_config.get("explosion_type", "weapon_hit"),
                laser_color=weapon_config.get("laser_color", (255, 0, 0)),
                laser_length=weapon_config.get("laser_length", 100),
                laser_width=weapon_config.get("laser_width", 5),
                alternate_fire=False,                   # Assuming 'trazer' doesn't alternate
                turret=turret,                         # Pass turret flag
                turret_projectiles=turret_projectiles, # Pass turret projectile count
                turret_spread=turret_spread
            )
        
        else:
            # For other weapon types, load assets normally
            try:
                sprite_sheet, frames = load_weapon_assets(BASE_ASSETS_PATH, self.race, weapon_type)
                print(f"Loaded weapon '{weapon_type}' with {len(frames)} frames.")
            except FileNotFoundError as e:
                print(f"Error loading weapon assets: {e}")
                return None
            
            turret = weapon_config.get("turret", False)
            turret_projectiles = weapon_config.get("turret_projectiles", 1)
            turret_spread = weapon_config.get("turret_spread", 15)

            return Weapon(
                damage=weapon_config.get("damage", 10),
                fire_rate=weapon_config.get("fire_rate", 0.5),
                projectile_type=weapon_type,
                sprite_sheet=sprite_sheet,
                pn_file=frames,
                speed=weapon_config.get("speed", 10),
                lifetime=weapon_config.get("lifetime", 2),
                size=weapon_config.get("size", 1.0),
                mass=weapon_config.get("mass", 0.0),
                sound_manager=sound_manager,
                fire_sound=weapon_config.get("fire_sound"),
                hit_sound=weapon_config.get("hit_sound"),
                explosion_type=weapon_config.get("explosion_type", "weapon_hit"),
                alternate_fire=False,                   # Default to no alternation
                turret=turret,                         # Pass turret flag
                turret_projectiles=turret_projectiles, # Pass turret projectile count
                turret_spread=turret_spread
            )

    def fire_weapon(self, weapon_type, projectiles, target_angle=None, ships=None):
        if weapon_type == "primary" and self.primary_weapon:
            if isinstance(self.primary_weapon, TrazerWeapon):
                self.primary_weapon.fire(
                    self.position, 
                    self.angle, 
                    projectiles, 
                    self.velocity, 
                    self.race, 
                    self.relationship,  # Pass the relationship
                    ships
                )
            else:
                firing_angle = target_angle if target_angle is not None else self.angle
                spawn_position = self.position + pygame.math.Vector2(0, -10).rotate(firing_angle)
                self.primary_weapon.fire(
                    spawn_position, 
                    firing_angle, 
                    projectiles, 
                    self.velocity, 
                    self.race, 
                    self.relationship,  # Pass the relationship
                    ships
                )
        elif weapon_type == "secondary" and self.secondary_weapon:
            firing_angle = target_angle if target_angle is not None else self.angle
            spawn_position = self.position + pygame.math.Vector2(0, -10).rotate(firing_angle)
            self.secondary_weapon.fire(
                spawn_position, 
                firing_angle, 
                projectiles, 
                self.velocity, 
                self.race, 
                self.relationship,  # Pass the relationship
                ships
            )
        elif weapon_type == "special" and self.special_weapon:
            firing_angle = target_angle if target_angle is not None else self.angle
            spawn_position = self.position + pygame.math.Vector2(0, -10).rotate(firing_angle)
            self.special_weapon.fire(
                spawn_position, 
                firing_angle, 
                projectiles, 
                self.velocity, 
                self.race, 
                self.relationship,  # Pass the relationship
                ships
            )

    def update_weapons(self, delta_time, ships, projectiles):
        """Update the cooldowns and states for all weapons."""
        if self.primary_weapon:
            self.primary_weapon.update_cooldown(delta_time)
            self.primary_weapon.update(delta_time, self, ships, projectiles)
        if self.secondary_weapon:
            self.secondary_weapon.update_cooldown(delta_time)
            self.secondary_weapon.update(delta_time, self, ships, projectiles)
        if self.special_weapon:
            self.special_weapon.update_cooldown(delta_time)
            self.special_weapon.update(delta_time, self, ships, projectiles)
